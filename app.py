from flask import Flask, jsonify, request, send_from_directory, render_template
import sqlite3
import threading
import logging

import os
app = Flask(__name__, static_folder='.', static_url_path='')
logging.basicConfig(level=logging.INFO)

# --- Data update logic (from fetch_and_store.py, simplified for import) ---
import csv
from datetime import datetime, timezone
from io import StringIO
import requests

def update_data():
    DB_FILE = 'data/real_time_data.db'
    TABLE_NAME = 'water_data'
    BASE_URL = 'https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline'
    STATIONS = ['05OJ005', '05OJ021', '05OJ024']
    PARAMETERS = ['3', '6', '46', '47']
    def get_latest_datetime_from_db(conn):
        cur = conn.cursor()
        cur.execute(f"SELECT MAX(Date) FROM {TABLE_NAME}")
        row = cur.fetchone()
        return row[0] if row and row[0] else None
    def create_table_if_not_exists(conn):
        cur = conn.cursor()
        cur.execute(f"DROP TABLE IF EXISTS {TABLE_NAME}")
        cur.execute(f"""
            CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
                ID TEXT,
                Date TEXT,
                Parameter TEXT,
                Value TEXT,
                PRIMARY KEY (ID, Date, Parameter)
            )
        """)
        conn.commit()
    def build_url(start_date, end_date):
        params = []
        for s in STATIONS:
            params.append(f"stations[]={s}")
        for p in PARAMETERS:
            params.append(f"parameters[]={p}")
        params.append(f"start_date={start_date}")
        params.append(f"end_date={end_date}")
        return f"{BASE_URL}?{'&'.join(params)}"
    def fetch_csv(url):
        resp = requests.get(url)
        resp.raise_for_status()
        return resp.text
    def parse_and_insert_csv(conn, csv_text):
        reader = csv.DictReader(StringIO(csv_text))
        def normalize_fieldname(f):
            return f.replace('\ufeff', '').strip()
        reader.fieldnames = [normalize_fieldname(f) for f in reader.fieldnames]
        cur = conn.cursor()
        rows = []
        for row in reader:
            row = {normalize_fieldname(k): v for k, v in row.items()}
            rows.append((
                row['ID'],
                row['Date'],
                row['Parameter/Paramètre'],
                row['Value/Valeur']
            ))
        cur.executemany(f"""
            INSERT OR IGNORE INTO {TABLE_NAME} (ID, Date, Parameter, Value)
            VALUES (?, ?, ?, ?)
        """, rows)
        conn.commit()
    conn = sqlite3.connect(DB_FILE)
    create_table_if_not_exists(conn)
    latest_dt = get_latest_datetime_from_db(conn)
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    if latest_dt:
        start_date = latest_dt
    else:
        start_date = '2020-08-24 00:00:00'
    url = build_url(start_date, now_utc)
    csv_text = fetch_csv(url)
    parse_and_insert_csv(conn, csv_text)
    conn.close()

from flask import g

def get_update_status():
    if not hasattr(app, 'update_status'):
        app.update_status = {'status': 'idle', 'message': ''}
    return app.update_status


@app.route('/api/update', methods=['POST'])
def api_update():
    status = get_update_status()
    def run_update():
        try:
            logging.info('Starting data update...')
            status['status'] = 'updating'
            status['message'] = 'Updating data from remote source...'
            update_data()
            status['status'] = 'success'
            status['message'] = 'Update complete.'
            logging.info('Data update complete.')
        except Exception as e:
            status['status'] = 'error'
            status['message'] = f'Update failed: {e}'
            logging.error(f'Update error: {e}')
    thread = threading.Thread(target=run_update)
    thread.start()
    return {'status': 'updating', 'message': 'Update started.'}, 202

@app.route('/api/update_status')
def api_update_status():
    return get_update_status()
DB_FILE = 'data/real_time_data.db'

def get_data(station=None, parameter=None):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    query = "SELECT ID, Date, Parameter, Value FROM water_data"
    params = []
    conditions = []
    if station:
        conditions.append("ID = ?")
        params.append(station)
    if parameter:
        conditions.append("Parameter = ?")
        params.append(parameter)
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
    query += " ORDER BY Date ASC"
    cur.execute(query, params)
    rows = cur.fetchall()
    conn.close()
    return [
        {"ID": r[0], "Date": r[1], "Parameter": r[2], "Value": r[3]} for r in rows
    ]

@app.route('/api/data')
def api_data():
    station = request.args.get('station')
    parameter = request.args.get('parameter')
    data = get_data(station, parameter)
    return jsonify(data)


def get_min_max_dates():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT MIN(Date), MAX(Date) FROM water_data")
    result = cur.fetchone()
    conn.close()
    return result if result else (None, None)

from datetime import timedelta

def get_recent_water_levels():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    seven_days_ago = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S')
    cur.execute(
        """
        SELECT ID, Date, Parameter, Value
        FROM water_data
        WHERE Parameter IN ('3', '6', '46', '47') AND Date >= ?
        ORDER BY Date ASC
        """,
        (seven_days_ago,)
    )
    rows = cur.fetchall()
    conn.close()
    return rows

@app.route('/')
def root():
    min_date, max_date = get_min_max_dates()
    recent_water_levels = get_recent_water_levels()
    return render_template('index.html', min_date=min_date, max_date=max_date, recent_water_levels=recent_water_levels)

if __name__ == '__main__':
    app.run(debug=False, host='0.0.0.0', port=80)
