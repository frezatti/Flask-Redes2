# Network Traffic Monitoring System

This application simulates network traffic monitoring for a small infrastructure, using Streamlit as the frontend and Flask as the backend API with SQLite database storage.

## Features

- Register network devices with IP address, name, and traffic rate
- Visualize all registered devices with their traffic status ("Normal" or "Alto")
- Delete devices from the monitoring system
- Interactive dashboard with traffic statistics

## Project Structure

```
network-monitor/
├── app.py                  # Flask backend API
├── streamlit_app.py        # Streamlit frontend
├── /db/devices.db          # SQLite database (created automatically)
├── Dockerfile              # Docker configuration
├── docker-compose.yml      # Docker Compose configuration
└── requirements.txt        # Python dependencies
```

## Requirements

- Python 3.8+
- Flask
- Streamlit
- SQLite
- Docker (optional)

## Running the Application Locally

### 1. Setup a Virtual Environment (Recommended)

```bash
# Create a virtual environment
python -m venv venv

# Activate the virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Run the Flask Backend

```bash
# Method 1: Direct Python execution
python app.py

# Method 2: Using Flask CLI
# On Windows CMD:
set FLASK_APP=app.py
flask run --debug

# On Windows PowerShell:
$env:FLASK_APP = "app.py"
flask run --debug

# On macOS/Linux:
export FLASK_APP=app.py
flask run --debug
```

This will start the Flask backend server on http://localhost:5000

### 4. Run the Streamlit Frontend

In a new terminal window:

```bash
streamlit run streamlit_app.py
```

This will start the Streamlit frontend on http://localhost:8501

## Running with Docker

### Using Docker Compose (Recommended)

```bash
docker-compose up --build
```

This will start both services:

- Flask backend: http://localhost:5000
- Streamlit frontend: http://localhost:8501

### Using Docker Directly

```bash
docker build -t network-monitor .
docker run -p 5000:5000 -p 8501:8501 network-monitor
```

## API Endpoints

- `GET /api/devices` - List all devices
- `POST /api/devices` - Add a new device
- `DELETE /api/devices/{id}` - Delete a device by ID

## Database Schema

The SQLite database contains a single `devices` table with the following schema:

```sql
CREATE TABLE devices (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ip TEXT NOT NULL UNIQUE,
    name TEXT NOT NULL,
    traffic_rate REAL NOT NULL
);
```

## Traffic Status Rules

- Normal: Traffic rate < 50 Mbps
- Alto (High): Traffic rate ≥ 50 Mbps
