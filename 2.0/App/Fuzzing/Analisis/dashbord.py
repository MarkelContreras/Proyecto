import os
import sys
import pandas as pd
import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import dash_bootstrap_components as dbc

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
# 📦 FUNCIONES DE GRÁFICOS
# ───────────────────────────────
def card(fig):
    return html.Div([dcc.Graph(figure=fig)], style={
        "backgroundColor": "#fff",
        "padding": "20px",
        "borderRadius": "12px",
        "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
    })

def generar_graficos(df_base, programa=None, sesion=None):
    # ────────────────────────────────
    # ⛔ Si no hay programa, no mostramos nada
    # ────────────────────────────────
    if not programa:
        return [], []

    # ────────────────────────────────
    # 📊 SECCIÓN GLOBAL (filtra solo por programa)
    # ────────────────────────────────
    df_global = df_base[df_base["programa"] == programa].copy()
    df_global["exit_code"] = df_global["exit_code"].astype(int)
    df_global["fallo"] = df_global["exit_code"] != 0

    # ✅ Gráfico global  1: Válidos vs Errores (global)
    valid_vs_errors = pd.DataFrame({
        "Tipo": ["Válidos", "Errores"],
        "Cantidad": [
            (df_global["fallo"] == False).sum(),
            (df_global["fallo"] == True).sum()
        ]
    })
    
    fig1_global = px.bar(
        valid_vs_errors,
        x="Tipo",
        y="Cantidad",
        title="Cantidad de válidos vs errores",
        color="Tipo",
        color_discrete_sequence=["green", "red"]
    )

    # 📦 Gráfico global 2: Distribución de códigos de error (global)
    errores_df = df_global[df_global["exit_code"] != 0].copy()
    exit_counts = errores_df["exit_code"].value_counts().sort_index().reset_index()
    exit_counts.columns = ["Código de error", "Frecuencia"]
    exit_counts["Código de error"] = exit_counts["Código de error"].astype(str)
    
    fig2_global = px.bar(
        exit_counts,
        x="Código de error",
        y="Frecuencia",
        title="Distribución de códigos de error",
        color="Código de error"
    )
    fig2_global.update_xaxes(type="category", dtick=1)

    # 🧪 Gráfico global 3: Inputs por sesión (global)
    inputs_por_sesion = df_global.groupby("session_id")["input"].count().reset_index(name="total_inputs")
    
    fig3_global = px.bar(
        inputs_por_sesion,
        x="session_id",
        y="total_inputs",
        title="📥 Cantidad de inputs por sesión",
        color="total_inputs",
        color_continuous_scale=px.colors.sequential.Blues
    )
    fig3_global.update_layout(coloraxis_showscale=False)
    fig3_global.update_xaxes(type="category", dtick=1)

    # ❌ Gráfico global 4: Errores por sesión (global)
    errores_sesion_global = df_global[df_global["fallo"] == True].copy()
    errores_sesion_global = errores_sesion_global.groupby("session_id").size().reset_index(name="Errores")
    
    fig4_global = px.bar(
        errores_sesion_global,
        x="session_id",
        y="Errores",
        title="❌ Número de errores por sesión",
        color="session_id",
        labels={"session_id": "ID de sesión"}
    )
    fig4_global.update_xaxes(dtick=1)

    # 📦 Tarjetas globales
    global_cards = [card(fig1_global), card(fig3_global), card(fig2_global), card(fig4_global)]

    # ────────────────────────────────
    # 🎯 SECCIÓN POR SESIÓN (programa + sesión)
    # ────────────────────────────────
    if sesion is None:
        return global_cards, []

    df_sesion = df_base[
        (df_base["programa"] == programa) &
        (df_base["session_id"] == sesion)
    ].copy()
    df_sesion["exit_code"] = df_sesion["exit_code"].astype(int)

    # 📉 Gráfico sesión 1: Códigos de error
    errores_por_codigo = df_sesion[df_sesion["exit_code"] != 0]["exit_code"].value_counts().sort_index().reset_index()
    errores_por_codigo.columns = ["Código", "Frecuencia"]
    errores_por_codigo["Código"] = errores_por_codigo["Código"].astype(str)
    
    fig1_sesion = px.bar(
        errores_por_codigo,
        x="Código",
        y="Frecuencia",
        title="❗ Códigos de error en la sesión",
        color="Código"
    )
    fig1_sesion.update_xaxes(type="category")

    # ✅❌ Gráfico sesión 2: Válidos vs Errores
    conteo = pd.DataFrame({
        "Tipo": ["Válidos", "Errores"],
        "Cantidad": [
            (df_sesion["exit_code"] == 0).sum(),
            (df_sesion["exit_code"] != 0).sum()
        ]
    })
    
    fig2_sesion = px.bar(
        conteo,
        x="Tipo",
        y="Cantidad",
        title="✅ Válidos vs ❌ Errores en la sesión",
        color="Tipo",
        color_discrete_map={"Válidos": "green", "Errores": "red"}
    )

    # 📏 Histograma de longitudes de input en esta sesión
    df_sesion["input_length"] = df_sesion["input"].apply(len)

    fig3_sesion = px.histogram(
        df_sesion,
        x="input_length",
        nbins=20,
        title="📐 Histograma de longitudes de inputs",
        labels={"input_length": "Longitud del input"},
        color_discrete_sequence=["#636EFA"]
    )
    fig3_sesion.update_traces(marker_line_width=1, marker_line_color="white")


    # 📦 Tarjetas por sesión
    session_cards = [card(fig1_sesion), card(fig2_sesion),card(fig3_sesion)]

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
        dbc.Collapse(id="collapse-global", is_open=True, children=html.Div(id="bloque-global-content", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "30px", "marginBottom": "40px"}))
    ]),

    html.Div(children=[
        html.H3(id="titulo-sesiones", children="➖ 🔶 Análisis de una sesión en concreto", style={"fontSize": "22px", "color": "#333", "marginBottom": "15px", "cursor": "pointer"}),
        dbc.Collapse(id="collapse-sesiones", is_open=True, children=html.Div(id="bloque-sesiones-content", style={"display": "grid", "gridTemplateColumns": "1fr 1fr", "gap": "30px"}))
    ])
])

@app.callback(
    Output("sesion-dropdown", "options"),
    Input("programa-dropdown", "value")
)
def actualizar_sesiones(programa_seleccionado):
    if programa_seleccionado is None:
        return []
    sesiones = df[df["programa"] == programa_seleccionado]["session_id"].unique()
    return [{"label": s, "value": s} for s in sorted(sesiones)]

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
    Output("bloque-sesiones-content", "children"),
    Input("programa-dropdown", "value"),
    Input("sesion-dropdown", "value")
)
def actualizar_graficos(programa, sesion):
    if not programa:
        mensaje = html.P("📌 Selecciona un programa para ver el análisis de un programa.", style={"textAlign": "center", "fontSize": "18px"})
        return mensaje, []
    
    global_cards, session_cards = generar_graficos(df, programa=programa, sesion=sesion)

    if not sesion:
        mensaje_sesion = html.P("📌 Selecciona una sesión para ver el análisis detallado de una sesión.", style={"textAlign": "center", "fontSize": "18px"})
        return global_cards, mensaje_sesion

    return global_cards, session_cards


# ───────────────────────────────
# ▶️ LANZAR LA APP
# ───────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)