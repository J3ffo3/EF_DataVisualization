
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime

# Paleta de colores personalizada
COLOR_BG = "#f5eee7"
COLOR_PRIMARY = "#9eb944"
COLOR_SECONDARY = "#e6c23e"
COLOR_TERTIARY = "#4b791c"
COLOR_TEXT = "#274e13"

# Configuración inicial
st.set_page_config(page_title="Análisis Superstore", layout="wide")

# Cargar datos
@st.cache_data
def load_data():
    df = pd.read_csv("Sample - Superstore.csv", encoding="ISO-8859-1", parse_dates=["Order Date"])
    df["Mes"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# Estilo general
st.markdown(
    f"""
    <style>
        /* Fuerza fondo y color de texto base */
        html, body, .stApp {{
            background-color: {COLOR_BG} !important;
            color: {COLOR_TEXT} !important;
        }}

        /* Encabezados y textos generales */
        h1, h2, h3, h4, h5, h6,
        .stMarkdown, .stText, .stTitle, .stSubtitle, .stCaption, .stHeader,
        .css-10trblm, .css-1cpxqw2, .css-1d391kg {{
            color: {COLOR_TEXT} !important;
        }}

        /* Etiquetas de filtros y subtítulos */
        label, .stMultiSelect label, .stSelectbox label, .stTextInput label {{
            color: {COLOR_TEXT} !important;
        }}

        /* Contenedor principal */
        .block-container {{
            padding-top: 2rem;
            color: {COLOR_TEXT} !important;
        }}

        /* Métricas y KPIs */
        div[data-testid="metric-container"] {{
            color: {COLOR_TEXT} !important;
        }}
        div[data-testid="metric-container"] > label,
        div[data-testid="metric-container"] > div {{
            color: {COLOR_TEXT} !important;
        }}

        /* Filtros desplegables */
        .stSelectbox > div > div > div {{
            background-color: white !important;
            color: black !important;
        }}

        /* Evita que el modo oscuro sobreescriba */
        [data-baseweb="select"] *, .stDataFrame *, .stButton *, .stMetric * {{
            color: {COLOR_TEXT} !important;
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# ---------------------- FILTROS SUPERIORES ----------------------
st.markdown("#####")
col1, col2, col3 = st.columns(3)
segmentos = df["Segment"].unique()
categorias = df["Category"].unique()
años = sorted(df["Order Date"].dt.year.unique())

with col1:
    segmento_filtro = st.multiselect("Segmento", segmentos, default=segmentos)
with col2:
    categoria_filtro = st.multiselect("Categoría", categorias, default=categorias)
with col3:
    años_filtro = st.multiselect("Años", años, default=años)

df_filtro = df[
    (df["Segment"].isin(segmento_filtro)) &
    (df["Category"].isin(categoria_filtro)) &
    (df["Order Date"].dt.year.isin(años_filtro))
]

# ---------------------- KPIs ----------------------
ventas = df_filtro["Sales"].sum()
ganancia = df_filtro["Profit"].sum()
clientes_unicos = df_filtro["Customer ID"].nunique()

col1, col2, col3 = st.columns(3)
col1.metric("🛒 Ventas totales", f"${ventas:,.0f}")
col2.metric("💰 Ganancia neta", f"${ganancia:,.0f}")
col3.metric("👥 Clientes únicos", clientes_unicos)

# ---------------------- HIPÓTESIS 1 ----------------------
st.markdown("### 🧪 Hipótesis 1: Algunas subcategorías jamás venden lo suficiente")

subcat_ventas = df_filtro.groupby("Sub-Category")["Sales"].sum().sort_values()
subcat_ventas_df = subcat_ventas.reset_index()
subcat_ventas_df["% del total"] = 100 * subcat_ventas_df["Sales"] / subcat_ventas_df["Sales"].sum()

col1, col2 = st.columns(2)

with col1:
    fig_subcat = px.bar(
        subcat_ventas_df,
        x="Sales",
        y="Sub-Category",
        orientation="h",
        text="Sales",
        color_discrete_sequence=[COLOR_PRIMARY]
    )
    fig_subcat.update_traces(texttemplate='%{text:.2s}', textposition='inside')
    fig_subcat.update_layout(title="Ventas por subcategoría", title_font=dict(color=COLOR_TEXT, size=20), plot_bgcolor=COLOR_BG, paper_bgcolor=COLOR_BG, font=dict(color=COLOR_TEXT),
                             xaxis=dict(
            title='Sales',
            title_font=dict(color=COLOR_TEXT),
            tickfont=dict(color=COLOR_TEXT)
        ),
        yaxis=dict(
            title='Sub-Category',
            title_font=dict(color=COLOR_TEXT),
            tickfont=dict(color=COLOR_TEXT)
        ))
    st.plotly_chart(fig_subcat, use_container_width=True)

with col2:
    st.dataframe(subcat_ventas_df.rename(columns={"Sales": "Ventas totales"}), use_container_width=True)

# ---------------------- HIPÓTESIS 2 ----------------------
st.markdown("### 🧪 Hipótesis 2: Ciertos clientes son los que siempre compran mes a mes")

# Calcular clientes por mes
cliente_mes = df_filtro.groupby(["Customer Name", "Mes"])["Sales"].sum().reset_index()
cliente_actividad = cliente_mes.groupby("Customer Name")["Mes"].nunique().sort_values(ascending=False)

top_clientes = cliente_actividad.head(10).reset_index()
top_clientes.columns = ["Cliente", "Meses activos"]

# Heatmap
heatmap_data = cliente_mes.pivot_table(index="Customer Name", columns="Mes", values="Sales", fill_value=0)

fig_heatmap = px.imshow(
    heatmap_data,
    labels=dict(x="Mes", y="Cliente", color="Ventas"),
    color_continuous_scale=["white", COLOR_TERTIARY, COLOR_TERTIARY],
    aspect="auto"
)
fig_heatmap.update_layout(
    title="Actividad mensual por cliente",
    plot_bgcolor="white",
    paper_bgcolor="white",
    font_color=COLOR_TEXT,
    coloraxis=dict(
        colorbar=dict(
            title='Ventas',
            tickfont=dict(color=COLOR_TEXT),
            titlefont=dict(color=COLOR_TEXT)
        )
    )
)

# Gráfico de barras
fig_top = px.bar(
    top_clientes,
    x="Meses activos",
    y="Cliente",
    orientation="h",
    text="Meses activos",
    color_discrete_sequence=[COLOR_TERTIARY]
)
fig_top.update_traces(textposition="inside")
fig_top.update_layout(
    title="Top 10 clientes frecuentes",
    title_font=dict(color=COLOR_TEXT, size=20),
    plot_bgcolor=COLOR_BG,
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    xaxis=dict(title='Meses activos', title_font=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_TEXT)),
    yaxis=dict(title='Cliente', title_font=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_TEXT))
)

# Mostrar gráficos y tabla
st.plotly_chart(fig_heatmap, use_container_width=True)
st.plotly_chart(fig_top, use_container_width=True)
st.dataframe(top_clientes, use_container_width=True)

# ---------------------- HIPÓTESIS 3 ----------------------
st.markdown("### 🧪 Hipótesis 3: Un Ship Mode siempre es preferido por algún segmento")

ship_segment = df_filtro.groupby(["Segment", "Ship Mode"])["Sales"].sum().reset_index()

fig_ship = px.bar(
    ship_segment,
    x="Segment",
    y="Sales",
    color="Ship Mode",
    barmode="group",
    text_auto=True,
    color_discrete_sequence=[COLOR_PRIMARY, COLOR_SECONDARY, COLOR_TERTIARY, "#ccc"]
)
fig_ship.update_layout(
    title="Preferencia de Ship Mode por segmento",
    title_font=dict(color=COLOR_TEXT, size=20),
    plot_bgcolor=COLOR_BG,
    paper_bgcolor=COLOR_BG,
    font=dict(color=COLOR_TEXT),
    xaxis=dict(title='Segmento', title_font=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_TEXT)),
    yaxis=dict(title='Ventas', title_font=dict(color=COLOR_TEXT), tickfont=dict(color=COLOR_TEXT)),
    legend=dict(font=dict(color=COLOR_TEXT))
)
st.plotly_chart(fig_ship, use_container_width=True)