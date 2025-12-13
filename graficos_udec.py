import pandas as pd
import numpy as np

cuestionario = pd.read_csv('data/cuestionario_original.csv', sep=',', encoding='utf-8')
egresos = pd.read_csv('data/egresados_original.csv', sep=';', encoding='latin-1')
ingresos = pd.read_csv('data/ingresos_original.csv', sep=';', encoding='utf-8', skiprows=3)

diccionario = {
    3309: 'Ingeniería Civil Industrial', 
    3310: 'Ingeniería Civil', 
    3311: 'Ingeniería Civil Eléctrica',
    3318: 'Ingeniería Civil Electrónica',
    3319: 'Ingeniería Civil Informática',
    13072.0: 'Ingeniería Civil Industrial', 
    13069.0: 'Ingeniería Civil',
    13070.0: 'Ingeniería Civil Eléctrica', 
    13071.0: 'Ingeniería Civil Electrónica',
    13073.0: 'Ingeniería Civil Informática',
    'Masculino': 'H', 
    'Femenino': 'M', 
    'MASCULINO': 'H', 
    'FEMENINO': 'M',
    'INGENIERIA CIVIL INDUSTRIAL': 'Ingeniería Civil Industrial',
    'INGENIERIA CIVIL': 'Ingeniería Civil',
    'INGENIERIA CIVIL ELECTRICA': 'Ingeniería Civil Eléctrica',
    'INGENIERIA CIVIL ELECTRONICA': 'Ingeniería Civil Electrónica',
    'INGENIERIA CIVIL INFORMATICA': 'Ingeniería Civil Informática'}

lista_carreras_validas = ['Ingeniería Civil Industrial', 'Ingeniería Civil', 'Ingeniería Civil Eléctrica','Ingeniería Civil Electrónica', 'Ingeniería Civil Informática']

def filtrar_carreras(df, columna_carrera):
    return df[df[columna_carrera].isin(lista_carreras_validas)]
def filtrar_genero(df, columna_genero):
    return df[df[columna_genero].isin(['H', 'M'])]
def clasificar_riesgo(valor):
    if valor == 1:
        return "Bajo"
    elif valor in [2, 3]:
        return "Medio"
    elif valor in [4, 5]:
        return "Alto"
    else:
        return None

cuestionario = cuestionario.iloc[:, np.r_[0, 2:16, 71]]
cuestionario.columns = [ 'carrera', 'año_ingreso', 'genero', 'reprobaciones', 'asistencia',
  'motivacion', 'participacion', 'autoconfianza_1', 'autoconfianza_2', 'autoconfianza_3',
    'autoconfianza_4', 'autoconfianza_5', 'autoconfianza_6', 'autoconfianza_7', 'autoconfianza_8', 'intencion_abandono']
cuestionario['autoconfianza'] = (cuestionario.loc[:, 'autoconfianza_1':'autoconfianza_8'].mean(axis=1) + 0.5).astype(int)
cuestionario = cuestionario.replace(diccionario)
cuestionario = cuestionario[cuestionario['año_ingreso'] != 'Antes de 2015']
cuestionario['año_ingreso'] = cuestionario['año_ingreso'].astype(int)
cuestionario = filtrar_genero(cuestionario, 'genero')
cuestionario = filtrar_carreras(cuestionario, 'carrera')
cuestionario['riesgo'] = cuestionario['intencion_abandono'].apply(clasificar_riesgo)

ingresos = ingresos.iloc[:, np.r_[1:4, 9]]
ingresos.columns = ['carrera', 'año_ingreso', 'genero', 'puntaje_ingreso']
ingresos = ingresos.replace(diccionario)
ingresos = filtrar_genero(ingresos, 'genero')
ingresos = filtrar_carreras(ingresos, 'carrera')
ingresos['puntaje_ingreso'] = ingresos['puntaje_ingreso'].astype(str).str.replace(',', '.').astype(float).astype(int)
ingresos['año_ingreso'] = ingresos['año_ingreso'].astype(int)

egresos = egresos[egresos['NOMBRE INSTITUCIÓN'] == 'UNIVERSIDAD DE CONCEPCION'].iloc[:, np.r_[0,1,2,3,14]]
egresos.columns = ['año_egreso', 'total_titulaciones', 'titulaciones_mujeres', 'titulaciones_hombres', 'carrera']
egresos = egresos.replace(diccionario)
egresos = filtrar_carreras(egresos, 'carrera')
egresos['año_egreso'] = egresos['año_egreso'].astype(str).str.replace('TIT_', '').astype(int)
egresos['titulaciones_mujeres'] = egresos['titulaciones_mujeres'].astype(float).round().astype('Int64').fillna(0)
egresos['titulaciones_hombres'] = egresos['titulaciones_hombres'].astype(float).round().astype('Int64').fillna(0)


