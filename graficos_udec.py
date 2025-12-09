import plotly.graph_objects as go
import pandas as pd

# ==========================================
# COLORES UdeC
# ==========================================
colores_udec = {
    'azul': '#003DA5',
    'amarillo': '#e69b0a',
    'gris': '#a0a0a0',
    'rojo': '#d21428',
    'mujer': '#E91E63',           # Rosa intenso
    'hombre': '#1976D2',          # Azul
    'mujer_claro': '#F8BBD0',
    'mujer_medio': '#F06292',
    'mujer_oscuro': '#C2185B',
    'hombre_claro': '#BBDEFB',
    'hombre_medio': '#64B5F6',
    'hombre_oscuro': '#1565C0',
    'brecha': '#FF9800',          # Naranja
    'verde': '#66BB6A',           # Riesgo Bajo
    'amarillo_riesgo': '#FFA726', # Riesgo Medio
    'rojo_riesgo': '#EF5350'      # Riesgo Alto
}

# ==========================================
# GRÁFICOS DE LÍNEAS (EVOLUCIÓN)
# ==========================================

def crear_grafico_lineas(datos, col_x, cols_y, titulo, etiq_y):
    """
    Crea gráfico de líneas moderno estilo UdeC
    Similar al gráfico de Análisis Histórico
    """
    # Filtrar datos para eliminar años sin información
    datos_filtrados = datos.copy()
    # Eliminar filas donde todas las columnas Y son 0 o NaN
    mask = datos_filtrados[cols_y].sum(axis=1) > 0
    datos_filtrados = datos_filtrados[mask]
    
    if datos_filtrados.empty:
        return None
    
    fig = go.Figure()
    
    for col in cols_y:
        # Determinar nombre y color
        if col.endswith('_M') or 'mujeres' in col.lower() or col in ['puntaje_M', 'ingresos_M', 'titulaciones_M']:
            nombre = 'Mujeres'
            color = colores_udec['mujer']
        else:
            nombre = 'Hombres'
            color = colores_udec['hombre']
        
        fig.add_trace(go.Scatter(
            x=datos_filtrados[col_x],
            y=datos_filtrados[col],
            mode='lines+markers',
            name=nombre,
            line=dict(color=color, width=3),
            marker=dict(size=8, color='white', line=dict(width=2, color=color))
        ))
    
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title="Año",
        yaxis_title=etiq_y,
        plot_bgcolor='white',
        hovermode="x unified",
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        margin=dict(t=60, b=60, l=60, r=40),
        xaxis=dict(
            showgrid=False, 
            tickangle=0,  # Años horizontales
            tickmode='linear',
            dtick=1
        ),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400
    )
    
    return fig

# ==========================================
# GRÁFICOS DE BARRAS HORIZONTALES (DISTRIBUCIÓN)
# ==========================================

def crear_grafico_barras_apiladas(datos, col_x, cols_y, titulo):
    """
    Crea gráfico de barras horizontales apiladas
    Similar al gráfico de Distribución de Puntajes
    """
    # Filtrar datos para eliminar años sin información
    datos_filtrados = datos.copy()
    mask = datos_filtrados[cols_y].sum(axis=1) > 0
    datos_filtrados = datos_filtrados[mask]
    
    if datos_filtrados.empty:
        return None
    
    # Ordenar datos por año descendente para visualización
    datos_sorted = datos_filtrados.sort_values(col_x, ascending=False).copy()
    
    fig = go.Figure()
    
    for col in cols_y:
        if col.endswith('_M') or 'mujeres' in col.lower() or col in ['puntaje_M', 'ingresos_M', 'titulaciones_M']:
            nombre = 'Mujeres'
            color = colores_udec['mujer']
        else:
            nombre = 'Hombres'
            color = colores_udec['hombre']
        
        fig.add_trace(go.Bar(
            y=datos_sorted[col_x].astype(str),
            x=datos_sorted[col],
            name=nombre,
            orientation='h',
            marker=dict(color=color),
            text=datos_sorted[col].round(0).astype(int),
            textposition='auto'
        ))
    
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        barmode='stack',
        plot_bgcolor='white',
        legend=dict(orientation="h", y=-0.15, x=0.5, xanchor="center"),
        xaxis=dict(showticklabels=False),
        margin=dict(t=60, b=60, l=60, r=40),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400
    )
    
    return fig

# ==========================================
# GRÁFICO DE BRECHA
# ==========================================

def crear_grafico_brecha(datos, col_brecha, titulo):
    """
    Crea gráfico de línea para mostrar brechas de género
    Similar al gráfico de Brecha de Género
    """
    # Filtrar datos para eliminar años sin información
    datos_filtrados = datos[datos[col_brecha].notna()].copy()
    
    if datos_filtrados.empty:
        return None
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=datos_filtrados['año'],
        y=datos_filtrados[col_brecha],
        mode='lines+markers',
        name='Brecha (M - H)',
        line=dict(color=colores_udec['brecha'], width=3, shape='spline'),
        marker=dict(size=8, color=colores_udec['brecha'])
    ))
    
    fig.add_hline(
        y=0,
        line_dash="dash",
        line_color="gray",
        annotation_text="Equilibrio"
    )
    
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title="Año",
        yaxis_title="Diferencia",
        plot_bgcolor='white',
        hovermode="x unified",
        margin=dict(t=60, b=60, l=60, r=40),
        xaxis=dict(
            showgrid=False, 
            tickangle=0,  # Años horizontales
            tickmode='linear',
            dtick=1
        ),
        yaxis=dict(showgrid=True, gridcolor='#f0f0f0'),
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        height=400
    )
    
    return fig

