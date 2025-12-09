import streamlit as st
import pandas as pd

# Importar funciones de gráficos actualizadas
from graficos_udec import (
    crear_grafico_lineas, crear_grafico_barras_apiladas, crear_grafico_barras_agrupadas,
    crear_grafico_dona, crear_grafico_radar, crear_grafico_barras_horizontales, 
    crear_grafico_brecha, colores_udec
)

# Configuración de la página
st.set_page_config(page_title="Análisis de Brechas de Género - UdeC", page_icon="📊", layout="wide")

# Aplicar estilos CSS de UdeC
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&family=Roboto:wght@300;400;500&display=swap');
    html, body, [class*="css"] { font-family: 'Roboto', sans-serif; }
    h1, h2, h3, h4, h5, h6 { font-family: 'Poppins', sans-serif; color: #223c6a; }
    .stButton>button { background-color: #223c6a; color: white; font-family: 'Poppins', sans-serif; }
    .stButton>button:hover { background-color: #e69b0a; color: #223c6a; }
</style>
""", unsafe_allow_html=True)

def verificar_credenciales(usuario, contraseña):
    """Verifica si el usuario y contraseña son correctos"""
    try:
        usuarios = st.secrets["usuarios"]
        if usuario in usuarios and usuarios[usuario] == contraseña:
            return True
    except Exception:
        pass
    return False

def obtener_rol_usuario(usuario):
    """Obtiene el rol del usuario (admin o carrera específica)"""
    try:
        return st.secrets["roles"].get(usuario, None)
    except Exception:
        return None

def obtener_carreras_permitidas(rol):
    todas_las_carreras = [
        'Ingeniería Civil Industrial', 'Ingeniería Civil', 'Ingeniería Civil Eléctrica',
        'Ingeniería Civil Electrónica', 'Ingeniería Civil Informática'
    ]
    if rol == "admin":
        return todas_las_carreras
    elif rol in todas_las_carreras:
        return [rol]
    else:
        return []

def pagina_login():
    st.markdown("<h1 style='text-align: center;'>Sistema de Análisis de Brechas de Género</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Universidad de Concepción - Facultad de Ingeniería</h3>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### Iniciar Sesión")
        usuario = st.text_input("Usuario")
        contraseña = st.text_input("Contraseña", type="password")
        if st.button("Ingresar", use_container_width=True):
            if verificar_credenciales(usuario, contraseña):
                rol = obtener_rol_usuario(usuario)
                st.session_state.autenticado = True
                st.session_state.usuario = usuario
                st.session_state.rol = rol
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

@st.cache_data
def cargar_datos():
    """Carga el archivo base maestra con todos los datos procesados"""
    try:
        return pd.read_csv('data/base_maestra.csv')
    except FileNotFoundError:
        st.error("No se encontró data/base_maestra.csv. Ejecuta el notebook primero.")
        return None

def mostrar_card_reprobaciones(titulo, promedio, minimo, maximo):
    """Muestra una tarjeta con estadísticas de reprobaciones"""
    st.markdown(f"""
    <div style='background-color: #f8f9fa; padding: 20px; border-radius: 10px; border-left: 5px solid {colores_udec['azul']};'>
        <h4 style='margin-top: 0; color: {colores_udec['azul']};'>{titulo}</h4>
        <p style='font-size: 24px; font-weight: bold; margin: 10px 0;'>Promedio: {promedio:.2f}</p>
        <p style='font-size: 18px; margin: 5px 0;'>Mínimo: {minimo:.2f}</p>
        <p style='font-size: 18px; margin: 5px 0;'>Máximo: {maximo:.2f}</p>
    </div>
    """, unsafe_allow_html=True)

def seccion_ingreso(datos_filtrados):
    """Sección 1: Análisis de Ingresos - LAYOUT VERTICAL"""
    st.header("Análisis de Ingresos")
    tabs = st.tabs(["Evolución", "Distribución", "Brechas"])
    
    with tabs[0]:
        st.subheader("Evolución Temporal de Ingresos")
        
        # GRÁFICO 1: Cantidad de Ingresos (ARRIBA)
        datos_ingresos_ev = datos_filtrados.groupby('año').agg({
            'ingresos_M':'sum', 
            'ingresos_H':'sum'
        }).reset_index()
        
        grafico1 = crear_grafico_lineas(
            datos_ingresos_ev, 'año', 
            ['ingresos_M', 'ingresos_H'],
            'Cantidad de Ingresos por Año', 
            'Cantidad de Estudiantes'
        )
        if grafico1:
            st.plotly_chart(grafico1, use_container_width=True)
        else:
            st.info("No hay datos de ingresos disponibles para mostrar")
        
        # GRÁFICO 2: Puntajes Promedio (ABAJO)
        datos_puntajes_ev = datos_filtrados.groupby('año').agg({
            'puntaje_M':'mean', 
            'puntaje_H':'mean'
        }).reset_index()
        
        grafico2 = crear_grafico_lineas(
            datos_puntajes_ev, 'año', 
            ['puntaje_M', 'puntaje_H'],
            'Puntajes Promedio por Año', 
            'Puntaje'
        )
        if grafico2:
            st.plotly_chart(grafico2, use_container_width=True)
        else:
            st.info("No hay datos de puntajes disponibles para mostrar")
    
    with tabs[1]:
        st.subheader("Distribución de Ingresos")
        
        # GRÁFICO 1: Distribución de Ingresos (ARRIBA)
        datos_ingresos = datos_filtrados.groupby('año').agg({
            'ingresos_M':'sum', 
            'ingresos_H':'sum'
        }).reset_index()
        
        grafico1 = crear_grafico_barras_apiladas(
            datos_ingresos, 'año', 
            ['ingresos_M', 'ingresos_H'],
            'Distribución de Ingresos por Género'
        )
        if grafico1:
            st.plotly_chart(grafico1, use_container_width=True)
        else:
            st.info("No hay datos disponibles para mostrar")
        
        # GRÁFICO 2: Comparación de Puntajes (ABAJO)
        datos_puntajes = datos_filtrados.groupby('año').agg({
            'puntaje_M':'mean', 
            'puntaje_H':'mean'
        }).reset_index()
        
        grafico2 = crear_grafico_barras_agrupadas(
            datos_puntajes, 'año', 
            ['puntaje_M', 'puntaje_H'],
            'Comparación de Puntajes Promedio por Género', 
            'Puntaje Promedio'
        )
        if grafico2:
            st.plotly_chart(grafico2, use_container_width=True)
        else:
            st.info("No hay datos disponibles para mostrar")
    
    with tabs[2]:
        st.subheader("Análisis de Brechas de Género")
        
        # GRÁFICO 1: Brecha de Ingresos (ARRIBA)
        grafico1 = crear_grafico_brecha(
            datos_filtrados, 
            'brecha_ingresos', 
            'Brecha de Ingresos (M - H)'
        )
        if grafico1:
            st.plotly_chart(grafico1, use_container_width=True)
        else:
            st.info("No hay datos de brecha de ingresos disponibles")
        
        # GRÁFICO 2: Brecha de Puntajes (ABAJO)
        grafico2 = crear_grafico_brecha(
            datos_filtrados, 
            'brecha_puntaje', 
            'Brecha de Puntajes (M - H)'
        )
        if grafico2:
            st.plotly_chart(grafico2, use_container_width=True)
        else:
            st.info("No hay datos de brecha de puntajes disponibles")

def seccion_riesgo(datos_filtrados):
    """Sección 2: Análisis de Riesgo de Abandono - LAYOUT VERTICAL"""
    st.header("Análisis de Riesgo de Abandono")
    
    # Evolución temporal - VERTICAL
    st.subheader("Evolución Temporal del Riesgo")
    
    # Riesgo Bajo
    grafico1 = crear_grafico_lineas(
        datos_filtrados, 'año', 
        ['riesgo_bajo_M', 'riesgo_bajo_H'],
        'Riesgo Bajo (%)', 
        'Porcentaje'
    )
    if grafico1:
        st.plotly_chart(grafico1, use_container_width=True)
    
    # Riesgo Medio
    grafico2 = crear_grafico_lineas(
        datos_filtrados, 'año', 
        ['riesgo_medio_M', 'riesgo_medio_H'],
        'Riesgo Medio (%)', 
        'Porcentaje'
    )
    if grafico2:
        st.plotly_chart(grafico2, use_container_width=True)
    
    # Riesgo Alto
    grafico3 = crear_grafico_lineas(
        datos_filtrados, 'año', 
        ['riesgo_alto_M', 'riesgo_alto_H'],
        'Riesgo Alto (%)', 
        'Porcentaje'
    )
    if grafico3:
        st.plotly_chart(grafico3, use_container_width=True)
    
    # Distribución general
    st.subheader("Distribución General del Riesgo")
    promedio_bajo = datos_filtrados[['riesgo_bajo_M', 'riesgo_bajo_H']].mean().mean()
    promedio_medio = datos_filtrados[['riesgo_medio_M', 'riesgo_medio_H']].mean().mean()
    promedio_alto = datos_filtrados[['riesgo_alto_M', 'riesgo_alto_H']].mean().mean()
    
    # Centrar el gráfico de dona
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        grafico = crear_grafico_dona(
            [promedio_bajo, promedio_medio, promedio_alto],
            ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto'],
            'Distribución Promedio Histórica'
        )
        st.plotly_chart(grafico, use_container_width=True)
    
    # Distribución por género - VERTICAL
    st.subheader("Distribución por Género")
    
    # Gráfico Mujeres (ARRIBA)
    bajo_m = datos_filtrados['riesgo_bajo_M'].mean()
    medio_m = datos_filtrados['riesgo_medio_M'].mean()
    alto_m = datos_filtrados['riesgo_alto_M'].mean()
    grafico_m = crear_grafico_dona(
        [bajo_m, medio_m, alto_m],
        ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto'],
        'Distribución - Mujeres', 
        genero='mujer'
    )
    st.plotly_chart(grafico_m, use_container_width=True)
    
    # Gráfico Hombres (ABAJO)
    bajo_h = datos_filtrados['riesgo_bajo_H'].mean()
    medio_h = datos_filtrados['riesgo_medio_H'].mean()
    alto_h = datos_filtrados['riesgo_alto_H'].mean()
    grafico_h = crear_grafico_dona(
        [bajo_h, medio_h, alto_h],
        ['Riesgo Bajo', 'Riesgo Medio', 'Riesgo Alto'],
        'Distribución - Hombres', 
        genero='hombre'
    )
    st.plotly_chart(grafico_h, use_container_width=True)
    
    # Análisis detallado
    st.subheader("Análisis Detallado por Nivel de Riesgo")
    tabs_nivel1 = st.tabs(["Comparación", "Solo Mujeres", "Solo Hombres"])
    
    for tab, filtro_genero in zip(tabs_nivel1, ['ambos', 'M', 'H']):
        with tab:
            tabs_nivel2 = st.tabs(["Riesgo Bajo", "Riesgo Medio", "Riesgo Alto"])
            for tab_nivel, nivel in zip(tabs_nivel2, ['bajo', 'medio', 'alto']):
                with tab_nivel:
                    mostrar_analisis_factores_por_riesgo(datos_filtrados, nivel, filtro_genero)

def mostrar_analisis_factores_por_riesgo(datos, nivel_riesgo, filtro_genero):
    """Muestra análisis detallado de factores por nivel de riesgo"""
    factores = ['motivacion', 'asistencia', 'participacion', 'autoconfianza']
    valores_por_factor = {}
    
    if filtro_genero == 'ambos':
        for factor in factores:
            columna_mujeres = f'{factor}_M_{nivel_riesgo}'
            columna_hombres = f'{factor}_H_{nivel_riesgo}'
            if columna_mujeres in datos.columns and columna_hombres in datos.columns:
                valores_por_factor[factor.capitalize()] = {
                    'Mujeres': datos[columna_mujeres].mean(),
                    'Hombres': datos[columna_hombres].mean()
                }
    elif filtro_genero == 'M':
        for factor in factores:
            columna = f'{factor}_M_{nivel_riesgo}'
            if columna in datos.columns:
                valores_por_factor[factor.capitalize()] = {'Mujeres': datos[columna].mean()}
    else:
        for factor in factores:
            columna = f'{factor}_H_{nivel_riesgo}'
            if columna in datos.columns:
                valores_por_factor[factor.capitalize()] = {'Hombres': datos[columna].mean()}
    
    if valores_por_factor:
        # Determinar modo para el radar
        if filtro_genero == 'ambos':
            modo = 'comparacion'
        elif filtro_genero == 'M':
            modo = 'mujeres'
        else:
            modo = 'hombres'
        
        grafico_radar = crear_grafico_radar(
            valores_por_factor,
            f'Factores Psicosociales - Riesgo {nivel_riesgo.capitalize()}',
            modo=modo
        )
        st.plotly_chart(grafico_radar, use_container_width=True)
        
        grafico_barras = crear_grafico_barras_horizontales(
            valores_por_factor, 
            'Comparación de Factores'
        )
        if grafico_barras:
            st.plotly_chart(grafico_barras, use_container_width=True)
        
        st.markdown("#### Estadísticas de Reprobaciones")
        if filtro_genero == 'ambos':
            col1, col2 = st.columns(2)
            with col1:
                prom_m = datos[f'repr_prom_M_{nivel_riesgo}'].mean()
                min_m = datos[f'repr_min_M_{nivel_riesgo}'].mean()
                max_m = datos[f'repr_max_M_{nivel_riesgo}'].mean()
                mostrar_card_reprobaciones('Mujeres', prom_m, min_m, max_m)
            with col2:
                prom_h = datos[f'repr_prom_H_{nivel_riesgo}'].mean()
                min_h = datos[f'repr_min_H_{nivel_riesgo}'].mean()
                max_h = datos[f'repr_max_H_{nivel_riesgo}'].mean()
                mostrar_card_reprobaciones('Hombres', prom_h, min_h, max_h)
        elif filtro_genero == 'M':
            prom_m = datos[f'repr_prom_M_{nivel_riesgo}'].mean()
            min_m = datos[f'repr_min_M_{nivel_riesgo}'].mean()
            max_m = datos[f'repr_max_M_{nivel_riesgo}'].mean()
            mostrar_card_reprobaciones('Mujeres', prom_m, min_m, max_m)
        else:
            prom_h = datos[f'repr_prom_H_{nivel_riesgo}'].mean()
            min_h = datos[f'repr_min_H_{nivel_riesgo}'].mean()
            max_h = datos[f'repr_max_H_{nivel_riesgo}'].mean()
            mostrar_card_reprobaciones('Hombres', prom_h, min_h, max_h)
    else:
        st.info("No hay datos disponibles para este nivel de riesgo")

def seccion_egreso(datos_filtrados):
    """Sección 3: Análisis de Egresos - LAYOUT VERTICAL"""
    st.header("Análisis de Egresos")
    tabs = st.tabs(["Evolución", "Distribución", "Brechas"])
    
    with tabs[0]:
        st.subheader("Evolución Temporal de Titulaciones")
        
        # Gráfico de líneas
        grafico = crear_grafico_lineas(
            datos_filtrados, 'año', 
            ['titulaciones_M', 'titulaciones_H'],
            'Titulaciones por Año', 
            'Cantidad de Titulados'
        )
        if grafico:
            st.plotly_chart(grafico, use_container_width=True)
        else:
            st.info("No hay datos de titulaciones disponibles")
        
        # Métricas debajo del gráfico
        col1, col2, col3 = st.columns(3)
        with col1:
            promedio_mujeres = datos_filtrados['titulaciones_M'].mean()
            st.metric("Promedio Histórico Mujeres", f"{promedio_mujeres:.1f}")
        with col2:
            promedio_hombres = datos_filtrados['titulaciones_H'].mean()
            st.metric("Promedio Histórico Hombres", f"{promedio_hombres:.1f}")
        with col3:
            promedio_total = datos_filtrados['total_titulaciones'].mean()
            st.metric("Promedio Total", f"{promedio_total:.1f}")
    
    with tabs[1]:
        st.subheader("Distribución de Titulaciones")
        grafico = crear_grafico_barras_apiladas(
            datos_filtrados, 'año', 
            ['titulaciones_M', 'titulaciones_H'],
            'Distribución de Titulaciones por Género'
        )
        if grafico:
            st.plotly_chart(grafico, use_container_width=True)
        else:
            st.info("No hay datos disponibles")
    
    with tabs[2]:
        st.subheader("Brecha de Titulaciones")
        grafico = crear_grafico_brecha(
            datos_filtrados, 
            'brecha_titulaciones', 
            'Brecha de Titulaciones (M - H)'
        )
        if grafico:
            st.plotly_chart(grafico, use_container_width=True)
        else:
            st.info("No hay datos de brecha disponibles")

def aplicacion_principal():
    """Aplicación principal después del login"""
    st.title("Sistema de Análisis de Brechas de Género en Ingeniería")
    st.markdown(f"**Usuario:** {st.session_state.usuario} | **Rol:** {st.session_state.rol}")
    
    # Cargar datos
    datos = cargar_datos()
    if datos is None:
        return
    
    # Sidebar con filtros
    with st.sidebar:
        st.header("Filtros")
        carreras_permitidas = obtener_carreras_permitidas(st.session_state.rol)
        if st.session_state.rol == "admin":
            carrera_seleccionada = st.selectbox("Seleccionar Carrera", options=['Todas'] + carreras_permitidas)
        else:
            carrera_seleccionada = st.selectbox("Carrera", options=carreras_permitidas, disabled=True)
        st.markdown("---")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            st.rerun()
    
    # Filtrar datos por carrera
    datos_filtrados = datos.copy()
    if carrera_seleccionada != 'Todas' and st.session_state.rol == "admin":
        datos_filtrados = datos_filtrados[datos_filtrados['carrera'] == carrera_seleccionada]
    elif st.session_state.rol != "admin":
        datos_filtrados = datos_filtrados[datos_filtrados['carrera'] == carrera_seleccionada]
    
    if len(datos_filtrados) == 0:
        st.warning("No hay datos disponibles para los filtros seleccionados")
        return
    
    # Mostrar las 3 secciones
    st.markdown("---")
    seccion_ingreso(datos_filtrados)
    st.markdown("---")
    seccion_riesgo(datos_filtrados)
    st.markdown("---")
    seccion_egreso(datos_filtrados)

# Inicializar estado de sesión
if 'autenticado' not in st.session_state:
    st.session_state.autenticado = False
    st.session_state.usuario = None
    st.session_state.rol = None

# Mostrar login o aplicación principal
if not st.session_state.autenticado:
    pagina_login()
else:
    aplicacion_principal()