agrupacion_ingresos = ingresos.groupby(['año_ingreso', 'carrera', 'genero']).agg(
    promedio_puntaje_ingreso=('puntaje_ingreso', 'mean'),
    contador_ingresos=('puntaje_ingreso', 'count')).reset_index()
agrupacion_ingresos = agrupacion_ingresos.rename(columns={'año_ingreso': 'año'})
agrupacion_ingresos['promedio_puntaje_ingreso'] = agrupacion_ingresos['promedio_puntaje_ingreso'].round(2)
pivot_ingresos = agrupacion_ingresos.pivot_table(
    index=['año', 'carrera'], columns='genero', 
    values=['contador_ingresos', 'promedio_puntaje_ingreso']).reset_index()
pivot_ingresos.columns = ['año', 'carrera', 'ingresos_H', 'ingresos_M', 'puntaje_H', 'puntaje_M']
pivot_ingresos['ingresos_H'] = pivot_ingresos['ingresos_H'].fillna(0).astype(int)
pivot_ingresos['ingresos_M'] = pivot_ingresos['ingresos_M'].fillna(0).astype(int)
pivot_ingresos.loc[pivot_ingresos['ingresos_M'] == 0, 'puntaje_M'] = np.nan
pivot_ingresos.loc[pivot_ingresos['ingresos_H'] == 0, 'puntaje_H'] = np.nan
pivot_ingresos['total_ingresos'] = pivot_ingresos['ingresos_M'] + pivot_ingresos['ingresos_H']
pivot_ingresos['brecha_ingresos'] = pivot_ingresos['ingresos_M'] - pivot_ingresos['ingresos_H']
pivot_ingresos['brecha_puntaje'] = (pivot_ingresos['puntaje_M'] - pivot_ingresos['puntaje_H']).round(2)

agrupacion_egresos = egresos.groupby(['año_egreso', 'carrera']).agg(
    suma_titulaciones_mujeres=('titulaciones_mujeres', 'sum'),
    suma_titulaciones_hombres=('titulaciones_hombres', 'sum'),
    suma_total_titulaciones=('total_titulaciones', 'sum')).reset_index()
agrupacion_egresos['brecha_titulaciones'] = agrupacion_egresos['suma_titulaciones_mujeres'] - agrupacion_egresos['suma_titulaciones_hombres']
pivot_egresos = agrupacion_egresos.rename(columns={'año_egreso': 'año', 'suma_titulaciones_hombres': 'titulaciones_H', 'suma_titulaciones_mujeres': 'titulaciones_M'})

agrupacion_factores = cuestionario.groupby(['año_ingreso','carrera','genero']).agg(
    promedio_motivacion=('motivacion', 'mean'),
    promedio_asistencia=('asistencia', 'mean'),
    promedio_participacion=('participacion', 'mean'),
    promedio_autoconfianza=('autoconfianza', 'mean')).reset_index()
pivot_factores = agrupacion_factores.pivot_table(
    index=['año_ingreso','carrera'], columns='genero',
    values=['promedio_motivacion','promedio_asistencia','promedio_participacion','promedio_autoconfianza']).reset_index()
pivot_factores.columns = [
    'año', 'carrera', 'asistencia_H', 'asistencia_M', 'autoconfianza_H', 'autoconfianza_M',
    'motivacion_H', 'motivacion_M', 'participacion_H', 'participacion_M']
for nombre_columna_redondear in [
    'asistencia_H', 'asistencia_M', 'autoconfianza_H', 'autoconfianza_M',
    'motivacion_H', 'motivacion_M', 'participacion_H', 'participacion_M']:
    pivot_factores[nombre_columna_redondear] = pivot_factores[nombre_columna_redondear].round(2)
pivot_factores['brecha_motivacion'] = (pivot_factores['motivacion_M'] - pivot_factores['motivacion_H']).round(2)
pivot_factores['brecha_asistencia'] = (pivot_factores['asistencia_M'] - pivot_factores['asistencia_H']).round(2)
pivot_factores['brecha_participacion'] = (pivot_factores['participacion_M'] - pivot_factores['participacion_H']).round(2)
pivot_factores['brecha_autoconfianza'] = (pivot_factores['autoconfianza_M'] - pivot_factores['autoconfianza_H']).round(2)