# ==========================================
# GRÁFICOS DE DONA
# ==========================================

def crear_grafico_dona(valores, etiquetas, titulo, genero=None):
    """
    Crea gráfico de dona moderno
    Similar a los gráficos de Distribución de Riesgo
    """
    # paleta de colores según el género
    if genero == 'mujer':
        colores = [colores_udec['mujer_claro'], colores_udec['mujer_medio'], colores_udec['mujer_oscuro']]
    elif genero == 'hombre':
        colores = [colores_udec['hombre_claro'], colores_udec['hombre_medio'], colores_udec['hombre_oscuro']]
    else:
        # Colores para gráfico general
        colores = [colores_udec['verde'], colores_udec['amarillo_riesgo'], colores_udec['rojo_riesgo']]
    
    fig = go.Figure(data=[go.Pie(
        labels=etiquetas,
        values=valores,
        hole=0.6,
        marker_colors=colores,
        textinfo='percent+label',
        textposition='outside'
    )])
    
    fig.update_layout(
        title={
            'text': f"<b>{titulo}</b>",
            'y': 0.95,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        showlegend=False,
        margin=dict(t=50, b=80, l=40, r=40),
        height=400,
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul'])
    )
    
    return fig

# ==========================================
# GRÁFICO RADAR
# ==========================================

def crear_grafico_radar(vals, titulo, modo='comparacion'):
    """
    Crea gráfico de radar para análisis psicosocial
    Similar al Perfil Psicosocial por nivel de riesgo
    
    vals: dict con estructura {Factor: {'Mujeres': val, 'Hombres': val}}
    modo: 'comparacion', 'mujeres', 'hombres'
    """
    categorias = list(vals.keys())
    
    fig = go.Figure()
    
    # Extraer valores según modo
    if 'Mujeres' in vals.get(categorias[0], {}):
        vals_m = [vals[c].get('Mujeres', 0) for c in categorias]
        vals_h = [vals[c].get('Hombres', 0) for c in categorias]
        
        if modo in ['comparacion', 'hombres']:
            fig.add_trace(go.Scatterpolar(
                r=vals_h,
                theta=categorias,
                fill='toself',
                name='Hombres',
                line_color=colores_udec['hombre'],
                opacity=0.7
            ))
        
        if modo in ['comparacion', 'mujeres']:
            fig.add_trace(go.Scatterpolar(
                r=vals_m,
                theta=categorias,
                fill='toself',
                name='Mujeres',
                line_color=colores_udec['mujer'],
                opacity=0.7
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 5]
            )
        ),
        showlegend=True,
        title=dict(
            text=f"<b>{titulo}</b>",
            x=0.5,
            xanchor='center'
        ),
        margin=dict(t=80, b=40, l=40, r=40),
        height=450,
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul'])
    )
    
    return fig

# ==========================================
# GRÁFICO DE BARRAS HORIZONTALES
# ==========================================

def crear_grafico_barras_horizontales(vals, titulo):
    """
    Crea gráfico de barras horizontales agrupadas
    Para comparación de factores
    """
    categorias = list(vals.keys())
    
    if not categorias or 'Mujeres' not in vals.get(categorias[0], {}):
        return None
    
    vals_m = [vals[c].get('Mujeres', 0) for c in categorias]
    vals_h = [vals[c].get('Hombres', 0) for c in categorias]
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        y=categorias,
        x=vals_m,
        name='Mujeres',
        orientation='h',
        marker_color=colores_udec['mujer']
    ))
    
    fig.add_trace(go.Bar(
        y=categorias,
        x=vals_h,
        name='Hombres',
        orientation='h',
        marker_color=colores_udec['hombre']
    ))
    
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title='Valor',
        yaxis_title='Factor',
        plot_bgcolor='white',
        barmode='group',
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        margin=dict(t=60, b=40, l=40, r=40),
        height=350
    )
    
    fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    
    return fig

# ==========================================
# GRÁFICO DE BARRAS AGRUPADAS
# ==========================================

def crear_grafico_barras_agrupadas(datos, col_x, cols_y, titulo, etiq_y):
    """
    Crea gráfico de barras verticales agrupadas
    Para comparaciones por año
    """
    # Filtrar datos para eliminar años sin información
    datos_filtrados = datos.copy()
    mask = datos_filtrados[cols_y].sum(axis=1) > 0
    datos_filtrados = datos_filtrados[mask]
    
    if datos_filtrados.empty:
        return None
    
    fig = go.Figure()
    
    for col in cols_y:
        if col.endswith('_M') or 'mujeres' in col.lower() or col in ['puntaje_M', 'ingresos_M', 'titulaciones_M']:
            nombre = 'Mujeres'
            color = colores_udec['mujer']
        else:
            nombre = 'Hombres'
            color = colores_udec['hombre']
        
        fig.add_trace(go.Bar(
            x=datos_filtrados[col_x],
            y=datos_filtrados[col],
            name=nombre,
            marker_color=color
        ))
    
    fig.update_layout(
        title=f"<b>{titulo}</b>",
        xaxis_title='Año',
        yaxis_title=etiq_y,
        barmode='group',
        plot_bgcolor='white',
        font=dict(family='Roboto', size=12),
        title_font=dict(family='Poppins', size=16, color=colores_udec['azul']),
        margin=dict(t=60, b=60, l=60, r=40),
        height=400
    )
    
    fig.update_xaxes(
        showgrid=True, 
        gridwidth=1, 
        gridcolor='#e0e0e0',
        tickangle=0,  # Años horizontales
        tickmode='linear',
        dtick=1
    )
    fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='#e0e0e0')
    
    return fig

    
    
    