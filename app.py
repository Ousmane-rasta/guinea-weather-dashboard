import streamlit as st
import pandas as pd
import requests
from datetime import date
import base64
import plotly.express as px
from pathlib import Path 


st.set_page_config(page_title="Guinea Weather Dashboard", layout="wide", initial_sidebar_state="expanded")

# ====== FOND D'ÉCRAN =======
def get_base64(file_path):
    with open(file_path, "rb") as f:
        return base64.b64encode(f.read()).decode()

bg_image = get_base64(r"C:\Users\HP\Downloads\Mon_Projet\formes-ou-texture-de-fond-geometrique-abstrait.jpg")
page_bg_img = f"""
<style>
[data-testid="stAppViewContainer"] > .main {{
    background-image: url("data:image/jpeg;base64,{bg_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}
</style>
"""
st.markdown(page_bg_img, unsafe_allow_html=True)

# ====== TITRE =======
st.title("Guinea Weather & Air Quality Dashboard 🌍")
st.sidebar.markdown("Created by **Ousmane Diallo**")

# ====== FONCTIONS =======
def get_coordinates(city, api_key):
    url = f"http://api.openweathermap.org/geo/1.0/direct?q={city}&limit=1&appid={api_key}"
    data = requests.get(url).json()
    if data:
        return data[0]['lat'], data[0]['lon']
    else:
        raise ValueError(f"Ville '{city}' non trouvée.")

def get_weather_data_nasa(lat, lon, selected_date):
    date_str = selected_date.strftime("%Y%m%d")
    parameters_str = ','.join(set(weather_param_map.values()))
    url = (
        f"https://power.larc.nasa.gov/api/temporal/daily/point"
        f"?parameters={parameters_str}"
        f"&community=AG"
        f"&longitude={lon}"
        f"&latitude={lat}"
        f"&start={date_str}&end={date_str}"
        f"&format=JSON"
    )
    return requests.get(url).json()


def get_air_quality(lat, lon, api_key):
    url = f"http://api.openweathermap.org/data/2.5/air_pollution?lat={lat}&lon={lon}&appid={api_key}"
    response = requests.get(url)
    return response.json() if response.status_code == 200 else {}

def get_weather_data_local(city, selected_date, data_dir=r"C:\Users\HP\Downloads\Mon_Projet\data"):
    try:
        filename = f"{city.capitalize()}.csv"
        filepath = Path(data_dir) / filename
        df = pd.read_csv(filepath, sep=';')  # Séparateur utilisé dans tes fichiers
        df.rename(columns={"index": "Date"}, inplace=True)
        df["Date"] = df["Date"].astype(str)
        date_str = selected_date.strftime('%Y%m%d')

        row = df[df["Date"] == date_str]
        if row.empty:
            return None

        return row.iloc[0].to_dict()
    except Exception as e:
        st.error(f"Erreur de lecture du fichier local : {e}")
        return None
    except FileNotFoundError:
        st.warning(f"Fichier non trouvé pour la ville '{city}'. Vérifie le nom du fichier : {city.capitalize()}.csv")
        return None
    except Exception as e:
        st.error(f"Erreur lors de la lecture du fichier local : {e}")
        return None



# Map: Label utilisateur → Nom technique
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
    "Vent moyen 10m (m/s)": "WS10M",
    "Vent max 10m (m/s)": "WS10M_MAX",
    "Vent min 10m (m/s)": "WS10M_MIN",
    "Amplitude vent 10m (m/s)": "WS10M_RANGE",
    "Vent moyen 50m (m/s)": "WS50M",
    "Vent max 50m (m/s)": "WS50M_MAX",
    "Vent min 50m (m/s)": "WS50M_MIN",
    "Amplitude vent 50m (m/s)": "WS50M_RANGE"
}

# Map: Label utilisateur → Emoji
weather_param_emojis = {
    "Amplitude thermique (°C)": "🌡️",
    "Température de surface (°C)": "🌍",
    "Température du point de rosée (°C)": "💧",
    "Température humide (°C)": "💦",
    "Température max (°C)": "🔥",
    "Température min (°C)": "❄️",
    "Température moyenne (°C)": "🌡️",
    "Humidité spécifique (g/kg)": "💧",
    "Humidité relative (%)": "💦",
    "Précipitations (mm)": "🌧️",
    "Pression de surface (hPa)": "📈",
    "Vent moyen 10m (m/s)": "🌬️",
    "Vent max 10m (m/s)": "💨",
    "Vent min 10m (m/s)": "🍃",
    "Amplitude vent 10m (m/s)": "🌪️",
    "Vent moyen 50m (m/s)": "🌬️",
    "Vent max 50m (m/s)": "💨",
    "Vent min 50m (m/s)": "🍃",
    "Amplitude vent 50m (m/s)": "🌪️"
}

