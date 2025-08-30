from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import os
import csv
import joblib
import pandas as pd
import random

# --- App Setup ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
app = Flask(__name__, static_folder=SCRIPT_DIR, static_url_path='')
CORS(app)

# --- User Database ---
CSV_FILE = os.path.join(SCRIPT_DIR, 'users.csv')
CSV_HEADERS = ['name', 'phone', 'email', 'gender', 'password']

def initialize_database():
    """Create users.csv with headers if it doesn't exist."""
    if not os.path.exists(CSV_FILE):
        with open(CSV_FILE, mode='w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(CSV_HEADERS)
        print(f"Database file '{CSV_FILE}' created.")

initialize_database()

# --- Load ML Models ---
bp_model = hr_model = stress_model = None
try:
    MODELS_DIR = os.path.join(SCRIPT_DIR, 'models')
    bp_model = joblib.load(os.path.join(MODELS_DIR, 'bp_model.pkl'))
    hr_model = joblib.load(os.path.join(MODELS_DIR, 'hr_model.pkl'))
    stress_model = joblib.load(os.path.join(MODELS_DIR, 'stress_model.pkl'))
    print("✅ All ML models loaded successfully.")
except FileNotFoundError as e:
    print(f"❌ Model file not found: {e}")
except Exception as e:
    print(f"❌ Unexpected error while loading models: {e}")

# --- Static File Routes ---
@app.route('/')
def home():
    return send_from_directory(SCRIPT_DIR, 'home.html')

@app.route('/login.html')
def login_page():
    return send_from_directory(SCRIPT_DIR, 'login.html')

@app.route('/signup.html')
def signup_page():
    return send_from_directory(SCRIPT_DIR, 'signup.html')

@app.route('/index.html')
def index_page():
    return send_from_directory(SCRIPT_DIR, 'index.html')

# --- User Authentication ---
@app.route('/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not all(key in data for key in CSV_HEADERS):
        return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400

    with open(CSV_FILE, mode='a', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=CSV_HEADERS)
        writer.writerow(data)

    return jsonify({'status': 'success', 'message': 'User registered successfully'})

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    with open(CSV_FILE, mode='r', newline='') as f:
        reader = csv.DictReader(f)
        for user in reader:
            if user['email'] == email and user['password'] == password:
                return jsonify({'status': 'success', 'message': 'Login successful'})

    return jsonify({'status': 'error', 'message': 'Invalid email or password'}), 401

# --- ML Prediction Endpoint ---
@app.route('/process', methods=['POST'])
def process_data():
    if not all([bp_model, hr_model, stress_model]):
        return jsonify({'status': 'error', 'message': 'Models are not loaded on the server.'}), 500

    # Simulate a calculated HR input
    simulated_hr = random.uniform(60, 100)
    input_df = pd.DataFrame([[simulated_hr]], columns=['calculated_hr'])

    # Predict
    bp_pred = bp_model.predict(input_df)
    if bp_pred.ndim == 1:  # ensure shape (1,2)
        bp_pred = bp_pred.reshape(1, -1)
    hr_pred = hr_model.predict(input_df)
    stress_pred = stress_model.predict(input_df)

    results = {
        'status': 'success',
        'systolic': round(bp_pred[0, 0]),
        'diastolic': round(bp_pred[0, 1]),
        'heartRate': round(float(hr_pred[0])),
        'stress': stress_pred[0]
    }
    return jsonify(results)

# --- Run App ---
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
