import os
import folium
import pandas as pd
import plotly.express as px
import requests
import streamlit as st
from streamlit_folium import st_folium

# -----------------------------------------------------------------------------
# PALETA DE COLORES OFICIAL COOPI / INTEGRAS
# -----------------------------------------------------------------------------
COLOR_AZUL_COOPI = '#0072CE'
COLOR_VERDE_COOPI = '#28A745'
COLOR_AGUAMARINA = '#17C3B2'
COLOR_ROSADO_AAP = '#D89FE3'
COLOR_AMARILLO_MOSTAZA = '#E5B130'

PALETA_COOPI = [
    COLOR_AZUL_COOPI,
    COLOR_VERDE_COOPI,
    COLOR_AGUAMARINA,
    COLOR_ROSADO_AAP,
    COLOR_AMARILLO_MOSTAZA,
    '#08327D',
]

# -----------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title='Tablero INTEGRAS | COOPI Venezuela',
    layout='wide',
    initial_sidebar_state='expanded',
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@700;800&family=Quicksand:wght@600;700&display=swap');

    html, body, [class*="css"], .stMarkdown, p, div, span, label, input, button {
        font-family: 'Quicksand', sans-serif !important;
        font-weight: 700 !important;
    }

    h1, h2, h3, h4, h5, h6, .stSubheader {
        font-family: 'Montserrat', sans-serif !important;
        font-weight: 700 !important;
    }

    .titulo-principal {
        font-family: 'Montserrat', sans-serif !important;
        color: #0072CE !important;
        margin-bottom: 5px !important;
        font-weight: 800 !important;
        font-size: 1.55rem !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# -----------------------------------------------------------------------------
# ENCABEZADO CON TÍTULO Y LOGO
# -----------------------------------------------------------------------------
col_header_title, col_header_logo = st.columns([3, 1])

with col_header_title:
    st.markdown(
        "<h1 class='titulo-principal'>Tablero de Monitoreo Proyecto INTEGRAS – "
        'Respuesta integrada en materia de protección, salud, nutrición y '
        'WASH para poblaciones vulnerables</h1>',
        unsafe_allow_html=True,
    )

with col_header_logo:
    posibles_nombres = [
        'AICS.LOGO.jpg',
        'aics.logo.jpg',
        'AICS.LOGO.png',
        'coopi.jpg',
        'coopi.jpeg',
        'COOPI.jpg',
        'coopi.png',
        'COOPI.png',
        'integras.png',
        'integras.jpg',
        'INTEGRAS.png',
    ]
    logo_path = next((n for n in posibles_nombres if os.path.exists(n)), None)

    if not logo_path:
        imagenes_repo = [
            f for f in os.listdir('.')
            if f.lower().endswith(('.jpg', '.jpeg', '.png'))
        ]
        if imagenes_repo:
            logo_path = imagenes_repo[0]

    if logo_path:
        try:
            st.image(logo_path, width='stretch')
        except TypeError:
            st.image(logo_path, use_container_width=True)
    else:
        st.warning('⚠️ No se encontró la imagen del logo en el repositorio.')

st.markdown('---')

# -----------------------------------------------------------------------------
# CONFIGURACIÓN DE CONEXIÓN KOBOTOOLBOX API V2
# -----------------------------------------------------------------------------
KOBO_SERVER = 'https://eu.kobotoolbox.org'
FORM_UID = 'aN3EQDFths7wXuRksh4Mdm'

try:
    KOBO_API_TOKEN = st.secrets['KOBO_TOKEN']
except Exception:
    KOBO_API_TOKEN = 'eb8497fd084a4fb456a5449e10987a9e341751c1'

META_PARTICIPANTES_SERVICIOS = 6500
META_PARTICIPANTES_UNICOS = 4500

MESES_ES = {
    1: 'Enero',
    2: 'Febrero',
    3: 'Marzo',
    4: 'Abril',
    5: 'Mayo',
    6: 'Junio',
    7: 'Julio',
    8: 'Agosto',
    9: 'Septiembre',
    10: 'Octubre',
    11: 'Noviembre',
    12: 'Diciembre',
}

MAPA_ESTADOS = {
    'VE01': 'Distrito Capital',
    'VE07': 'Bolívar',
    'VE15': 'Miranda',
    'VE19': 'Sucre',
    'VE24': 'La Guaira',
    'Distrito Capital': 'Distrito Capital',
    'Distrito_Capital': 'Distrito Capital',
    'Bolivar': 'Bolívar',
    'Bolívar': 'Bolívar',
    'Miranda': 'Miranda',
    'Sucre': 'Sucre',
    'La Guaira': 'La Guaira',
    'La_Guaira': 'La Guaira',
}

MAPA_MUNICIPIOS = {
    'Libertador': 'Libertador',
    'Vargas': 'Vargas',
    'Urdaneta': 'Urdaneta',
    'Paz_Castillo': 'Paz Castillo',
    'Paz Castillo': 'Paz Castillo',
    'Sucre_': 'Sucre (Miranda)',
    'Sucre__': 'Sucre (Sucre)',
    'Cruz_Salmerón_Acosta': 'Cruz Salmerón Acosta',
    'Cruz Salmerón Acosta': 'Cruz Salmerón Acosta',
    'Bermúdez': 'Bermúdez',
    'Bermudez': 'Bermúdez',
    'Arismendi': 'Arismendi',
    'Angostura del Orinoco': 'Angostura del Orinoco',
    'Angostura_del_Orinoco': 'Angostura del Orinoco',
    'Caroni': 'Caroní',
    'Caroní': 'Caroní',
}

COORDENADAS_MUNICIPIOS = {
    'Libertador': [10.5000, -66.9167],
    'Vargas': [10.6000, -66.9333],
    'Urdaneta': [10.1500, -66.8833],
    'Paz Castillo': [10.2167, -66.6667],
    'Sucre (Miranda)': [10.4833, -66.8167],
    'Sucre (Sucre)': [10.4539, -64.1825],
    'Cruz Salmerón Acosta': [10.5750, -64.2583],
    'Bermúdez': [10.6667, -63.2500],
    'Arismendi': [10.7167, -62.5833],
    'Angostura del Orinoco': [8.1292, -63.5409],
    'Caroní': [8.3167, -62.7167],
}

font_layout = dict(family='Quicksand', size=13)


def clasificar_servicio_proteccion(id_act, actividad_texto):
    cod = str(id_act).upper().strip()
    txt = str(actividad_texto).lower().strip()
    if 'R1A2' in cod or 'violencia de género' in txt or 'vbg' in txt:
        return 'Prevención y Respuesta VBG (R1A2)'
    elif 'R1A3' in cod or 'jurídica' in txt or 'legal' in txt:
        return 'Asistencia Jurídica (R1A3)'
    elif 'R1A4' in cod or 'psicosocial' in txt or 'smaps' in txt:
        return 'Apoyo Psicosocial - SMAPS (R1A4)'
    elif 'R1A5' in cod or 'sensibilización' in txt or 'formación' in txt:
        return 'Sensibilización y Formación (R1A5)'
    elif 'R1A1' in cod or 'protección infantil' in txt or 'nna' in txt:
        return 'Gestión de Casos Protección Infantil (R1A1)'
    return 'Otras Actividades de Protección'


def buscar_valor_columna(row_dict, candidatos, default=''):
    for cand in candidatos:
        if cand in row_dict and row_dict[cand] not in (None, ''):
            return row_dict[cand]

    claves_lower = {k.lower(): k for k in row_dict.keys()}
    for cand in candidatos:
        cand_l = cand.lower()
        if cand_l in claves_lower:
            val = row_dict[claves_lower[cand_l]]
            if val not in (None, ''):
                return val
        for k_l, k_orig in claves_lower.items():
            if k_l.endswith('/' + cand_l) or cand_l in k_l:
                val = row_dict[k_orig]
                if val not in (None, ''):
                    return val
    return default


def calcular_rango_etario(edad_val):
    try:
        edad = int(float(edad_val))
        if edad <= 4:
            return '0 a 4 años'
        elif edad <= 17:
            return '5 a 17 años'
        elif edad <= 49:
            return '18 a 49 años'
        else:
            return '50 años o más'
    except Exception:
        return '18 a 49 años'


# -----------------------------------------------------------------------------
# 2. CARGA DE DATOS DESDE API KOBOTOOLBOX
# -----------------------------------------------------------------------------
@st.cache_data(ttl=600, show_spinner='Sincronizando registros con KoboToolbox...')
def cargar_datos_kobo(server_url, form_uid, api_token):
    url = f'{server_url}/api/v2/assets/{form_uid}/data/?format=json&limit=1000'
    headers = {'Authorization': f'Token {api_token}'}
    todos_los_envios = []

    try:
        while url:
            resp = requests.get(url, headers=headers, timeout=30)
            if resp.status_code == 401:
                st.error('❌ Error de autenticación (401): Verifica el Token API de KoboToolbox.')
                return pd.DataFrame(), []
            elif resp.status_code == 404:
                st.error('❌ Formulario no encontrado (404): Verifica el UID del proyecto o permisos.')
                return pd.DataFrame(), []
            resp.raise_for_status()

            payload = resp.json()
            resultados = payload.get('results', [])
            todos_los_envios.extend(resultados)
            url = payload.get('next')
    except requests.exceptions.RequestException as e:
        st.error(f'❌ Error de conexión con KoboToolbox: {e}')
        return pd.DataFrame(), []

    if not todos_los_envios:
        return pd.DataFrame(), []

    filas_aplanadas = []
    columnas_detectadas = set()

    for envio in todos_los_envios:
        campos_repeat = [
            k for k, v in envio.items()
            if isinstance(v, list) and len(v) > 0 and isinstance(v[0], dict)
        ]

        if campos_repeat:
            nombre_repeat = campos_repeat[0]
            datos_padre = {k: v for k, v in envio.items() if k not in campos_repeat}
            for item_rep in envio[nombre_repeat]:
                fila_combinada = {**datos_padre, **item_rep}
                filas_aplanadas.append(fila_combinada)
                columnas_detectadas.update(fila_combinada.keys())
        else:
            filas_aplanadas.append(envio)
            columnas_detectadas.update(envio.keys())

    registros = []
    for idx, row in enumerate(filas_aplanadas):
        kobo_id = str(row.get('_id') or f'KOBO_{idx}').strip()
        codigo_id = str(
            buscar_valor_columna(
                row,
                ['CodigoID', 'codigo_id', 'cedula', 'documento', 'id_beneficiario', 'identificacion'],
                default=kobo_id,
            )
        ).strip()

        fecha = buscar_valor_columna(
            row,
            ['fecha_actividad', 'Fecha de la Actividad', 'fecha', 'start', '_submission_time'],
            default=None,
        )

        estado_raw = str(
            buscar_valor_columna(row, ['estado', 'Estado', 'admin1'], default='')
        ).strip()
        estado = MAPA_ESTADOS.get(estado_raw, estado_raw.replace('_', ' ') or 'No especificado')

        muni_raw = str(
            buscar_valor_columna(row, ['municipio', 'Municipio', 'admin2'], default='')
        ).strip()
        muni = MAPA_MUNICIPIOS.get(muni_raw, muni_raw.replace('_', ' ') or 'No especificado')

        parroquia = str(
            buscar_valor_columna(row, ['parroquia', 'Parroquia', 'admin3', 'comunidad'], default='No especificado')
        ).strip().replace('_', ' ')

        organizacion = str(
            buscar_valor_columna(row, ['organizacion', 'Organización', 'socio', 'implementador'], default='COOPI')
        ).strip()

        id_resul_val = str(
            buscar_valor_columna(row, ['id_resultado', 'ID Resultado', 'resultado_cod'], default='')
        ).strip().upper()
        resultado_raw = str(
            buscar_valor_columna(row, ['resultado', 'Resultado', 'sector', 'componente'], default='')
        ).strip()

        if id_resul_val == 'R1' or 'protección' in resultado_raw.lower() or 'proteccion' in resultado_raw.lower():
            sector = 'R1. Protección'
        elif id_resul_val == 'R2' or 'salud' in resultado_raw.lower() or 'nutrición' in resultado_raw.lower():
            sector = 'R2. Salud'
        elif id_resul_val == 'R4' or 'wash' in resultado_raw.lower() or 'agua' in resultado_raw.lower():
            sector = 'R4. WASH'
        elif id_resul_val == 'R5' or 'emergencia' in resultado_raw.lower():
            sector = 'R5. Respuesta a Emergencia'
        else:
            sector = resultado_raw if resultado_raw else 'R1. Protección'

        id_act = str(
            buscar_valor_columna(row, ['id_actividad', 'ID Actividad', 'codigo_actividad'], default='')
        ).strip()
        actividad_texto = str(
            buscar_valor_columna(row, ['actividad', 'Actividad', 'tipo_actividad', 'servicio'], default='Actividad registrada')
        ).strip()
        indicador_texto = str(
            buscar_valor_columna(row, ['indicador', 'Indicadores', 'indicadores'], default='Sin indicador asignado')
        ).strip()

        tipo_serv = clasificar_servicio_proteccion(id_act, actividad_texto)

        val_sexo = str(
            buscar_valor_columna(row, ['sexo', 'Sexo', 'genero', 'Genero'], default='Mujer')
        ).strip().title()
        if any(x in val_sexo.lower() for x in ['hombre', 'masc', 'h', 'm_hombre']):
            sexo = 'Hombre'
        elif any(x in val_sexo.lower() for x in ['mujer', 'fem', 'f']):
            sexo = 'Mujer'
        else:
            sexo = 'Otro'

        rango_raw = buscar_valor_columna(row, ['rango_etario', 'grupo_etario', 'rango_edad'], default='')
        if rango_raw:
            rango_etario = str(rango_raw).strip().replace('_', ' ')
        else:
            edad_num = buscar_valor_columna(row, ['edad', 'Edad', 'age'], default='')
            rango_etario = calcular_rango_etario(edad_num)

        val_disc = str(
            buscar_valor_columna(row, ['discapacidad', 'Persona con Discapacidad', 'pcd'], default='No')
        ).strip().lower()
        discapacidad = (
            'Sí' if any(x in val_disc for x in ['sí', 'si', 'yes', 'true', '1']) else 'No'
        )

        try:
            cant_atenciones = int(float(buscar_valor_columna(row, ['total_participantes', 'cantidad', 'beneficiarios'], default=1)))
            if cant_atenciones < 1:
                cant_atenciones = 1
        except Exception:
            cant_atenciones = 1

        registros.append({
            'Fecha': fecha,
            'Estado': estado,
            'Municipio': muni,
            'Parroquia': parroquia,
            'Organizacion': organizacion,
            'Sector': sector,
            'ID_Actividad': id_act,
            'Actividad_Texto': actividad_texto,
            'Indicador_Texto': indicador_texto,
            'Tipo_Servicio_Proteccion': tipo_serv,
            'Sexo': sexo,
            'Rango_Etario': rango_etario,
            'Discapacidad': discapacidad,
            'Servicios_Count': cant_atenciones,
            'Case_ID': codigo_id,
        })

    df = pd.DataFrame(registros)

    if not df.empty:
        df['Fecha_DT'] = pd.to_datetime(df['Fecha'], errors='coerce')
        df = df.sort_values(by=['Fecha_DT', 'Case_ID'], na_position='last').reset_index(drop=True)

        df['Unicos_General'] = (~df.duplicated(subset=['Case_ID'])).astype(int)
        df['Unicos_Resultado'] = (~df.duplicated(subset=['Case_ID', 'Sector'])).astype(int)
        df['Unicos_Actividad'] = (~df.duplicated(subset=['Case_ID', 'Actividad_Texto'])).astype(int)

        df['Mes_Orden'] = df['Fecha_DT'].dt.strftime('%Y-%m').fillna('9999-99')
        df['Mes_Reporte'] = df['Fecha_DT'].apply(
            lambda x: f'{x.year} - {MESES_ES.get(x.month, "")}' if pd.notnull(x) else 'Sin fecha'
        )

    return df, sorted(list(columnas_detectadas))


df_raw, cols_kobo = cargar_datos_kobo(KOBO_SERVER, FORM_UID, KOBO_API_TOKEN)

if df_raw.empty:
    st.warning('⚠️ No hay registros disponibles en el formulario de KoboToolbox o no se pudo establecer conexión.')
    st.stop()

# -----------------------------------------------------------------------------
# FILTROS LATERALES
# -----------------------------------------------------------------------------
st.sidebar.header('Sincronización y Filtros')

if st.sidebar.button('🔄 Actualizar Datos desde Kobo', width='stretch'):
    st.cache_data.clear()
    st.rerun()

st.sidebar.caption(f'🟢 Conectado a KoboToolbox (`{FORM_UID}`)')
st.sidebar.markdown('---')

meses_df = (
    df_raw[['Mes_Orden', 'Mes_Reporte']]
    .drop_duplicates()
    .sort_values('Mes_Orden')
)
meses_disp = ['Todos'] + meses_df['Mes_Reporte'].tolist()
mes_sel = st.sidebar.selectbox('Mes del Reporte:', meses_disp, index=0)

org_disp = ['Todos'] + sorted(df_raw['Organizacion'].unique().tolist())
org_sel = st.sidebar.selectbox('Socio / Organización:', org_disp, index=0)

estado_disp = ['Todos'] + sorted(df_raw['Estado'].unique().tolist())
estado_sel = st.sidebar.selectbox('Estado:', estado_disp, index=0)

sexo_disp = ['Todos', 'Mujer', 'Hombre', 'Otro']
sexo_sel = st.sidebar.selectbox('Sexo del Participante:', sexo_disp, index=0)

rango_disp = ['Todos'] + sorted(df_raw['Rango_Etario'].unique().tolist())
rango_sel = st.sidebar.selectbox('Rango Etario:', rango_disp, index=0)

disc_disp = ['Todos', 'Sí', 'No']
disc_sel = st.sidebar.selectbox('Persona con Discapacidad:', disc_disp, index=0)

with st.sidebar.expander('🔍 Ver campos detectados en Kobo'):
    campos_limpios = [c for c in cols_kobo if not c.startswith('_') and not c.startswith('meta/')]
    st.write(campos_limpios)

df_filtered = df_raw.copy()
if mes_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Mes_Reporte'] == mes_sel]
if org_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Organizacion'] == org_sel]
if estado_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Estado'] == estado_sel]
if sexo_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Sexo'] == sexo_sel]
if rango_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Rango_Etario'] == rango_sel]
if disc_sel != 'Todos':
    df_filtered = df_filtered[df_filtered['Discapacidad'] == disc_sel]

# -----------------------------------------------------------------------------
# MÉTRICAS CLAVE
# -----------------------------------------------------------------------------
total_servicios = int(df_filtered['Servicios_Count'].sum())
total_unicos = int(df_filtered['Unicos_General'].sum())

pct_meta_unicos = (
    (total_unicos / META_PARTICIPANTES_UNICOS) * 100
    if META_PARTICIPANTES_UNICOS > 0
    else 0
)

df_unicos_rows = df_filtered[df_filtered['Unicos_General'] == 1]

conteo_sexo = (
    df_unicos_rows.groupby('Sexo')['Unicos_General'].sum()
    if not df_unicos_rows.empty
    else pd.Series()
)
total_mujeres = int(conteo_sexo.get('Mujer', 0))
total_hombres = int(conteo_sexo.get('Hombre', 0))
total_otro = int(conteo_sexo.get('Otro', 0))

conteo_disc = (
    df_unicos_rows.groupby('Discapacidad')['Unicos_General'].sum()
    if not df_unicos_rows.empty
    else pd.Series()
)
total_discapacidad = int(conteo_disc.get('Sí', 0))

total_unicos_r1 = int(
    df_filtered[df_filtered['Sector'] == 'R1. Protección']['Unicos_Resultado'].sum()
)
total_unicos_r2 = int(
    df_filtered[df_filtered['Sector'] == 'R2. Salud']['Unicos_Resultado'].sum()
)
total_unicos_r4 = int(
    df_filtered[df_filtered['Sector'] == 'R4. WASH']['Unicos_Resultado'].sum()
)
total_unicos_r5 = int(
    df_filtered[df_filtered['Sector'] == 'R5. Respuesta a Emergencia']['Unicos_Resultado'].sum()
)

col1, col2, col3 = st.columns(3)
col1.metric('Total de Atenciones / Servicios', f'{total_servicios:,}')
col2.metric('Participantes Únicos Totales', f'{total_unicos:,}')
col3.metric(
    f'% Alcance Meta Únicos ({META_PARTICIPANTES_UNICOS:,})',
    f'{pct_meta_unicos:.1f}%',
    delta=f'{total_unicos:,} / {META_PARTICIPANTES_UNICOS:,}',
)

col_r1, col_r2, col_r4, col_r5 = st.columns(4)
col_r1.metric('Únicos R1. Protección', f'{total_unicos_r1:,}')
col_r2.metric('Únicos R2. Salud', f'{total_unicos_r2:,}')
col_r4.metric('Únicos R4. WASH', f'{total_unicos_r4:,}')
col_r5.metric('Únicos R5. Emergencia', f'{total_unicos_r5:,}')

col_m, col_h, col_o, col_d = st.columns(4)
col_m.metric('Participantes Únicos: Mujeres', f'{total_mujeres:,}')
col_h.metric('Participantes Únicos: Hombres', f'{total_hombres:,}')
col_o.metric('Participantes Únicos: Otro', f'{total_otro:,}')
col_d.metric('Participantes con Discapacidad', f'{total_discapacidad:,}')

st.markdown('---')

# -----------------------------------------------------------------------------
# GRÁFICOS: RANGO ETARIO Y SEXO / MUNICIPIOS
# -----------------------------------------------------------------------------
g1, g2 = st.columns(2)

with g1:
    st.subheader('Participantes Únicos por Rango Etario y Sexo')
    if not df_unicos_rows.empty and 'Rango_Etario' in df_unicos_rows.columns:
        df_demo = (
            df_unicos_rows.groupby(['Rango_Etario', 'Sexo'])['Unicos_General']
            .sum()
            .reset_index(name='Cantidad')
        )

        total_global_unicos = df_demo['Cantidad'].sum()
        df_demo['Porcentaje'] = (
            (df_demo['Cantidad'] / total_global_unicos) * 100
            if total_global_unicos > 0
            else 0.0
        ).round(1)
        df_demo['Texto_Etiqueta'] = (
            df_demo['Cantidad'].astype(str)
            + ' ('
            + df_demo['Porcentaje'].astype(str)
            + '%)'
        )

        orden_etario = {
            '0 a 4 años': 1,
            '5 a 17 años': 2,
            '18 a 49 años': 3,
            '50 años o más': 4,
        }
        df_demo['Orden'] = (
            df_demo['Rango_Etario'].str.lower().map(orden_etario).fillna(99)
        )
        df_demo = df_demo.sort_values('Orden')

        fig_demo = px.bar(
            df_demo,
            x='Rango_Etario',
            y='Cantidad',
            color='Sexo',
            barmode='group',
            text='Texto_Etiqueta',
            color_discrete_sequence=PALETA_COOPI,
        )
        fig_demo.update_traces(textposition='outside')
        fig_demo.update_layout(
            font=font_layout,
            xaxis_title='Rango Etario',
            yaxis_title='Cantidad',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.25,
                xanchor='center',
                x=0.5,
            ),
        )
        st.plotly_chart(fig_demo, width='stretch')
    else:
        st.info('No hay datos disponibles para los filtros seleccionados.')

