import os
import sys
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import plotly.express as px
import dash_bootstrap_components as dbc
import math
import time
import plotly.graph_objects as go
from graficos_sesion import generar_graficos_sesion, grafico_errores_por_codigo, grafico_validos_vs_errores, grafico_longitud_histograma, grafico_inputs_unicos_repetidos, tabla_inputs_repetidos, grafico_longitud_inputs, categorizar_longitud
from graficos_globales import grafico_validos_vs_errores_global, grafico_codigos_error_global, grafico_inputs_por_sesion, grafico_errores_por_sesion, grafico_duracion_sesiones, grafico_radar_programa, grafico_longitud_inputs_global, categorizar_longitud

# ───────────────────────────────
# 🔗 CONEXIÓN A LA BASE DE DATOS
# ───────────────────────────────
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../")))
from config_db import get_connection

conn = get_connection()
if conn is None:
    print("❌ No se pudo conectar a la base de datos.")
    sys.exit(1)

query = "SELECT * FROM fuzzing"
df = pd.read_sql(query, conn)
conn.close()

# ───────────────────────────────
# 📊 GENERACIÓN DE GRÁFICOS
# ───────────────────────────────

def generar_graficos(df_base, programa=None, sesion=None):
    if not programa:
        return [], []

    # ─── Preparamos DataFrame global ─────────────────────────────
    df_global = df_base[df_base["programa"] == programa].copy()
    df_global = df_global.drop_duplicates(subset=["input", "exit_code"])
    df_global["exit_code"] = df_global["exit_code"].astype(int)
    df_global["fallo"] = df_global["exit_code"] != 0
    df_global["input_length"] = df_global["input"].apply(len)
    df_global["length_category"] = df_global["input_length"].apply(categorizar_longitud)

    # ─── Gráficos globales como en sesiones ──────────────────────
    global_cards = [
        grafico_validos_vs_errores_global(df_global),
        grafico_inputs_por_sesion(df_global),
        grafico_codigos_error_global(df_global),
        grafico_errores_por_sesion(df_global),
        grafico_duracion_sesiones(df_global),
        grafico_radar_programa(),
        grafico_longitud_inputs_global(df_global, exito=True),
        grafico_longitud_inputs_global(df_global, exito=False)
    ]

    if not sesion:
        return global_cards, []

    # ─── Preparamos DataFrame de sesión ──────────────────────────
    df_sesion = df_base[
        (df_base["programa"] == programa) &
        (df_base["session_id"] == sesion)
    ].copy()

    df_sesion["exit_code"] = df_sesion["exit_code"].astype(int)
    df_sesion = df_sesion.drop_duplicates(subset=["input", "exit_code"])
    df_sesion["input_length"] = df_sesion["input"].apply(len)
    df_sesion["length_category"] = df_sesion["input_length"].apply(categorizar_longitud)

    # ─── Gráficos de sesión ──────────────────────────────────────
    session_cards = [
        grafico_errores_por_codigo(df_sesion),
        grafico_validos_vs_errores(df_sesion),
        grafico_longitud_histograma(df_sesion),
        grafico_inputs_unicos_repetidos(df_sesion),
        #tabla_inputs_repetidos(df_sesion),
        grafico_longitud_inputs(df_sesion, exito=True),
        grafico_longitud_inputs(df_sesion, exito=False)
    ]

    return global_cards, session_cards

# ───────────────────────────────
# 🚀 INICIALIZACIÓN DE LA APP
# ───────────────────────────────
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.title = "Dashboard Fuzzing"
programas_unicos = sorted(df["programa"].unique())

