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
opcion_categoria = st.sidebar.selectbox("Selecciona una categoría",
                                        ["Canciones", "Álbumes", "Artistas", "Playlists", "Podcasts"])

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
@st.cache
def obtener_datos_chart(campo_api):
    try:
        url = "http://localhost:8080?endpoint=chart"  # URL del backend
        response = requests.get(url)
        response.raise_for_status()
        data = response.json().get(campo_api, {}).get("data", [])

        if not data:
            st.warning(f"No se encontraron datos para {opcion_categoria}.")
            return pd.DataFrame()

        # Procesar datos según la categoría
        if campo_api == "tracks":
            return pd.DataFrame([{
                "Posición": i + 1,
                "Título": track.get("title", "N/A"),
                "Artista": track["artist"]["name"],
                "Álbum": track["album"]["title"],
                "Duración (s)": track.get("duration", 0),
                "Preview": track.get("preview", None)
            } for i, track in enumerate(data)])
        elif campo_api in ["albums", "playlists", "podcasts"]:
            return pd.DataFrame([{
                "Posición": i + 1,
                "Título": item.get("title", "N/A"),
                "Link": item.get("link", "N/A")
            } for i, item in enumerate(data)])
        elif campo_api == "artists":
            return pd.DataFrame([{
                "Posición": i + 1,
                "Nombre": artist.get("name", "N/A"),
                "Link": artist.get("link", "N/A")
            } for i, artist in enumerate(data)])

    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener datos: {e}")
        return pd.DataFrame()

# Obtener datos de la categoría seleccionada
df = obtener_datos_chart(campo_api)

# Validar si hay datos
if df.empty:
    st.stop()

# Mostrar tabla interactiva
st.subheader(f"Top {opcion_categoria}")
st.dataframe(df, use_container_width=True)

# Gráficos adicionales si la categoría es "Canciones"
if campo_api == "tracks":
    # Histograma
    st.subheader("Histograma de Duración")
    fig_hist = px.histogram(df, x="Duración (s)", nbins=10, title="Distribución de la Duración de Canciones")
    st.plotly_chart(fig_hist, use_container_width=True)

    # Gráfico de barras
    st.subheader("Gráfico de Barras: Duración por Canción")
    fig_bar = px.bar(df, x="Título", y="Duración (s)", color="Artista",
                     title="Duración de Canciones por Artista", labels={"Duración (s)": "Duración (segundos)"})
    st.plotly_chart(fig_bar, use_container_width=True)

    # Gráfico de líneas
    st.subheader("Gráfico de Líneas: Duración por Posición")
    fig_line = px.line(df, x="Posición", y="Duración (s)", title="Duración por Posición en el Ranking")
    st.plotly_chart(fig_line, use_container_width=True)

    # Diagrama de dispersión
    st.subheader("Dispersión: Posición vs. Duración")
    fig_scatter = px.scatter(df, x="Posición", y="Duración (s)", color="Artista",
                             title="Dispersión: Duración vs. Posición", size="Duración (s)")
    st.plotly_chart(fig_scatter, use_container_width=True)

    # Mapa de calor
    st.subheader("Mapa de Calor: Correlación entre Variables")
    if len(df.columns) > 2:  # Asegurarse de tener suficientes columnas
        numeric_cols = df.select_dtypes(include=[np.number])
        correlation_matrix = numeric_cols.corr()
        fig_heatmap = px.imshow(correlation_matrix, text_auto=True, title="Mapa de Calor: Correlaciones")
        st.plotly_chart(fig_heatmap, use_container_width=True)