with g2:
    st.subheader('Participantes Únicos por Municipio')
    if not df_unicos_rows.empty and 'Municipio' in df_unicos_rows.columns:
        df_muni = (
            df_unicos_rows.groupby(['Estado', 'Municipio'])['Unicos_General']
            .sum()
            .reset_index(name='Cantidad')
        )
        total_global_unicos_muni = df_muni['Cantidad'].sum()
        df_muni['Porcentaje'] = (
            (df_muni['Cantidad'] / total_global_unicos_muni) * 100
            if total_global_unicos_muni > 0
            else 0.0
        ).round(1)
        df_muni['Texto_Etiqueta'] = (
            df_muni['Cantidad'].astype(str)
            + ' ('
            + df_muni['Porcentaje'].astype(str)
            + '%)'
        )

        df_muni = df_muni.sort_values(by='Cantidad', ascending=True)
        fig_muni = px.bar(
            df_muni,
            y='Municipio',
            x='Cantidad',
            color='Estado',
            orientation='h',
            text='Texto_Etiqueta',
            color_discrete_sequence=PALETA_COOPI,
        )
        fig_muni.update_traces(textposition='outside')
        fig_muni.update_layout(
            font=font_layout,
            yaxis_title='Municipio',
            legend=dict(
                orientation='h',
                yanchor='top',
                y=-0.25,
                xanchor='center',
                x=0.5,
            ),
        )
        st.plotly_chart(fig_muni, width='stretch')
    else:
        st.info('No hay datos disponibles.')

