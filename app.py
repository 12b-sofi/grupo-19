import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

colores_udec = {
    'azul': '#003DA5',
    'amarillo': '#e69b0a',
    'gris': '#a0a0a0',
    'rojo': '#d21428',
    'mujer': '#E91E63',
    'hombre': '#1976D2',
    'mujer_claro': '#F8BBD0',
    'mujer_medio': '#F06292',
    'mujer_oscuro': '#C2185B',
    'hombre_claro': '#BBDEFB',
    'hombre_medio': '#64B5F6',
    'hombre_oscuro': '#1565C0',
    'brecha': '#FF9800',
    'verde': '#66BB6A',
    'amarillo_riesgo': '#FFA726',
    'rojo_riesgo': '#EF5350'}

def crear_grafico_lineas(df, col_x, lista_columnas, titulo, nombre_eje_y):
    datos = df.copy()
    datos = datos[datos[lista_columnas].sum(axis=1) > 0]
    if datos.empty:
        return None
    fig = go.Figure()
    for col in lista_columnas:
        if col.endswith('_M'):
            nombre = 'Mujeres'
            color = colores_udec['mujer']
        else:
            nombre = 'Hombres'
            color = colores_udec['hombre']
        fig.add_trace(go.Scatter(
            x=datos[col_x],
            y=datos[col],
            mode='lines+markers',
            name=nombre,
            line=dict(color=color, width=3),
            marker=dict(size=8, color='white', line=dict(width=2, color=color))))
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title="Año",
        yaxis_title=nombre_eje_y,
        plot_bgcolor='white',
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        margin=dict(t=60, b=60, l=60, r=40),
        xaxis=dict(showgrid=False, tickangle=0, tickmode='linear', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400)
    return fig

def crear_grafico_barras_apiladas(df, col_x, lista_columnas, titulo):
    datos = df.copy()
    datos = datos[datos[lista_columnas].sum(axis=1) > 0]
    if datos.empty:
        return None
    datos = datos.sort_values(col_x, ascending=False)
    fig = go.Figure()
    for col in lista_columnas:
        if col.endswith('_M'):
            nombre = 'Mujeres'
            color = colores_udec['mujer']
        else:
            nombre = 'Hombres'
            color = colores_udec['hombre']
        fig.add_trace(go.Bar(
            y=datos[col_x].astype(str),
            x=datos[col],
            name=nombre,
            orientation='h',
            marker=dict(color=color),
            text=datos[col].round(0).astype(int),
            textposition='auto'))
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        barmode='stack',
        plot_bgcolor='white',
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        xaxis=dict(showticklabels=False),
        margin=dict(t=60, b=60, l=60, r=40),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400)
    return fig

def crear_grafico_brecha(df, columna_brecha, titulo):
    datos = df[df[columna_brecha].notna()].copy()
    if datos.empty:
        return None
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=datos['año'],
        y=datos[columna_brecha],
        mode='lines+markers',
        name='Brecha (M - H)',
        line=dict(color=colores_udec['brecha'], width=3, shape='spline'),
        marker=dict(size=8, color=colores_udec['brecha'])))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", annotation_text="Equilibrio")
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title="Año",
        yaxis_title="Diferencia",
        plot_bgcolor='white',
        hovermode="x unified",
        margin=dict(t=60, b=60, l=60, r=40),
        xaxis=dict(showgrid=False, tickangle=0, tickmode='linear', dtick=1),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400)
    return fig

st.set_page_config(page_title="Análisis de Brechas de Género - UdeC", page_icon="📊", layout="wide")
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Roboto:wght@300;400;500&display=swap');
        html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
        h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif; color: #223c6a; }
        .stButton>button { background-color: #223c6a; color: white; font-family: 'Poppins', sans-serif; }
        .stButton>button:hover { background-color: #e69b0a; color: #223c6a; }
    </style>
    """, unsafe_allow_html=True)

carreras_disponibles = [
    'Ingeniería Civil Industrial',
    'Ingeniería Civil',
    'Ingeniería Civil Eléctrica',
    'Ingeniería Civil Electrónica',
    'Ingeniería Civil Informática']

usuarios_sistema = {
    "admin": "admin123",
    "industrial": "clave1",
    "informatica": "clave2"}

roles_usuarios = {
    "admin": "admin",
    "industrial": "Ingeniería Civil Industrial",
    "informatica": "Ingeniería Civil Informática"}

def verificar_credenciales(usuario, contraseña):
    return usuario in usuarios_sistema and usuarios_sistema[usuario] == contraseña

def obtener_rol_usuario(usuario):
    return roles_usuarios.get(usuario, None)

def cargar_datos():
    if not hasattr(st.session_state, "datos_base_maestra"):
        datos = pd.read_csv('data/base_maestra.csv')
        st.session_state.datos_base_maestra = datos
    return st.session_state.datos_base_maestra

def pagina_login():
    st.markdown("<h1 style='text-align: center;'>Sistema de Análisis de Brechas de Género</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Universidad de Concepción - Facultad de Ingeniería</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Iniciar Sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.button("Ingresar"):
            if verificar_credenciales(usuario, contraseña):
                rol_usuario = obtener_rol_usuario(usuario)
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.session_state.rol = rol_usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def aplicacion_principal():
    st.title("Sistema de Análisis de Brechas de Género en Ingeniería")
    st.markdown(f"**Usuario:** {st.session_state.usuario} | **Rol:** {st.session_state.rol}")
    datos = cargar_datos()
    if datos is None:
        st.warning("No se encontraron datos.")
        return
    with st.sidebar:
        st.header("Filtros")
        carreras_permitidas = carreras_disponibles if st.session_state.rol == "admin" else [st.session_state.rol]
        if st.session_state.rol == "admin":
            carrera_seleccionada = st.selectbox("Seleccionar Carrera", options=["Todas"] + carreras_permitidas)
        else:
            carrera_seleccionada = st.selectbox("Carrera", options=carreras_permitidas, disabled=True)
        st.markdown("---")
        if st.button("Cerrar Sesión"):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            if hasattr(st.session_state, "datos_base_maestra"):
                del st.session_state.datos_base_maestra
            st.rerun()
    datos_filtrados = datos.copy()
    if carrera_seleccionada != "Todas":
        datos_filtrados = datos_filtrados[datos_filtrados['carrera'] == carrera_seleccionada]
    if datos_filtrados.empty:
        st.warning("No hay datos para los filtros seleccionados")
        return
    st.header("Evolución de Ingresos")
    grafico = crear_grafico_lineas(
        datos_filtrados,
        'año',
        ['ingresos_M', 'ingresos_H'],
        'Cantidad de Ingresos por Año',
        'Cantidad de Ingresos')
    if grafico:
        st.plotly_chart(grafico, use_container_width=True)
    else:
        st.info("No hay datos suficientes para mostrar el gráfico.")

if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

if not st.session_state.autenticado:
    pagina_login()
else:
    aplicacion_principal()
    
