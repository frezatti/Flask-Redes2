import streamlit as st
import requests
import pandas as pd
import time
import re

# Configuration
FLASK_API_URL = "http://localhost:5000/api"  # Flask backend URL

# Page configuration
st.set_page_config(
    page_title="Network Traffic Monitor",
    page_icon="🌐",
    layout="wide",
)

# Add custom styling
st.markdown("""
<style>
    .main {
        padding: 2rem;
    }
    .status-normal {
        background-color: #D1FFD1;
        padding: 5px 10px;
        border-radius: 5px;
        color: #007500;
        font-weight: bold;
    }
    .status-high {
        background-color: #FFD1D1;
        padding: 5px 10px;
        border-radius: 5px;
        color: #C00000;
        font-weight: bold;
    }
    .header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1.5rem;
        color: #1E3A8A;
    }
    .subheader {
        font-size: 1.5rem;
        margin-bottom: 1rem;
        color: #1E3A8A;
    }
    .stButton button {
        width: 100%;
    }
    .delete-btn {
        background-color: #FF5252;
        color: white;
        border: none;
        border-radius: 5px;
        padding: 5px 10px;
        font-size: 14px;
        cursor: pointer;
    }
    .chart-container {
        display: flex;
        justify-content: center;
        margin-top: 2rem;
        margin-bottom: 2rem;
    }
    .chart {
        width: 100%;
        min-height: 300px;
    }
</style>
""", unsafe_allow_html=True)

# Add header
st.markdown('<p class="header">🌐 Network Traffic Monitoring System</p>', unsafe_allow_html=True)

# Function to validate IP address
def is_valid_ip(ip):
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    if not re.match(pattern, ip):
        return False
    octets = ip.split('.')
    for octet in octets:
        if int(octet) > 255:
            return False
    return True

# Helper function for traffic status
def get_status(traffic):
    if traffic < 5:
        return "Very Low"
    elif traffic < 10:
        return "Low"
    elif traffic < 50:
        return "Normal"
    else:
        return "High"

# Function to fetch all devices
def get_devices():
    try:
        response = requests.get(f"{FLASK_API_URL}/devices")
        if response.status_code == 200:
            return response.json().get("devices", [])
        else:
            st.error(f"Error fetching devices: {response.json().get('error', 'Unknown error')}")
            return []
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend server. Make sure the Flask API is running.")
        return []
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return []

# Function to add a device
def add_device(ip, name, traffic_rate):
    try:
        response = requests.post(
            f"{FLASK_API_URL}/devices",
            json={"ip": ip, "name": name, "traffic_rate": float(traffic_rate)}
        )
        
        if response.status_code == 201:
            st.success(f"Device {name} ({ip}) added successfully!")
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"Error adding device: {error_msg}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend server. Make sure the Flask API is running.")
        return False
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

def delete_device(device_id):
    try:
        response = requests.delete(f"{FLASK_API_URL}/devices/{device_id}")
        
        if response.status_code == 200:
            st.success("Device deleted successfully!")
            return True
        else:
            error_msg = response.json().get('error', 'Unknown error')
            st.error(f"Error deleting device: {error_msg}")
            return False
    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend server. Make sure the Flask API is running.")
        return False
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")
        return False

# Create tabs for different sections
tab1, tab2 = st.tabs(["📊 Dashboard", "➕ Add Device"])