st.markdown('---')

# -----------------------------------------------------------------------------
# MAPA INTERACTIVO
# -----------------------------------------------------------------------------
st.subheader('Mapa de Cobertura por Municipios Atendidos')

mapa = folium.Map(
    location=[9.60, -64.80], zoom_start=7, tiles='OpenStreetMap'
)

if not df_unicos_rows.empty:
    muni_resumen = []
    for (est, mun), grupo in df_unicos_rows.groupby(['Estado', 'Municipio']):
        tot = int(grupo['Unicos_General'].sum())
        parroquias = sorted([
            p
            for p in grupo['Parroquia'].dropna().unique()
            if p and p != 'No especificado'
        ])
        parroquias_str = '<br>'.join([f'- {p}' for p in parroquias[:10]])
        if len(parroquias) > 10:
            parroquias_str += f'<br><i>... y {len(parroquias) - 10} más</i>'
        if not parroquias_str:
            parroquias_str = '- No especificado'

        muni_resumen.append({
            'Estado': est,
            'Municipio': mun,
            'Total_Unicos': tot,
            'Parroquias': parroquias_str,
        })

    df_mapa = pd.DataFrame(muni_resumen)

    for _, m_row in df_mapa.iterrows():
        est = m_row['Estado']
        mun = m_row['Municipio']
        tot = m_row['Total_Unicos']
        parrs = m_row['Parroquias']
        coords = COORDENADAS_MUNICIPIOS.get(mun, [10.5, -66.9])

        popup_html = f"""
        <div style='font-family: Quicksand; font-size: 13px; width: 230px;'>
            <h4 style='color: {COLOR_AZUL_COOPI}; margin-bottom: 5px;'>{mun}</h4>
            <b>Estado:</b> {est}<br>
            <b>Participantes Únicos:</b> <b>{tot:,}</b><br>
            <hr style='margin: 5px 0;'>
            <b>Parroquias atendidas:</b><br>
            {parrs}
        </div>
        """
        folium.CircleMarker(
            location=coords,
            radius=min(tot / 45, 25) + 8,
            popup=folium.Popup(popup_html, max_width=260),
            color=COLOR_AZUL_COOPI,
            fill=True,
            fill_color=COLOR_AZUL_COOPI,
            fill_opacity=0.8,
        ).add_to(mapa)

