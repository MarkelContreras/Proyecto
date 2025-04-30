import pandas as pd
import plotly.express as px
from dash import html, dash_table, dcc
import math
from utils import card, crear_grafico_bar, categorizar_longitud

def grafico_errores_por_codigo(df):
    errores = df[df["exit_code"] != 0]["exit_code"].value_counts().sort_index().reset_index()
    errores.columns = ["Código", "Frecuencia"]
    errores["Código"] = errores["Código"].astype(str)
    return card(crear_grafico_bar(errores, "Código", "Frecuencia", "❗ Códigos de error en la sesión", color="Código"))

def grafico_validos_vs_errores(df):
    conteo = pd.DataFrame({
        "Tipo": ["Válidos", "Errores"],
        "Cantidad": [
            (df["exit_code"] == 0).sum(),
            (df["exit_code"] != 0).sum()
        ]
    })
    return card(crear_grafico_bar(conteo, "Tipo", "Cantidad", "✅ Válidos vs ❌ Errores en la sesión", color="Tipo", color_discrete_sequence=["green", "red"]))

def grafico_longitud_histograma(df):
    fig = px.histogram(
        df,
        x="input_length",
        nbins=20,
        title="📐 Longitudes de inputs",
        labels={"input_length": "Longitud del input"},
        color_discrete_sequence=["#636EFA"]
    )
    fig.update_traces(marker_line_width=1, marker_line_color="white")
    return card(fig)

def grafico_inputs_unicos_repetidos(df):
    conteos = df["input"].value_counts()
    unicos = (conteos == 1).sum()
    repetidos = (conteos > 1).sum()
    df_div = pd.DataFrame({"Tipo": ["Únicos", "Repetidos"], "Cantidad": [unicos, repetidos]})
    return card(crear_grafico_bar(df_div, "Tipo", "Cantidad", "🔁 Inputs únicos vs repetidos", color="Tipo", color_discrete_sequence=["steelblue", "darkorange"]))

def tabla_inputs_repetidos(df):
    conteos = df["input"].value_counts()
    repetidos = conteos[conteos > 1].reset_index()
    repetidos.columns = ["input", "veces"]
    mitad = math.ceil(len(repetidos) / 2)
    tabla_1, tabla_2 = repetidos.iloc[:mitad], repetidos.iloc[mitad:]

    return html.Div([
        html.H4("📄 Inputs repetidos en la sesión"),
        dcc.Loading(
            id='loading-inputs-repetidos',
            type="circle",
            color="#2c3e50",
            children=html.Div(style={"display": "flex", "gap": "30px"}, children=[
                dash_table.DataTable(
                    data=tabla_1.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in tabla_1.columns],
                    style_table={"width": "100%", "tableLayout": "fixed", "overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "6px"},
                    style_header={"backgroundColor": "#f9f9f9", "fontWeight": "bold"}
                ),
                dash_table.DataTable(
                    data=tabla_2.to_dict("records"),
                    columns=[{"name": col, "id": col} for col in tabla_2.columns],
                    style_table={"width": "100%", "tableLayout": "fixed", "overflowX": "auto"},
                    style_cell={"textAlign": "left", "padding": "6px"},
                    style_header={"backgroundColor": "#f9f9f9", "fontWeight": "bold"}
                )
            ])
        )
    ], style={"marginTop": "20px"})

def grafico_longitud_inputs(df, exito=True):
    estado = 0 if exito else 1
    texto = "✅ Longitud de Inputs Válidos por Sesión" if exito else "❌ Longitud de Inputs con Fallos por Sesión"
    colores = px.colors.sequential.Greens if exito else px.colors.sequential.Reds
    filtro = df["exit_code"] == 0 if exito else df["exit_code"] != 0

    orden = ['0-50', '51-100', '101-300', '301-1000', '1000+']
    grupo = df[filtro].groupby("length_category").size().reset_index(name='cantidad')
    grupo["length_category"] = pd.Categorical(grupo["length_category"], categories=orden, ordered=True)
    return card(crear_grafico_bar(grupo.sort_values("length_category"), "length_category", "cantidad", texto, color="cantidad", color_continuous_scale=colores))

def generar_graficos_sesion(df_base, programa, sesion):
    df_sesion = df_base[(df_base["programa"] == programa) & (df_base["session_id"] == sesion)].copy()
    df_sesion["exit_code"] = df_sesion["exit_code"].astype(int)
    df_sesion = df_sesion.drop_duplicates(subset=["input", "exit_code"])
    df_sesion["input_length"] = df_sesion["input"].apply(len)
    df_sesion["length_category"] = df_sesion["input_length"].apply(categorizar_longitud)

    return [
        grafico_errores_por_codigo(df_sesion),
        grafico_validos_vs_errores(df_sesion),
        grafico_longitud_histograma(df_sesion),
        grafico_inputs_unicos_repetidos(df_sesion),
        tabla_inputs_repetidos(df_sesion),
        grafico_longitud_inputs(df_sesion, exito=True),
        grafico_longitud_inputs(df_sesion, exito=False)
    ]
