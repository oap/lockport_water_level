# Water Level Dashboard - Lockport Area

A Flask-based web dashboard for monitoring water levels at multiple monitoring stations near Lockport, Manitoba. The application fetches real-time data from Environment and Climate Change Canada's Water Office and displays interactive charts showing both unit values (5-minute intervals) and daily mean water levels.

## 🌊 Features

- **Multi-Station Monitoring**: Displays data for 3 water monitoring stations (05OJ005, 05OJ021, 05OJ024)
- **Real-Time Data**: Fetches current water level data from Environment Canada's Water Office API
- **Interactive Charts**: Uses Chart.js to display time-series data with proper chronological ordering
- **Dual Data Types**: Shows both high-frequency unit values (5-min intervals) and daily mean values
- **Automatic Updates**: Background data fetching with manual update capability
- **Responsive Design**: Clean, mobile-friendly interface

## 📊 Data Visualization

- **Green Line**: Unit values (5-minute interval readings)
- **Blue Points**: Daily mean values (positioned at noon for clarity)
- **Time-based X-axis**: Proper chronological ordering with local time display
- **Last 7 Days**: Displays recent data for trend analysis

## 🗂️ Project Structure

```
lockport/
├── app.py                 # Main Flask application
├── fetch_and_store.py     # Data fetching and storage utilities
├── requirements.txt       # Python dependencies
├── Dockerfile            # Docker container configuration
├── docker-compose.yml    # Docker Compose setup
├── .dockerignore         # Docker build exclusions
├── deploy.sh             # Automated deployment script
├── data/                 # Database storage directory
│   └── real_time_data.db # SQLite database (created automatically)
├── templates/
│   ├── index.html        # Main dashboard template
│   ├── plot.html         # Chart-specific template
│   └── table.html        # Table view template
└── venv/                 # Virtual environment (for local development)
```

## 🚀 Quick Start

### Prerequisites

- **For Docker deployment (Recommended)**: Docker and Docker Compose
- **For local development**: Python 3.8 or higher
- Internet connection (for fetching water level data)

### Option 1: Docker Deployment (Recommended)

The easiest way to run the application is using Docker:

1. **Clone or download the project**
   ```bash
   cd /path/to/your/projects
   # Copy the project files to your desired location
   ```

2. **Run the deployment script**
   ```bash
   chmod +x deploy.sh
   ./deploy.sh
   ```

3. **Access the dashboard**
   Open your web browser and go to: `http://localhost`

### Option 2: Manual Docker Setup

If you prefer manual control:

1. **Build and run with Docker Compose**
   ```bash
   docker-compose up --build -d
   ```

2. **Access the dashboard**
   Open your web browser and go to: `http://localhost`

### Option 3: Local Development Setup

### Option 3: Local Development Setup

1. **Clone or download the project**
   ```bash
   cd /path/to/your/projects
   # Copy the project files to your desired location
   ```

2. **Create a virtual environment**
   ```bash
   python3 -m venv venv
   ```

3. **Activate the virtual environment**
   ```bash
   # On macOS/Linux:
   source venv/bin/activate
   
   # On Windows:
   venv\Scripts\activate
   ```

4. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Access the dashboard**
   Open your web browser and go to: `http://localhost:80`

## 🐳 Docker Management

### Common Docker Commands

```bash
# View logs
docker-compose logs -f

# Stop the application
docker-compose down

# Restart the application
docker-compose restart

# Rebuild and restart
docker-compose up --build -d

# Check container status
docker-compose ps
```

### Data Persistence

The Docker setup includes a volume mount for the `data/` directory, ensuring that:
- Database files persist between container restarts
- Historical data is preserved during updates
- Backup and restore operations are simplified

## 📡 Data Sources