st_folium(mapa, width='stretch', height=450)

st.markdown('---')

# -----------------------------------------------------------------------------
# RESUMEN POR RESULTADO, ACTIVIDAD E INDICADOR
# -----------------------------------------------------------------------------
st.subheader('Desglose por Resultado, Actividad e Indicador (KoboToolbox)')

if not df_filtered.empty:
    df_resumen_act = (
        df_filtered.groupby(
            ['Sector', 'Actividad_Texto', 'Indicador_Texto'], as_index=False
        )
        .agg(
            Total_Atenciones=('Servicios_Count', 'sum'),
            Participantes_Unicos_Actividad=('Unicos_Actividad', 'sum'),
        )
        .sort_values(by=['Sector', 'Total_Atenciones'], ascending=[True, False])
    )
    df_resumen_act = df_resumen_act.rename(
        columns={
            'Sector': 'Resultado',
            'Actividad_Texto': 'Actividad',
            'Indicador_Texto': 'Indicador Asociado',
            'Total_Atenciones': 'Total Atenciones',
            'Participantes_Unicos_Actividad': 'Beneficiarios Únicos x Actividad',
        }
    )

    st.dataframe(
        df_resumen_act,
        width='stretch',
        hide_index=True,
    )
else:
    st.info('No hay datos disponibles para los filtros seleccionados.')

