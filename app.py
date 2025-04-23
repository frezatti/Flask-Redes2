from flask import Flask, request, jsonify
import sqlite3
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes to communicate with Streamlit frontend

# Database configuration
DB_FOLDER = 'db'
DB_PATH = os.path.join(DB_FOLDER, 'network_devices.db')

# Ensure the db folder exists
def ensure_db_folder():
    if not os.path.exists(DB_FOLDER):
        os.makedirs(DB_FOLDER)
        print(f"Created database directory: {DB_FOLDER}")

# Initialize the database
def init_db():
    ensure_db_folder()
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        # Create devices table if it doesn't exist
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS devices (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT NOT NULL UNIQUE,
            name TEXT NOT NULL,
            traffic_rate REAL NOT NULL
        )
        ''')
        conn.commit()
        print("Database initialized successfully.")

# API endpoint to get all devices
@app.route('/api/devices', methods=['GET'])
def get_devices():
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM devices')
            devices = [dict(row) for row in cursor.fetchall()]
            
            # Add status based on traffic rate
            for device in devices:
                device['status'] = "Alto" if device['traffic_rate'] >= 50 else "Normal"
                
            return jsonify({"devices": devices}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint to add a new device
@app.route('/api/devices', methods=['POST'])
def add_device():
    try:
        data = request.json
        ip = data.get('ip')
        name = data.get('name')
        traffic_rate = data.get('traffic_rate')
        
        # Validate input
        if not all([ip, name, traffic_rate is not None]):
            return jsonify({"error": "Missing required fields"}), 400
        
        # Validate IP format (basic check)
        ip_parts = ip.split('.')
        if len(ip_parts) != 4 or not all(part.isdigit() and 0 <= int(part) <= 255 for part in ip_parts):
            return jsonify({"error": "Invalid IP address format"}), 400
        
        # Validate traffic rate
        try:
            traffic_rate = float(traffic_rate)
            if traffic_rate < 0:
                return jsonify({"error": "Traffic rate must be a positive number"}), 400
        except ValueError:
            return jsonify({"error": "Traffic rate must be a number"}), 400
        
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            cursor.execute(
                'INSERT INTO devices (ip, name, traffic_rate) VALUES (?, ?, ?)',
                (ip, name, traffic_rate)
            )
            conn.commit()
            
            # Return the newly created device with its ID
            device_id = cursor.lastrowid
            status = "Alto" if traffic_rate >= 50 else "Normal"
            
            return jsonify({
                "message": "Device added successfully",
                "device": {
                    "id": device_id,
                    "ip": ip,
                    "name": name,
                    "traffic_rate": traffic_rate,
                    "status": status
                }
            }), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Device with this IP already exists"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# API endpoint to delete a device
@app.route('/api/devices/<int:device_id>', methods=['DELETE'])
def delete_device(device_id):
    try:
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()
            # Check if device exists
            cursor.execute('SELECT id FROM devices WHERE id = ?', (device_id,))
            if not cursor.fetchone():
                return jsonify({"error": "Device not found"}), 404
                
            cursor.execute('DELETE FROM devices WHERE id = ?', (device_id,))
            conn.commit()
            
            return jsonify({"message": f"Device with ID {device_id} deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Initialize the database when the app starts
with app.app_context():
    # Create the database if it doesn't exist
    ensure_db_folder()
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        print(f"Using existing database at {DB_PATH}")

if __name__ == '__main__':
    # Run the Flask app
    app.run(host='0.0.0.0', port=5000, debug=True)