The application fetches data from **Environment and Climate Change Canada's Water Office**:
- **API Endpoint**: `https://wateroffice.ec.gc.ca/services/real_time_data/csv/inline`
- **Stations Monitored**:
  - `05OJ005`: Water monitoring station at Selkirk Manitoba
  - `05OJ021`: Water level monitoring station at Upstream Lockport Dam
  - `05OJ024`: Water level monitoring station at Upstream Lockport Dam
- **Parameters**:
  - `Parameter 3`: Daily mean water levels
  - `Parameter 46`: Unit values (5-minute intervals)

## 🎛️ Usage

### Main Dashboard
- View real-time water level charts for all stations
- Charts automatically display the last 7 days of data
- Each station has its own dedicated chart section

### Manual Data Update
- Click "Update Data" to fetch the latest information
- Updates run in the background without interrupting the interface
- Status messages indicate update progress

### Chart Interaction
- Hover over data points for detailed values
- Green lines show continuous 5-minute readings
- Blue points represent daily averages
- X-axis displays local time in MM/dd HH:mm format

## 🔧 Technical Details

### Backend
- **Framework**: Flask 3.1.2
- **Database**: SQLite (for local data storage)
- **Data Fetching**: Python requests library
- **Background Processing**: Threading for non-blocking updates

### Frontend
- **Charts**: Chart.js with date-fns adapter
- **Styling**: Clean HTML/CSS
- **Time Handling**: UTC to local time conversion
- **Responsive**: Mobile-friendly design

### Database Schema
```sql
CREATE TABLE water_data (
    ID TEXT,           -- Station identifier
    Date TEXT,         -- Timestamp (ISO format)
    Parameter TEXT,    -- Data type (3=daily mean, 46=unit values)
    Value TEXT,        -- Water level measurement
    PRIMARY KEY (ID, Date, Parameter)
);
```

## 🛠️ Configuration

### Monitored Stations
To modify which stations are monitored, edit the `STATIONS` list in `app.py`:
```python
STATIONS = ['05OJ005', '05OJ021', '05OJ024']
```

### Data Parameters
To change which data types are fetched, modify the `PARAMETERS` list:
```python
PARAMETERS = ['3', '6', '46', '47']  # 3=daily mean, 46=unit values
```

### Server Settings
**Docker Deployment**: Runs on port 80 (standard HTTP port)
**Local Development**: To run on a different port, modify the last line in `app.py`:
```python
app.run(debug=False, host='0.0.0.0', port=80)
```

## 🔍 API Endpoints

- `GET /` - Main dashboard
- `POST /api/update` - Trigger data update
- `GET /api/update_status` - Check update status
- `GET /api/data` - Raw data API (with optional station/parameter filters)

## 🐛 Troubleshooting

### Common Issues

1. **Port 8001 already in use**
   ```bash
   # Kill existing processes
   pkill -f "python.*app.py"
   # Or change port in app.py
   ```

2. **No charts displayed**
   - Check browser console for JavaScript errors
   - Ensure Chart.js libraries are loading
   - Verify data is being fetched (check network tab)

3. **Database errors**
   - Delete `real_time_data.db` to reset database
   - App will recreate it on next run

4. **Network connection issues**
   - Verify internet connection
   - Check if Environment Canada's API is accessible
   - Try manual data update

### Logs
The application logs important events to the console. Look for:
- Data update start/completion messages
- HTTP request logs
- Error messages for debugging

## 📚 Dependencies

See `requirements.txt` for complete list. Key dependencies:
- **Flask**: Web framework
- **requests**: HTTP client for API calls
- **Chart.js**: Frontend charting (loaded via CDN)

## 🤝 Contributing

1. Fork or copy the project
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request or share your improvements

## 📄 License

This project is open source. Feel free to use, modify, and distribute as needed.

## 🔗 Related Resources

- [Environment Canada Water Office](https://wateroffice.ec.gc.ca/)
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Chart.js Documentation](https://www.chartjs.org/docs/)

---

**Note**: This dashboard is for informational purposes. For official water level data and flood warnings, always consult Environment and Climate Change Canada's official sources.