st.markdown('---')

# -----------------------------------------------------------------------------
# CAPÍTULO: RESULTADO 1 - PROTECCIÓN
# -----------------------------------------------------------------------------
st.subheader('Detalle Resultado 1: Protección')

df_prot = df_filtered[df_filtered['Sector'] == 'R1. Protección'].copy()

if not df_prot.empty:
    total_casos_prot = int(df_prot['Servicios_Count'].sum())
    total_unicos_prot = int(df_prot['Unicos_Resultado'].sum())

    col_p1, col_p2 = st.columns(2)
    col_p1.metric('Total de Atenciones en Protección', f'{total_casos_prot:,}')
    col_p2.metric(
        'Participantes Únicos en Protección', f'{total_unicos_prot:,}'
    )

    df_servicios_count = (
        df_prot.groupby('Tipo_Servicio_Proteccion', as_index=False)
        .agg(
            Cantidad_Atenciones=('Servicios_Count', 'sum'),
            Beneficiarios_Unicos=('Unicos_Actividad', 'sum'),
        )
        .sort_values(by='Cantidad_Atenciones', ascending=False)
    )

    fig_prot = px.bar(
        df_servicios_count,
        x='Tipo_Servicio_Proteccion',
        y='Cantidad_Atenciones',
        text='Cantidad_Atenciones',
        color='Tipo_Servicio_Proteccion',
        color_discrete_sequence=PALETA_COOPI,
    )
    fig_prot.update_traces(textposition='outside')
    fig_prot.update_layout(
        font=font_layout,
        xaxis_title='Actividad / Servicio de Protección',
        yaxis_title='Cantidad de Atenciones',
        showlegend=False,
    )
    st.plotly_chart(fig_prot, width='stretch')
else:
    st.info(
        'No hay registros de servicios de protección para los filtros seleccionados.'
    )