agrupacion_reprobaciones = cuestionario.groupby(['año_ingreso', 'carrera', 'genero']).agg(
    promedio_reprobaciones=('reprobaciones','mean'),
    min_reprobaciones=('reprobaciones','min'),
    max_reprobaciones=('reprobaciones','max')).reset_index()
agrupacion_reprobaciones = agrupacion_reprobaciones.rename(columns={'año_ingreso':'año'})
pivot_reprobaciones = agrupacion_reprobaciones.pivot_table(
    index=['año', 'carrera'], columns='genero',
    values=['promedio_reprobaciones', 'min_reprobaciones', 'max_reprobaciones']).reset_index()
pivot_reprobaciones.columns = [
    'año', 'carrera', 'repr_prom_H', 'repr_prom_M', 'repr_min_H', 'repr_min_M', 'repr_max_H', 'repr_max_M']
for nombre_col in ['repr_prom_H', 'repr_prom_M', 'repr_min_H', 'repr_min_M', 'repr_max_H', 'repr_max_M']:
    pivot_reprobaciones[nombre_col] = pivot_reprobaciones[nombre_col].round(2)
pivot_reprobaciones['brecha_reprobaciones'] = (pivot_reprobaciones['repr_prom_M'] - pivot_reprobaciones['repr_prom_H']).round(2)

tabla_riesgo = cuestionario.groupby(['año_ingreso', 'carrera', 'genero', 'riesgo']).size().reset_index(name='conteo_riesgo')
pivot_riesgo_genero = tabla_riesgo.pivot_table(
    index=['año_ingreso','carrera','genero'], columns='riesgo', values='conteo_riesgo', fill_value=0).reset_index()
if 'Bajo' in pivot_riesgo_genero.columns and 'Medio' in pivot_riesgo_genero.columns and 'Alto' in pivot_riesgo_genero.columns:
    total_riesgo = pivot_riesgo_genero['Bajo'] + pivot_riesgo_genero['Medio'] + pivot_riesgo_genero['Alto']
    pivot_riesgo_genero['bajo_pct'] = (pivot_riesgo_genero['Bajo'] / total_riesgo * 100).round(2)
    pivot_riesgo_genero['medio_pct'] = (pivot_riesgo_genero['Medio'] / total_riesgo * 100).round(2)
    pivot_riesgo_genero['alto_pct'] = (pivot_riesgo_genero['Alto'] / total_riesgo * 100).round(2)
tabla_riesgo_genero = pivot_riesgo_genero.pivot_table(
    index=['año_ingreso','carrera'], columns='genero', values=['bajo_pct','medio_pct','alto_pct']).reset_index()
tabla_riesgo_genero.columns = [
    'año', 'carrera', 'riesgo_alto_H', 'riesgo_alto_M', 'riesgo_bajo_H', 'riesgo_bajo_M', 'riesgo_medio_H', 'riesgo_medio_M']

factores_por_riesgo = cuestionario.groupby(['año_ingreso','carrera','genero','riesgo']).agg(
    promedio_motivacion=('motivacion', 'mean'),
    promedio_asistencia=('asistencia', 'mean'),
    promedio_participacion=('participacion', 'mean'),
    promedio_autoconfianza=('autoconfianza', 'mean'),
    promedio_reprobaciones=('reprobaciones', 'mean'),
    min_reprobaciones=('reprobaciones', 'min'),
    max_reprobaciones=('reprobaciones', 'max')).reset_index()
factores_por_riesgo = factores_por_riesgo.rename(columns={'año_ingreso':'año'})
pivot_factores_riesgo = factores_por_riesgo.pivot_table(
    index=['año', 'carrera', 'riesgo'], columns='genero',
    values=[
        'promedio_motivacion','promedio_asistencia','promedio_participacion','promedio_autoconfianza',
        'promedio_reprobaciones','min_reprobaciones','max_reprobaciones']).reset_index()
pivot_factores_riesgo.columns = [
    'año', 'carrera', 'riesgo', 'asistencia_H', 'asistencia_M', 'autoconfianza_H', 'autoconfianza_M',
    'motivacion_H', 'motivacion_M', 'participacion_H', 'participacion_M', 'repr_prom_H', 'repr_prom_M',
    'repr_min_H', 'repr_min_M', 'repr_max_H', 'repr_max_M']
for nombre_columna_factor in [
    'asistencia_H', 'asistencia_M', 'autoconfianza_H', 'autoconfianza_M',
    'motivacion_H', 'motivacion_M', 'participacion_H', 'participacion_M',
    'repr_prom_H', 'repr_prom_M', 'repr_min_H', 'repr_min_M', 'repr_max_H', 'repr_max_M']:
    pivot_factores_riesgo[nombre_columna_factor] = pivot_factores_riesgo[nombre_columna_factor].round(2)
