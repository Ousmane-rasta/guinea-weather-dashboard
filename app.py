import streamlit as st
import pandas as pd
import requests
from datetime import date
import base64
import altair as alt
from pathlib import Path
import yaml

# ================= CONFIG =================
st.set_page_config(
    page_title="Guinea Weather Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ================= FOND =================
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64(
    r"C:\Users\HP\Downloads\Mon_Projet\formes-ou-texture-de-fond-geometrique-abstrait.jpg"
)

st.markdown(
    f"""
    <style>
    [data-testid="stAppViewContainer"] > .main {{
        background-image: url("data:image/jpeg;base64,{bg_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    </style>
    """,
    unsafe_allow_html=True
)

# ================= TITRE =================
st.title("Guinea Weather Dashboard")
st.sidebar.markdown("Created by **Ousmane Diallo**")

# ================= CHARGEMENT YAML =================
@st.cache_data
def load_coordinates(yaml_file):
    with open(yaml_file, "r") as f:
        data = yaml.safe_load(f)
    # Convertir la liste en dict
    prefectures_dict = {loc["name"]: {"lat": loc["lat"], "lon": loc["lon"]} for loc in data["locations"]}
    return prefectures_dict

COORD_FILE = r"C:\Users\HP\Downloads\Mon_Projet\config.yaml"
PREFECTURES = load_coordinates(COORD_FILE)

# ================= NASA POWER =================
def get_weather_data_nasa(lat, lon, selected_date, parameters):
    date_str = selected_date.strftime("%Y%m%d")
    url = (
        "https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={parameters}"
        f"&community=AG"
        f"&latitude={lat}"
        f"&longitude={lon}"
        f"&start={date_str}&end={date_str}"
        f"&format=JSON"
    )
    response = requests.get(url)
    response.raise_for_status()
    return response.json()

# ================= PARAMÈTRES =================
weather_param_map = {
    "Amplitude thermique (°C)": "T2M_RANGE",
    "Température de surface (°C)": "TS",
    "Température du point de rosée (°C)": "T2MDEW",
    "Température humide (°C)": "T2MWET",
    "Température max (°C)": "T2M_MAX",
    "Température min (°C)": "T2M_MIN",
    "Température moyenne (°C)": "T2M",
    "Humidité spécifique (g/kg)": "QV2M",
    "Humidité relative (%)": "RH2M",
    "Précipitations (mm)": "PRECTOTCORR",
    "Pression de surface (hPa)": "PS",
    "Vent moyen 10m (m/s)": "WS10M"
}

# ================= MAIN =================
def main():
    st.sidebar.title("🔍 Paramètres")

    prefecture = st.sidebar.selectbox(
        "🏙️ Sélectionnez une préfecture",
        options=list(PREFECTURES.keys())
    )

    selected_date = st.sidebar.date_input(
        "📅 Choisissez une date",
        value=date.today(),
        min_value=date(1990, 1, 1),
        max_value=date.today()
    )

    selected_labels = st.sidebar.multiselect(
        "📊 Paramètres météo",
        options=list(weather_param_map.keys()),
        default=[
            "Température moyenne (°C)",
            "Précipitations (mm)",
            "Humidité relative (%)",
            "Pression de surface (hPa)",
            "Vent moyen 10m (m/s)"
        ]
    )

    lat = PREFECTURES[prefecture]["lat"]
    lon = PREFECTURES[prefecture]["lon"]

    try:
        params_str = ",".join(
            weather_param_map[label] for label in selected_labels
        )

        weather_data = get_weather_data_nasa(
            lat, lon, selected_date, params_str
        )

        date_str = selected_date.strftime("%Y%m%d")
        parameters = weather_data["properties"]["parameter"]

        st.subheader(f"{prefecture} — {selected_date.strftime('%d/%m/%Y')}")

        cols = st.columns(len(selected_labels))
        for i, label in enumerate(selected_labels):
            param = weather_param_map[label]
            value = parameters.get(param, {}).get(date_str, "N/A")
            cols[i].metric(label, value)

        # ===== TELECHARGEMENT =====
        df = pd.DataFrame(
            {k: [v.get(date_str, None)] for k, v in parameters.items()}
        )

        csv = df.to_csv(index=False).encode("utf-8")

        st.download_button(
            "📥 Télécharger les données NASA POWER",
            data=csv,
            file_name=f"{prefecture}_{date_str}_NASA_POWER.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Erreur : {e}")

# ================= RUN =================
if __name__ == "__main__":
    main()

st.info(
    "Les valeurs -9999 indiquent des données non disponibles pour la date sélectionnée."
)
