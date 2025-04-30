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
    df_global = df_global.drop_duplicates(subset=["input", "exit_code"])
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
    fig1_global.update_layout(showlegend=False)

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
    fig2_global.update_layout(showlegend=False)

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
    fig3_global.update_layout(coloraxis_showscale=False, showlegend=False)
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
    fig4_global.update_layout(showlegend=False, coloraxis_showscale=False)

    # Asegurarse de que las fechas y horas están en formato correcto
    df_global = df_global[df_global["fecha_inicio"].notna() & df_global["fecha_fin"].notna()]
    df_global = df_global[df_global["hora_inicio"].notna() & df_global["hora_fin"].notna()]

    duraciones = []

    for sesion_id in df_global["session_id"].unique():
        sub_df = df_global[df_global["session_id"] == sesion_id].sort_values(by=["fecha_inicio", "hora_inicio"])

        try:
            if sub_df.empty:
                continue

            inicio_fecha = str(sub_df["fecha_inicio"].iloc[0])
            inicio_hora = (pd.Timestamp("00:00:00") + sub_df["hora_inicio"].iloc[0]).strftime("%H:%M:%S")
            fin_fecha = str(sub_df["fecha_fin"].iloc[-1])
            fin_hora = (pd.Timestamp("00:00:00") + sub_df["hora_fin"].iloc[-1]).strftime("%H:%M:%S")

            dt_inicio = pd.to_datetime(f"{inicio_fecha} {inicio_hora}")
            dt_fin = pd.to_datetime(f"{fin_fecha} {fin_hora}")
            duracion_min = (dt_fin - dt_inicio).total_seconds() / 60

            duraciones.append({
                "session_id": sesion_id,
                "duracion_min": round(duracion_min, 2)
            })

        except Exception as e:
            print(f"Error al calcular duración de la sesión {sesion_id}: {e}")

    df_duracion = pd.DataFrame(duraciones)

    fig5_global = px.bar(
        df_duracion,
        x="session_id",
        y="duracion_min",
        title="⏱️ Duración de las sesiones",
        color="duracion_min",
        color_continuous_scale=px.colors.sequential.Tealgrn,
        labels={"duracion_min": "Duración (min)", "session_id": "ID de sesión"}
    )
    fig5_global.update_layout(showlegend=False, coloraxis_showscale=False)
    fig5_global.update_xaxes(type="category")

    categories = [
        'Metrica 1', 
        'Metrica 2', 
        'Metrica 3', 
        'Metrica 4', 
        'Metrica 5', 
    ]

    values = [80, 70, 85, 75, 90]
    categories_with_values = []
    for cat, val in zip(categories, values):
        if val is None:
            categories_with_values.append(f"{cat}<br>-")  
        else:
            categories_with_values.append(f"{cat}<br>{val}")

    # Para graficar, necesitamos valores numéricos: en caso de None, usamos 0.
    values_plot = [v if v is not None else 0 for v in values]

    # Cerramos el polígono repitiendo el primer elemento
    categories_closed = categories_with_values + [categories_with_values[0]]
    values_closed = values_plot + [values_plot[0]]

    # Creamos la figura en la variable fig6_global
    fig6_global = go.Figure()

    fig6_global.add_trace(
        go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            showlegend=False,
        )
    )

    fig6_global.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )
        ),
        showlegend=False, 
        title="Evaluación del programa"
    )

    # 🧪 Gráfico global 7: Longitud de Inputs Válidos (global)

    df_global["input_length"] = df_global["input"].apply(len)

    def categorizar_longitud(x):
        if x <= 50:
            return '0-50'
        elif x <= 100:
            return '51-100'
        elif x <= 300:
            return '101-300'
        elif x <= 1000:
            return '301-1000'
        else:
            return '1000+'

    df_global["length_category"] = df_global["input_length"].apply(categorizar_longitud)

    validos = df_global[df_global["fallo"] == False]
    validos_group = validos.groupby("length_category").size().reset_index(name='cantidad')

    categories_order = ['0-50', '51-100', '101-300', '301-1000', '1000+']
    validos_group["length_category"] = pd.Categorical(validos_group["length_category"], categories=categories_order, ordered=True)
    validos_group = validos_group.sort_values(by="length_category")

    fig7_global = px.bar(
        validos_group,
        x="length_category",
        y="cantidad",
        title="✅ Longitud de Inputs Válidos",
        color="cantidad",
        color_continuous_scale=px.colors.sequential.Greens
    )
    fig7_global.update_layout(coloraxis_showscale=False, showlegend=False)


    # 🧪 Gráfico global 8: Longitud de Inputs con Fallos (global)

    fallos = df_global[df_global["fallo"] == True]
    fallos_group = fallos.groupby("length_category").size().reset_index(name='cantidad')
    fallos_group["length_category"] = pd.Categorical(fallos_group["length_category"], categories=categories_order, ordered=True)
    fallos_group = fallos_group.sort_values(by="length_category")

    fig8_global = px.bar(
        fallos_group,
        x="length_category",
        y="cantidad",
        title="❌ Longitud de Inputs con Fallos",
        color="cantidad",
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig8_global.update_layout(coloraxis_showscale=False, showlegend=False)




    global_cards = [card(fig1_global), card(fig3_global), card(fig2_global), card(fig4_global), card(fig5_global), card(fig6_global), card(fig7_global),card(fig8_global)]

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
    df_sesion = df_sesion.drop_duplicates(subset=["input", "exit_code"])

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

    df_sesion["input_length"] = df_sesion["input"].apply(len)

    fig3_sesion = px.histogram(
        df_sesion,
        x="input_length",
        nbins=20,
        title="📐 Longitudes de inputs",
        labels={"input_length": "Longitud del input"},
        color_discrete_sequence=["#636EFA"]
    )
    fig3_sesion.update_traces(marker_line_width=1, marker_line_color="white")

    conteos_inputs = df_sesion["input"].value_counts()
    unicos = (conteos_inputs == 1).sum()
    repetidos = (conteos_inputs > 1).sum()

    df_diversidad = pd.DataFrame({
        "Tipo": ["Únicos", "Repetidos"],
        "Cantidad": [unicos, repetidos]
    })

    fig4_sesion = px.bar(
        df_diversidad,
        x="Tipo",
        y="Cantidad",
        title="🔁 Inputs únicos vs repetidos",
        color="Tipo",
        color_discrete_map={"Únicos": "steelblue", "Repetidos": "darkorange"}
    )

    inputs_repetidos = conteos_inputs[conteos_inputs > 1].reset_index()
    inputs_repetidos.columns = ["input", "veces"]

    mitad = math.ceil(len(inputs_repetidos) / 2)
    tabla_1 = inputs_repetidos.iloc[:mitad]
    tabla_2 = inputs_repetidos.iloc[mitad:]

    tabla_repetidos_sesion = html.Div([
        html.H4("📄 Inputs repetidos en la sesión"),
        dcc.Loading(
            id='loading-inputs-repetidos',
            type="circle",            # Tipo de spinner (círculo)
            color="#2c3e50",          # Color del spinner (puedes modificarlo)
            children=html.Div(
                style={"display": "flex", "gap": "30px"},
                children=[
                    dash_table.DataTable(
                        data=tabla_1.to_dict("records"),
                        columns=[{"name": col, "id": col} for col in tabla_1.columns],
                        style_table={
                            "width": "100%",
                            "tableLayout": "fixed",
                            "overflowX": "auto"
                        },
                        style_cell={"textAlign": "left", "padding": "6px"},
                        style_header={"backgroundColor": "#f9f9f9", "fontWeight": "bold"}
                    ),
                    dash_table.DataTable(
                        data=tabla_2.to_dict("records"),
                        columns=[{"name": col, "id": col} for col in tabla_2.columns],
                        style_table={
                            "width": "100%",
                            "tableLayout": "fixed",
                            "overflowX": "auto"
                        },
                        style_cell={"textAlign": "left", "padding": "6px"},
                        style_header={"backgroundColor": "#f9f9f9", "fontWeight": "bold"}
                    )
                ]
            )
        )
    ], style={"marginTop": "20px"})
    # 🧪 Gráfico sesión 5: Longitud de Inputs Válidos (sesión)

    df_sesion["input_length"] = df_sesion["input"].apply(len)

    def categorizar_longitud(x):
        if x <= 50:
            return '0-50'
        elif x <= 100:
            return '51-100'
        elif x <= 300:
            return '101-300'
        elif x <= 1000:
            return '301-1000'
        else:
            return '1000+'

    df_sesion["length_category"] = df_sesion["input_length"].apply(categorizar_longitud)

    validos_sesion = df_sesion[df_sesion["exit_code"] == 0]
    validos_sesion_group = validos_sesion.groupby("length_category").size().reset_index(name='cantidad')

    categories_order = ['0-50', '51-100', '101-300', '301-1000', '1000+']
    validos_sesion_group["length_category"] = pd.Categorical(validos_sesion_group["length_category"], categories=categories_order, ordered=True)
    validos_sesion_group = validos_sesion_group.sort_values(by="length_category")

    fig5_sesion = px.bar(
        validos_sesion_group,
        x="length_category",
        y="cantidad",
        title="✅ Longitud de Inputs Válidos por Sesión",
        color="cantidad",
        color_continuous_scale=px.colors.sequential.Greens
    )
    fig5_sesion.update_layout(coloraxis_showscale=False, showlegend=False)


    # 🧪 Gráfico sesión 6: Longitud de Inputs con Fallos (sesión)

    fallos_sesion = df_sesion[df_sesion["exit_code"] != 0]
    fallos_sesion_group = fallos_sesion.groupby("length_category").size().reset_index(name='cantidad')
    fallos_sesion_group["length_category"] = pd.Categorical(fallos_sesion_group["length_category"], categories=categories_order, ordered=True)
    fallos_sesion_group = fallos_sesion_group.sort_values(by="length_category")

    fig6_sesion = px.bar(
        fallos_sesion_group,
        x="length_category",
        y="cantidad",
        title="❌ Longitud de Inputs con Fallos por Sesión",
        color="cantidad",
        color_continuous_scale=px.colors.sequential.Reds
    )
    fig6_sesion.update_layout(coloraxis_showscale=False, showlegend=False)


    session_cards = [card(fig1_sesion), card(fig2_sesion), card(fig3_sesion), card(fig4_sesion), tabla_repetidos_sesion,card(fig5_sesion),card(fig6_sesion)]

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
        return []  # Al eliminar sesión, vacía directamente el contenido sin esperar
    time.sleep(1)
    _, session_cards = generar_graficos(df, programa=programa, sesion=sesion)
    return session_cards


# ───────────────────────────────
# ▶️ LANZAR LA APP
# ───────────────────────────────
if __name__ == "__main__":
    app.run(debug=True)