pivot_factores_riesgo_bajo = pivot_factores_riesgo[pivot_factores_riesgo['riesgo'] == 'Bajo'].drop('riesgo', axis=1)
pivot_factores_riesgo_bajo.columns = ['año', 'carrera'] + [f'{col}_bajo' for col in pivot_factores_riesgo_bajo.columns[2:]]
pivot_factores_riesgo_medio = pivot_factores_riesgo[pivot_factores_riesgo['riesgo'] == 'Medio'].drop('riesgo', axis=1)
pivot_factores_riesgo_medio.columns = ['año', 'carrera'] + [f'{col}_medio' for col in pivot_factores_riesgo_medio.columns[2:]]
pivot_factores_riesgo_alto = pivot_factores_riesgo[pivot_factores_riesgo['riesgo'] == 'Alto'].drop('riesgo', axis=1)
pivot_factores_riesgo_alto.columns = ['año', 'carrera'] + [f'{col}_alto' for col in pivot_factores_riesgo_alto.columns[2:]]

lista_años_completos = sorted(set(pivot_ingresos['año'].tolist() + pivot_egresos['año'].tolist() + cuestionario['año_ingreso'].tolist()))
lista_carreras_completas = sorted(set(ingresos['carrera'].tolist() + egresos['carrera'].tolist() + cuestionario['carrera'].tolist()))
base_maestra = pd.DataFrame([{'año': año_individual, 'carrera': carrera_individual} for año_individual in lista_años_completos for carrera_individual in lista_carreras_completas])
base_maestra = base_maestra.merge(pivot_ingresos, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_egresos, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_factores, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_reprobaciones, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(tabla_riesgo_genero, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_factores_riesgo_bajo, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_factores_riesgo_medio, on=['año', 'carrera'], how='outer')
base_maestra = base_maestra.merge(pivot_factores_riesgo_alto, on=['año', 'carrera'], how='outer')

conjunto_entradas_cuestionario = set(zip(cuestionario['año_ingreso'], cuestionario['carrera']))
conjunto_entradas_ingresos = set(zip(ingresos['año_ingreso'], ingresos['carrera']))
conjunto_entradas_egresos = set(zip(egresos['año_egreso'], egresos['carrera']))

def poner_nan_si_no_hay_original(fila):
    combinacion_ac = (fila['año'], fila['carrera'])
    if combinacion_ac not in conjunto_entradas_cuestionario:
        columnas_cuestionario = [
            'motivacion_M', 'motivacion_H', 'asistencia_M', 'asistencia_H', 'participacion_M', 'participacion_H',
            'autoconfianza_M', 'autoconfianza_H', 'repr_prom_M', 'repr_prom_H', 'repr_min_M', 'repr_min_H',
            'repr_max_M', 'repr_max_H', 'brecha_reprobaciones', 'riesgo_alto_M', 'riesgo_alto_H',
            'riesgo_bajo_M', 'riesgo_bajo_H', 'riesgo_medio_M', 'riesgo_medio_H', 'brecha_motivacion',
            'brecha_asistencia', 'brecha_participacion', 'brecha_autoconfianza']
        for riesgo_nivel in ['bajo', 'medio', 'alto']:
            for factor_col in ['asistencia', 'autoconfianza', 'motivacion', 'participacion', 'repr_prom', 'repr_min', 'repr_max']:
                columnas_cuestionario.extend([f'{factor_col}_H_{riesgo_nivel}', f'{factor_col}_M_{riesgo_nivel}'])
        for columna in columnas_cuestionario:
            if columna in fila.index: fila[columna] = np.nan
    if combinacion_ac not in conjunto_entradas_ingresos:
        for columna in ['puntaje_M', 'puntaje_H', 'ingresos_M', 'ingresos_H', 'brecha_ingresos', 'brecha_puntaje', 'total_ingresos']:
            if columna in fila.index: fila[columna] = np.nan
    if combinacion_ac not in conjunto_entradas_egresos:
        for columna in ['titulaciones_M', 'titulaciones_H', 'total_titulaciones', 'brecha_titulaciones']:
            if columna in fila.index: fila[columna] = np.nan
    return fila

base_maestra = base_maestra.apply(poner_nan_si_no_hay_original, axis=1).sort_values(['carrera', 'año']).reset_index(drop=True)
base_maestra.to_csv('data/base_maestra.csv', index=False)

