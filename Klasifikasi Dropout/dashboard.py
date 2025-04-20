import streamlit as st
import joblib, requests, tempfile
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from xgboost import XGBClassifier
from sklearn.preprocessing import StandardScaler

# Set page config
st.set_page_config(page_title="Student Dropout Dashboard", layout="wide")

# Load dataset
df = pd.read_csv("https://raw.githubusercontent.com/dicodingacademy/dicoding_dataset/refs/heads/main/students_performance/data.csv", sep=";")

# Unduh file dari URL
url = "https://github.com/Alqurtubi17/pds-hr/raw/main/model_pipeline.pkl"
response = requests.get(url)
if response.status_code == 200:
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        tmp_file.write(response.content)
        tmp_file_path = tmp_file.name

    # Load model
    model, scaler, selected_features = joblib.load(tmp_file_path)
else:
    raise Exception("Gagal mengunduh file model dari GitHub.")