# ───────────────────────────────
# 🎨 LAYOUT + CALLBACKS
# ───────────────────────────────
app.layout = html.Div(style={"backgroundColor": "#f9f9f9", "padding": "20px", "fontFamily": "Arial, sans-serif"}, children=[
    html.H1("📊 Dashboard de Fuzzing", style={"textAlign": "center", "color": "#333"}),

    html.Div(style={"display": "flex", "justifyContent": "center", "marginBottom": "40px"}, children=[
        html.Div(style={"backgroundColor": "#ffffff", "padding": "30px", "borderRadius": "15px", "boxShadow": "0 4px 12px rgba(0, 0, 0, 0.1)", "maxWidth": "1000px", "width": "100%"}, children=[
            html.H2("🔍 Filtrar resultados", style={"textAlign": "center", "marginBottom": "25px", "color": "#333"}),
            html.Div(style={"display": "flex", "justifyContent": "space-between", "gap": "20px"}, children=[
                html.Div(style={"flex": "1"}, children=[
                    html.Label("Programa", style={"fontWeight": "bold"}),
                    dcc.Dropdown(id="programa-dropdown", options=[{"label": p, "value": p} for p in programas_unicos], placeholder="Selecciona un programa")
                ]),
                html.Div(style={"flex": "1"}, children=[
                    html.Label("Sesión", style={"fontWeight": "bold"}),
                    dcc.Dropdown(id="sesion-dropdown", placeholder="Selecciona una sesión")
                ])
            ])
        ])
    ]),

    html.Div(children=[
        html.H3(id="titulo-global", children="➖ 🔷 Análisis global del programa", style={"fontSize": "22px", "color": "#333", "marginBottom": "15px", "cursor": "pointer"}),
        dbc.Collapse(
            id="collapse-global",
            is_open=True,
            children=dcc.Loading(
                type="circle",
                color="#2c3e50",
                children=html.Div(id="bloque-global-content", style={"display": "grid", "gap": "30px 40px", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "alignItems": "start", "width": "100%"})
            )
        )
    ]),

    html.Div(children=[
        html.H3(id="titulo-sesiones", children="➖ 🔶 Análisis de una sesión en concreto", style={"fontSize": "22px", "color": "#333", "marginBottom": "15px", "cursor": "pointer"}),
        dbc.Collapse(
            id="collapse-sesiones",
            is_open=True,
            children=dcc.Loading(
                type="circle",
                color="#2c3e50",
                children=html.Div(id="bloque-sesiones-content", style={"display": "grid", "gap": "30px 40px", "gridTemplateColumns": "repeat(auto-fit, minmax(300px, 1fr))", "alignItems": "start", "width": "100%"})
            )
        )
    ])
])

@app.callback(
    Output("sesion-dropdown", "options"),
    Output("sesion-dropdown", "value"),
    Input("programa-dropdown", "value")
)
def actualizar_sesiones(programa_seleccionado):
    if programa_seleccionado is None:
        return [], None
    sesiones = df[df["programa"] == programa_seleccionado]["session_id"].unique()
    return [{"label": s, "value": s} for s in sorted(sesiones)], None

@app.callback(
    Output("collapse-global", "is_open"),
    Output("titulo-global", "children"),
    Input("titulo-global", "n_clicks"),
    State("collapse-global", "is_open")
)
def toggle_global(n, is_open):
    if n:
        nuevo_estado = not is_open
    else:
        nuevo_estado = is_open
    icono = "➖" if nuevo_estado else "➕"
    return nuevo_estado, f"{icono} 🔷 Análisis global del programa"

@app.callback(
    Output("collapse-sesiones", "is_open"),
    Output("titulo-sesiones", "children"),
    Input("titulo-sesiones", "n_clicks"),
    State("collapse-sesiones", "is_open")
)
def toggle_sesiones(n, is_open):
    if n:
        nuevo_estado = not is_open
    else:
        nuevo_estado = is_open
    icono = "➖" if nuevo_estado else "➕"
    return nuevo_estado, f"{icono} 🔶 Análisis de una sesión en concreto"

@app.callback(
    Output("bloque-global-content", "children"),
    Input("programa-dropdown", "value"),
    prevent_initial_call=True
)
def actualizar_global(programa):
    if not programa:
        return html.P("📌 Selecciona un programa para ver el análisis de un programa.", style={"textAlign": "center", "fontSize": "18px"})
    time.sleep(1)
    global_cards, _ = generar_graficos(df, programa=programa, sesion=None)
    return global_cards

@app.callback(
    Output("bloque-sesiones-content", "children"),
    Input("programa-dropdown", "value"),
    Input("sesion-dropdown", "value"),
    prevent_initial_call=True
)
def actualizar_sesion(programa, sesion):
    if not programa or not sesion:
        return []
    time.sleep(1)
    _, session_cards = generar_graficos(df, programa=programa, sesion=sesion)
    return session_cards

# ───────────────────────────────
# ▶️ LANZAR LA APP
# ───────────────────────────────
if __name__ == "__main__":
    app.run(debug=True, port=8051)
