import streamlit as st
import requests
import pandas as pd

import numpy as np

# Configuración de la página
st.set_page_config(page_title="Deezer Top Charts", page_icon="🎵", layout="wide")

# Título y descripción
st.title("🎵 Deezer Top Charts")
st.markdown("Explora las canciones, álbumes, artistas y más populares según los charts oficiales de Deezer.")

# Sidebar: Selección de categoría
st.sidebar.header("Opciones")
opcion_categoria = st.sidebar.selectbox(
    "Selecciona una categoría",
    ["Canciones", "Álbumes", "Artistas", "Playlists", "Podcasts"]
)

# Mapeo de categorías a campos API
endpoint_fields = {
    "Canciones": "tracks",
    "Álbumes": "albums",
    "Artistas": "artists",
    "Playlists": "playlists",
    "Podcasts": "podcasts",
}

campo_api = endpoint_fields[opcion_categoria]

# Función para obtener datos del chart
@st.cache_data
def obtener_datos_chart(campo_api):
    url = "http://localhost:8080?endpoint=chart"  # URL del backend
    try:
        response = requests.get(url)
        response.raise_for_status()
        datos = response.json().get(campo_api, {}).get("data", [])
        if not datos:
            return pd.DataFrame()

        # Procesar datos según la categoría
        if campo_api == "tracks":
            return pd.DataFrame([{
                "Posición": i + 1,
                "Título": track.get("title", "N/A"),
                "Artista": track["artist"].get("name", "N/A"),
                "Álbum": track["album"].get("title", "N/A"),
                "Duración (s)": track.get("duration", 0),
                "Preview": track.get("preview", None)
            } for i, track in enumerate(datos)])
        elif campo_api in ["albums", "playlists", "podcasts"]:
            return pd.DataFrame([{
                "Posición": i + 1,
                "Título": item.get("title", "N/A"),
                "Link": item.get("link", "N/A")
            } for i, item in enumerate(datos)])
        elif campo_api == "artists":
            return pd.DataFrame([{
                "Posición": i + 1,
                "Nombre": artist.get("name", "N/A"),
                "Link": artist.get("link", "N/A")
            } for i, artist in enumerate(datos)])
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

# Obtener datos de la categoría seleccionada
df = obtener_datos_chart(campo_api)

# Validar si hay datos
if df.empty:
    st.warning(f"No se encontraron datos para la categoría seleccionada: {opcion_categoria}.")
    st.stop()

# Mostrar tabla interactiva
st.subheader(f"Top {opcion_categoria}")
st.dataframe(df, use_container_width=True)

# Gráficos adicionales si la categoría es "Canciones"
if campo_api == "tracks":
    # Gráfico interactivo seleccionado por el usuario
    st.sidebar.subheader("Gráficos interactivos")
    grafico_seleccionado = st.sidebar.selectbox(
        "Selecciona un gráfico",
        ["Histograma de Duración", "Gráfico de Barras", "Gráfico de Líneas", "Dispersión", "Mapa de Calor"]
    )

    if grafico_seleccionado == "Histograma de Duración":
        fig = px.histogram(df, x="Duración (s)", nbins=10, title="Distribución de la Duración de Canciones")
        st.plotly_chart(fig, use_container_width=True)

    elif grafico_seleccionado == "Gráfico de Barras":
        fig = px.bar(df, x="Título", y="Duración (s)", color="Artista",
                     title="Duración de Canciones por Artista",
                     labels={"Duración (s)": "Duración (segundos)"})
        st.plotly_chart(fig, use_container_width=True)

    elif grafico_seleccionado == "Gráfico de Líneas":
        fig = px.line(df, x="Posición", y="Duración (s)", title="Duración por Posición en el Ranking")
        st.plotly_chart(fig, use_container_width=True)

    elif grafico_seleccionado == "Dispersión":
        fig = px.scatter(df, x="Posición", y="Duración (s)", color="Artista",
                         title="Dispersión: Duración vs. Posición", size="Duración (s)")
        st.plotly_chart(fig, use_container_width=True)

    elif grafico_seleccionado == "Mapa de Calor":
        numeric_cols = df.select_dtypes(include=[np.number])
        if not numeric_cols.empty:
            correlation_matrix = numeric_cols.corr()
            fig = px.imshow(correlation_matrix, text_auto=True, title="Mapa de Calor: Correlaciones")
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("No hay datos numéricos suficientes para generar un mapa de calor.")
