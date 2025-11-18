import streamlit as st
import pandas as pd
import os
import datetime
import pydeck as pdk 
import matplotlib.pyplot as plt 
# Importar seaborn para los gráficos estadísticos
import seaborn as sns 

# --- 0. Configuración, CSS y Carga de Datos ---

st.set_page_config(layout="wide")
st.title("Avistamientos de Animales en México")
st.markdown("Filtra las observaciones por especie y un rango de tiempo (mes y año).")

FILE_PATH = 'Data/base.csv'

@st.cache_data
def load_data(path):
    """Carga y preprocesa el DataFrame."""
    if not os.path.exists(path):
        st.error(f"Error: El archivo no se encuentra en la ruta especificada: {path}")
        return pd.DataFrame()
    
    try:
        df = pd.read_csv(path)
        
        df = df.dropna(subset=['decimalLatitude', 'decimalLongitude', 'eventDate'])
        
        # Renombrar decimalLatitude y decimalLongitude a lat y lon, y mantener los nombres originales
        df = df.rename(columns={'decimalLatitude': 'lat', 'decimalLongitude': 'lon'}).copy() 
        df['decimalLatitude'] = df['lat']
        df['decimalLongitude'] = df['lon']
        
        df['eventDate'] = pd.to_datetime(df['eventDate'], errors='coerce')
        df = df.dropna(subset=['eventDate']) 
        df['YearMonth'] = df['eventDate'].dt.to_period('M')
        df['year'] = df['eventDate'].dt.year
        
        # Calcular conteo de especies para el orden
        species_counts = df['verbatimScientificName'].value_counts().reset_index()
        species_counts.columns = ['verbatimScientificName', 'count']
        
        # Merge para tener el conteo junto a cada observación
        df = pd.merge(df, species_counts, on='verbatimScientificName', how='left')
        
        # **Asegurar la columna 'stateProvince' para el gráfico de estados**
        if 'stateProvince' not in df.columns:
            st.warning("La columna 'stateProvince' no se encontró y se agregó vacía. El gráfico de provincias no funcionará sin ella.")
            df['stateProvince'] = 'Desconocido'

        return df
    except Exception as e:
        st.error(f"Error al leer o procesar el archivo CSV: {e}")
        return pd.DataFrame()

observaciones = load_data(FILE_PATH)

if observaciones.empty:
    st.info("Por favor, asegúrate de que el archivo 'base.csv' exista en la ruta especificada.")
    st.stop()

todas_las_especies = sorted(observaciones['verbatimScientificName'].unique())

# --- 1. Generación de Mapa de Colores para PyDeck ---

color_map = {}
default_gray = [180, 180, 180, 255] 

if 'verbatimScientificName' in observaciones.columns:
    all_species_unique = sorted(observaciones['verbatimScientificName'].dropna().unique())
    color_palette = plt.cm.tab20.colors 
    
    for i, sp in enumerate(all_species_unique):
        color_index = i % len(color_palette)
        rgb_float = color_palette[color_index]
        rgb_255 = [int(c * 255) for c in rgb_float[:3]] + [255] 
        color_map[sp] = rgb_255

# --- 2. Gestión del Estado y Funciones de Acción (CORREGIDO) ---

MULTISELECT_KEY = 'especies_filtradas_lista' 

def update_filter_list():
    """Actualiza la lista de especies seleccionadas en el estado de la sesión."""
    selected_species = []
    for species in todas_las_especies:
        toggle_key = f"toggle_{species}"
        if st.session_state.get(toggle_key, False):
            selected_species.append(species)
    
    st.session_state[MULTISELECT_KEY] = selected_species


if MULTISELECT_KEY not in st.session_state:
    for species in todas_las_especies:
        st.session_state[f"toggle_{species}"] = True
    update_filter_list()

def select_all_species_action():
    """Selecciona todos los toggles y actualiza la lista de filtro."""
    for species in todas_las_especies:
        st.session_state[f"toggle_{species}"] = True
    update_filter_list() 

def deselect_all_species_action():
    """Deselecciona todos los toggles y actualiza la lista de filtro."""
    for species in todas_las_especies:
        st.session_state[f"toggle_{species}"] = False
    update_filter_list()


# --- 3. Inyección de CSS Personalizado (Mantenido) ---