# Tab 1: Dashboard
with tab1:
    st.markdown('<p class="subheader">Network Devices Status</p>', unsafe_allow_html=True)
    
    # Get devices data
    devices = get_devices()
    
    if not devices:
        st.info("No devices found. Add some devices to start monitoring.")
    else:
        # Create a DataFrame for better display
        df = pd.DataFrame(devices)
        
        # Calculate some statistics
        avg_traffic = df['traffic_rate'].mean() if len(df) > 0 else 0
        high_traffic_count = len(df[df['traffic_rate'] >= 50]) if len(df) > 0 else 0
        
        # Display metrics
        metric_col1, metric_col2, metric_col3 = st.columns(3)
        metric_col1.metric("Total Devices", len(devices))
        metric_col2.metric("Average Traffic (Mbps)", f"{avg_traffic:.2f}")
        metric_col3.metric("High Traffic Devices", high_traffic_count)
        
        # Display devices in a custom table with delete buttons
        st.markdown("### Device List")
        
        # Create a table with delete buttons for each row
        for i, device in enumerate(devices):
            key_prefix = f"device_{device['id']}"
            with st.container():
                cols = st.columns([1, 2, 2, 2, 1, 1])
                cols[0].write(f"**ID:** {device['id']}")
                cols[1].write(f"**IP:** {device['ip']}")
                cols[2].write(f"**Name:** {device['name']}")
                traffic = device['traffic_rate']
                # Status display
                if traffic < 5:
                    cols[3].markdown(f"<div class='status-high'>🟣 VERY LOW ({traffic:.1f} Mbps)</div>", unsafe_allow_html=True)
                elif traffic < 10:
                    cols[3].markdown(f"<div class='status-high'>🔵 LOW ({traffic:.1f} Mbps)</div>", unsafe_allow_html=True)
                elif traffic < 50:
                    cols[3].markdown(f"<div class='status-normal'>🟢 NORMAL ({traffic:.1f} Mbps)</div>", unsafe_allow_html=True)
                else:
                    cols[3].markdown(f"<div class='status-high'>🔴 HIGH ({traffic:.1f} Mbps)</div>", unsafe_allow_html=True)
                # Delete button
                if cols[5].button("Delete", key=f"{key_prefix}_delete"):
                    if delete_device(device['id']):
                        time.sleep(0.5)
                        st.experimental_rerun()
            if i < len(devices) - 1:
                st.markdown("---")
        
        # Traffic visualizations in a more prominent layout
        st.markdown("<h3 style='text-align: center; margin-top: 2rem;'>Network Traffic Analytics</h3>", unsafe_allow_html=True)
        chart_col1, chart_col2 = st.columns(2)
        
        with chart_col1:
            st.markdown("<h4 style='text-align: center;'>Traffic Status Distribution</h4>", unsafe_allow_html=True)
            # Add status column and count
            df['status'] = df['traffic_rate'].apply(get_status)
            status_order = ["Very Low", "Low", "Normal", "High"]
            status_counts = df['status'].value_counts().reindex(status_order, fill_value=0)
            fig_data = pd.DataFrame({'Status': status_counts.index, 'Count': status_counts.values})
            with st.container():
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.bar_chart(fig_data.set_index('Status'), height=300)
                st.markdown("</div>", unsafe_allow_html=True)
        
        with chart_col2:
            st.markdown("<h4 style='text-align: center;'>Traffic by Device (Mbps)</h4>", unsafe_allow_html=True)
            # Group by name and sum the traffic rates for devices with the same name
            device_data = df.groupby('name')['traffic_rate'].sum().reset_index()
            device_data = device_data.set_index('name')
            with st.container():
                st.markdown("<div class='chart-container'>", unsafe_allow_html=True)
                st.bar_chart(device_data, height=300)
                st.markdown("</div>", unsafe_allow_html=True)

# Tab 2: Add Device Form
with tab2:
    st.markdown('<p class="subheader">Add New Device</p>', unsafe_allow_html=True)
    with st.form("add_device_form"):
        col1, col2 = st.columns(2)
        with col1:
            ip = st.text_input("IP Address", placeholder="e.g., 192.168.1.1")
            name = st.text_input("Device Name", placeholder="e.g., Router-01")
        with col2:
            traffic_rate = st.number_input(
                "Traffic Rate (Mbps)", 
                min_value=0.0, 
                max_value=1000.0, 
                value=25.0,
                step=5.0
            )
        # Live status indicator
        if traffic_rate < 5:
            st.markdown("<div class='status-high'>VERY LOW TRAFFIC</div>", unsafe_allow_html=True)
        elif traffic_rate < 10:
            st.markdown("<div class='status-high'>LOW TRAFFIC</div>", unsafe_allow_html=True)
        elif traffic_rate < 50:
            st.markdown("<div class='status-normal'>NORMAL TRAFFIC</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='status-high'>HIGH TRAFFIC</div>", unsafe_allow_html=True)
        submitted = st.form_submit_button("Add Device")
        if submitted:
            if not ip or not name:
                st.error("All fields are required.")
            elif not is_valid_ip(ip):
                st.error("Please enter a valid IP address (format: xxx.xxx.xxx.xxx)")
            else:
                if add_device(ip, name, traffic_rate):
                    time.sleep(1)
                    if hasattr(st, "rerun"):
                        st.rerun()
                    else:
                        st.experimental_rerun()

# Footer
st.markdown("---")
st.markdown("Network Traffic Monitoring System | Computer Networks Project")