# ====== MAIN =======
def main():
    api_key = "4096a4f91a4e8c80e69ca8a4da8675a1"
    st.sidebar.title("🔍 Rechercher")

    # Choix de la source
    #source = st.sidebar.radio("📦 Source des données météo :", ["Automatique (NASA POWER API)", "Fichier CSV local"])

    # Entrée utilisateur
    city = st.sidebar.text_input("🏙️ Entrez le nom d'une ville", "Conakry")
    selected_date = st.sidebar.date_input("📅 Choisissez une date", value=date.today(),  min_value=date(1990, 1, 1), max_value=date.today())
    #selected_date = st.sidebar.date_input("📅 Choisissez une période", value=(date.today() - pd.Timedelta(days=7), date.today()), min_value=date(1990, 1, 1), max_value=date.today())
    selected_labels = st.sidebar.multiselect("Sélectionnez les paramètres météo à afficher :", options=list(weather_param_map.keys()),
    default=["Température moyenne (°C)","Précipitations (mm)", "Humidité relative (%)", "Pression de surface (hPa)", "Vent moyen 10m (m/s)" ])

    if city:
        try:
            lat, lon = get_coordinates(city, api_key)

            #if source == "Automatique (NASA POWER API)":
            weather_data = get_weather_data_nasa(lat, lon, selected_date)
            date_str = selected_date.strftime("%Y%m%d")
            parameters = weather_data.get("properties", {}).get("parameter", {})
            st.subheader(city.title() + ", " + selected_date.strftime('%d/%m/%Y'))
            selected_params = [weather_param_map[label] for label in selected_labels]
            cols = st.columns(len(selected_params))
            for i, param in enumerate(selected_params):
                emoji = weather_param_emojis[selected_labels[i]]
                value = parameters.get(param, {}).get(date_str, "N/A")
                cols[i].metric(f"{emoji} {selected_labels[i]}", f"{value}")


#            elif source == "Fichier CSV local":
#                weather = get_weather_data_local(city, selected_date)
#                if weather:
#                    st.subheader(f"📊 Données météo (locale) du {selected_date.strftime('%d/%m/%Y')} à {city.title()}")
#                    # Affichage dynamique des paramètres sélectionnés
#                selected_params = [weather_param_map[label] for label in selected_labels]
#                cols = st.columns(len(selected_params))
#                for i, param in enumerate(selected_params):
#                    emoji = weather_param_emojis[selected_labels[i]]
#                    value = weather.get(param, "N/A")
#                    cols[i].metric(f"{emoji} {selected_labels[i]}", f"{value}")
            
            # Données qualité de l'air (toujours en ligne)
            air_quality = get_air_quality(lat, lon, api_key)
            pollutants = air_quality.get("list", [{}])[0].get("components", {})
            if pollutants:
                df = pd.DataFrame(pollutants.items(), columns=["Pollutant", "Value"])
                df = df.sort_values(by="Value", ascending=False)
                fig = px.bar(df, x="Pollutant", y="Value", text="Value", title="Pollutant Levels (μg/m³)")
                fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
                fig.update_layout(margin=dict(t=80))
                st.plotly_chart(fig)
            else:
                st.info("Aucune donnée de qualité de l'air disponible.")
                # ===== Ajout du bouton de téléchargement =====
            if parameters or pollutants:
    # Combiner les données météo et air dans un seul DataFrame
                weather_df = pd.DataFrame({k: [v.get(date_str, None)] for k, v in parameters.items()})
                air_df = pd.DataFrame(pollutants.items(), columns=["Pollutant", "Value"])
    
    # Convertir en CSV
                weather_csv = weather_df.to_csv(index=False).encode('utf-8')
                air_csv = air_df.to_csv(index=False).encode('utf-8')
    
    # Bouton pour télécharger les données météo
                st.download_button(
                label="📥 Télécharger les données météo",
                data=weather_csv,
                file_name=f"{city}_{date_str}_weather.csv",
                mime="text/csv"
    )
    
    # Bouton pour télécharger les données air
                st.download_button(
                label="📥 Télécharger les données qualité de l'air",
                data=air_csv,
                file_name=f"{city}_{date_str}_air_quality.csv",
                mime="text/csv"
    )


        except Exception as e:
            st.error(f"❌ Erreur : {e}")


if __name__ == "__main__":
    main()
st.info("Dans le cas où vous observez des valeurs aberrantes, comme -9999, cela indique que les données pour la date sélectionnée ne sont pas encore disponibles. Nous vous invitons à choisir une date antérieure.")
