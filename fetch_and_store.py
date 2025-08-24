import requests
import sqlite3
import csv
from datetime import datetime, timezone
from io import StringIO

DB_FILE = 'real_time_data.db'
TABLE_NAME = 'water_data'
BASE_URL = 'https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline'
STATIONS = ['05OJ005', '05OJ021', '05OJ024']
PARAMETERS = ['3', '6', '46', '47']


def get_latest_datetime_from_db(conn):
    cur = conn.cursor()
    cur.execute(f"""
        SELECT MAX(Date) FROM {TABLE_NAME}
    """)
    row = cur.fetchone()
    return row[0] if row and row[0] else None


def create_table_if_not_exists(conn):
    cur = conn.cursor()
    # Drop the old table if it exists (for schema migration)
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
    # Normalize fieldnames to strip whitespace and BOM
    def normalize_fieldname(f):
        return f.replace('\ufeff', '').strip()
    reader.fieldnames = [normalize_fieldname(f) for f in reader.fieldnames]
    print('Detected CSV fieldnames:', reader.fieldnames)
    cur = conn.cursor()
    rows = []
    for row in reader:
        # Also normalize keys in each row
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


def main():
    conn = sqlite3.connect(DB_FILE)
    create_table_if_not_exists(conn)
    latest_dt = get_latest_datetime_from_db(conn)
    now_utc = datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S')
    if latest_dt:
        start_date = latest_dt
    else:
        start_date = '2020-08-24 00:00:00'
    url = build_url(start_date, now_utc)
    print(f"Fetching data from: {url}")
    csv_text = fetch_csv(url)
    parse_and_insert_csv(conn, csv_text)
    print("Data updated.")
    conn.close()

if __name__ == '__main__':
    main()