st.markdown(
    """
    <style>
    /* Estilo para los botones de control (25x25px) */
    [data-testid="stSidebar"] [data-testid="column"] .stButton button {
        width: 25px !important;
        height: 25px !important;
        padding: 0;
        margin: 0;
        line-height: 1; 
        display: flex;
        justify-content: center;
        align-items: center;
    }

    /* Estilo para los toggles (botones de especie) */
    [data-testid="stToggle"] > label {
        width: 100%;
        padding: 5px 10px;
        margin: 2px 0;
        border-radius: 0.5rem;
        border: 1px solid rgba(49, 51, 63, 0.2);
        cursor: pointer;
        transition: all 0.1s ease-in-out;
    }

    /* Estilo para el botón DESELECCIONADO (claro) */
    [data-testid="stToggle"] > label:not([aria-checked="true"]) {
        background-color: #F0F2F6;
        color: #4B4B4B;
    }
    
    /* Estilo para el botón SELECCIONADO (oscuro) */
    [data-testid="stToggle"] > label[aria-checked="true"] {
        background-color: #004D40;
        color: white;
    }

    /* Ocultar el interruptor/switch nativo */
    [data-testid="stToggle"] div:last-child {
        display: none;
    }
    
    /* Quitar línea horizontal */
    [data-testid="stSidebar"] hr {
        display: none;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 4. Definición de Filtros en la Barra Lateral (CORREGIDO) ---

st.sidebar.header("Filtros de Datos")

col_select_all, col_deselect_all = st.sidebar.columns([1, 1])

col_select_all.button("✓", on_click=select_all_species_action, key="btn_select_all", help="Seleccionar TODAS las especies.", use_container_width=True)
col_deselect_all.button("×", on_click=deselect_all_species_action, key="btn_deselect_all", help="Deseleccionar TODAS las especies.", use_container_width=True)


# --- A. Listado de Especies como Botones (Slicer Nativo) ---
st.sidebar.subheader("Especie")

species_counts_df = observaciones[['verbatimScientificName', 'count']].drop_duplicates().sort_values(by='count', ascending=False)
ordered_species = species_counts_df['verbatimScientificName'].tolist()

with st.sidebar.container(height=300, border=False):
    for species in ordered_species:
        count = species_counts_df[species_counts_df['verbatimScientificName'] == species]['count'].iloc[0]
        label = f"{species} ({count})"
        toggle_key = f"toggle_{species}" 

        st.toggle(label, key=toggle_key, on_change=update_filter_list)


# --- B. Filtro de Rango de Fecha (Mes y Año) ---
st.sidebar.subheader("Filtro de Rango de Fecha")
all_periods = sorted(observaciones['YearMonth'].unique())

start_period, end_period = None, None
if all_periods:
    min_date = all_periods[0].start_time.date()
    max_date = all_periods[-1].end_time.date()
    
    date_range = st.sidebar.slider(
        'Selecciona el rango de Mes/Año:',
        min_value=min_date, max_value=max_date, value=(min_date, max_date), format="YYYY-MM"
    )

    start_period = pd.Period(pd.to_datetime(date_range[0]), freq='M')
    end_period = pd.Period(pd.to_datetime(date_range[1]), freq='M')
else:
    st.sidebar.warning("No hay datos de fecha válidos para el filtro.")


# --- 5. Filtrado de Datos (Mantenido) ---

especies_seleccionadas = st.session_state.get(MULTISELECT_KEY, todas_las_especies)

# 1. Filtrar por especie
df_filtrado_especie = observaciones[observaciones['verbatimScientificName'].isin(especies_seleccionadas)].copy()

# 2. Filtrar por fecha
if start_period and end_period:
    df_final = df_filtrado_especie[
        (df_filtrado_especie['YearMonth'] >= start_period) & 
        (df_filtrado_especie['YearMonth'] <= end_period)
    ].copy()
else:
    df_final = df_filtrado_especie.copy()


# --- 6. Visualización del Mapa (Mantenido) ---

st.header("Distribución de Avistamientos")

if df_final.empty:
    st.warning("No hay observaciones que coincidan con los filtros seleccionados. Intenta ajustar los filtros.")
else:
    st.markdown(f"**Total de observaciones visualizadas:** **{len(df_final)}**")
    
    # --- Aplicar Colores ---
    if 'verbatimScientificName' in df_final.columns:
        df_final['color'] = df_final['verbatimScientificName'].map(color_map).apply(
            lambda c: c if isinstance(c, list) and len(c) == 4 else default_gray
        )
    else:
        df_final['color'] = [default_gray] * len(df_final)

    # --- Creación de la Capa y el Mapa PyDeck ---
    
    point_radius = 5000 
    layer = pdk.Layer(
        "ScatterplotLayer",
        data=df_final,
        get_position=['decimalLongitude', 'decimalLatitude'], 
        get_color="color", 
        get_radius=point_radius,
        pickable=True
    )

    center_lat = df_final["lat"].mean() if not df_final["lat"].empty else 23.6345
    center_lon = df_final["lon"].mean() if not df_final["lon"].empty else -102.5528
    
    view_state = pdk.ViewState(
        latitude=center_lat,
        longitude=center_lon,
        zoom=4,
        pitch=0
    )

    tooltip = {
        "html": "<b>Especie:</b> {verbatimScientificName}<br/><b>Año:</b> {year}",
        "style": {"backgroundColor": "rgba(50, 50, 50, 0.8)", "color": "white"}
    }

    st.pydeck_chart(
        pdk.Deck(
            layers=[layer], 
            initial_view_state=view_state, 
            tooltip=tooltip
        ),
        use_container_width=True
    )
    
    with st.expander("Ver Datos Filtrados"):
        st.dataframe(df_final[['verbatimScientificName', 'eventDate', 'lat', 'lon']].sort_values(by='eventDate', ascending=False), use_container_width=True)

# -------------------------------------------------------------
# 🌟 NUEVA SECCIÓN: GRÁFICOS ESTÁTICOS 🌟
# Nota: Se ha reemplazado 'mexico_df' por 'df_final' para usar datos filtrados.
# -------------------------------------------------------------

if not df_final.empty:
    
    # ======================================
    # 7 & 8. TOP 10 ESPECIES Y PROVINCIAS (50/50 Layout)
    # ======================================
    st.markdown("---")
    st.subheader("Análisis de Distribución: Top 10 Especies y Provincias")

    col_species, col_states = st.columns([1, 1])

    # === COLUMNA DE ESPECIES ===
    with col_species:
        st.markdown("#### Top 10 especies más registradas")
        if 'verbatimScientificName' in df_final.columns and not df_final['verbatimScientificName'].empty:
            top_species = df_final['verbatimScientificName'].value_counts().head(10)
            
            # Solo graficar si hay datos
            if not top_species.empty:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(x=top_species.values, y=top_species.index, palette="crest", ax=ax)
                
                # === AÑADIR ETIQUETAS ===
                for i, (count, name) in enumerate(zip(top_species.values, top_species.index)):
                    # Calcula un offset basado en el valor máximo para evitar cortar las etiquetas
                    max_count = top_species.values[0]
                    offset = max_count * 0.02 
                    ax.text(count + offset, i, f'{count}', va='center', fontsize=9, color='black')

                ax.set_title("Top 10 especies más registradas")
                ax.set_xlabel("Número de registros")
                
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No hay especies registradas en los datos filtrados.")
        else:
            st.warning("No se encontró la columna 'verbatimScientificName' o está vacía para el Top 10.")


    # === COLUMNA DE PROVINCIAS/ESTADOS ===
    with col_states:
        st.markdown("#### Top 10 provincias con más registros")
        if 'stateProvince' in df_final.columns and not df_final['stateProvince'].empty:
            top_states = df_final['stateProvince'].value_counts().head(10)
            
            # Solo graficar si hay datos
            if not top_states.empty:
                fig, ax = plt.subplots(figsize=(10, 5))
                sns.barplot(x=top_states.values, y=top_states.index, palette="flare", ax=ax)

                # === AÑADIR ETIQUETAS ===
                for i, (count, name) in enumerate(zip(top_states.values, top_states.index)):
                    # Calcula un offset basado en el valor máximo para evitar cortar las etiquetas
                    max_count = top_states.values[0]
                    offset = max_count * 0.02 
                    ax.text(count + offset, i, f'{count}', va='center', fontsize=9, color='black')

                ax.set_title("Top 10 provincias con más registros")
                ax.set_xlabel("Número de registros")
                
                fig.tight_layout()
                st.pyplot(fig)
                plt.close(fig)
            else:
                st.info("No hay provincias registradas en los datos filtrados.")
        else:
            st.warning("No se encontró la columna 'stateProvince' o está vacía para el Top 10.")


    # ======================================
    # 9. HISTOGRAMA DE OBSERVACIONES POR AÑO Y ESPECIE
    # ======================================
    st.markdown("---")
    st.subheader("Tendencia Temporal: Histograma de Observaciones por Año (Top 5 Especies)")

    if 'year' in df_final.columns and 'verbatimScientificName' in df_final.columns:
        # 1. Identificar las Top 5 especies en el DF FILTRADO
        top_n = 5
        top_species_list = df_final['verbatimScientificName'].value_counts().head(top_n).index.tolist()
        
        # 2. Crear un DataFrame para el histograma, agrupando el resto
        df_hist = df_final.copy()
        df_hist['species_group'] = df_hist['verbatimScientificName'].apply(
            lambda x: x if x in top_species_list else 'Otras Especies'
        )
        
        # 3. Determinar los límites de los bins
        if not df_hist['year'].dropna().empty:
            min_year = int(df_hist['year'].min())
            max_year = int(df_hist['year'].max())
            
            # Asegurar que el rango de años no sea cero para evitar errores
            if max_year > min_year:
                num_bins = max_year - min_year
            else:
                num_bins = 1 # Si solo hay un año o menos
            
            # 4. Generar la figura
            fig, ax = plt.subplots(figsize=(12, 6))
            
            # Usar Seaborn para el histograma apilado
            sns.histplot(
                data=df_hist.dropna(subset=['year']), # Eliminar NaNs en el año para el plot
                x='year',
                hue='species_group',
                multiple='stack', # Esto es lo que crea el apilamiento
                bins=num_bins, 
                palette='tab10',
                ax=ax
            )
            
            ax.set_title("Tendencia temporal de registros, apilada por Top 5 especies")
            ax.set_xlabel("Año de Registro")
            ax.set_ylabel("Número de Observaciones")
            
            # Ajustar el eje X para mostrar años de manera legible
            ax.set_xticks(ax.get_xticks().astype(int))
            plt.xticks(rotation=45, ha='right')
            
            fig.tight_layout()
            st.pyplot(fig)
            plt.close(fig)
        else:
             st.info("No hay datos de año válidos para generar el histograma apilado en el rango seleccionado.")
    else:
        st.warning("No se encontraron las columnas 'year' o 'verbatimScientificName' para generar el histograma apilado.")