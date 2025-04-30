import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from dash import html
from utils import card, crear_grafico_bar, categorizar_longitud

def grafico_validos_vs_errores_global(df):
    valid_vs_errors = pd.DataFrame({
        "Tipo": ["Válidos", "Errores"],
        "Cantidad": [
            (df["fallo"] == False).sum(),
            (df["fallo"] == True).sum()
        ]
    })
    return card(crear_grafico_bar(valid_vs_errors, "Tipo", "Cantidad", "Cantidad de válidos vs errores", color="Tipo", color_discrete_sequence=["green", "red"]))

def grafico_codigos_error_global(df):
    errores_df = df[df["exit_code"] != 0]
    exit_counts = errores_df["exit_code"].value_counts().sort_index().reset_index()
    exit_counts.columns = ["Código de error", "Frecuencia"]
    exit_counts["Código de error"] = exit_counts["Código de error"].astype(str)
    return card(crear_grafico_bar(exit_counts, "Código de error", "Frecuencia", "Distribución de códigos de error", color="Código de error"))

def grafico_inputs_por_sesion(df):
    inputs_por_sesion = df.groupby("session_id")["input"].count().reset_index(name="total_inputs")
    return card(crear_grafico_bar(inputs_por_sesion, "session_id", "total_inputs", "📥 Cantidad de inputs por sesión", color="total_inputs", color_continuous_scale=px.colors.sequential.Blues))

def grafico_errores_por_sesion(df):
    errores_sesion = df[df["fallo"]].groupby("session_id").size().reset_index(name="Errores")
    return card(crear_grafico_bar(errores_sesion, "session_id", "Errores", "❌ Número de errores por sesión", color="session_id"))

def grafico_duracion_sesiones(df):
    df = df[df["fecha_inicio"].notna() & df["fecha_fin"].notna() & df["hora_inicio"].notna() & df["hora_fin"].notna()]
    duraciones = []
    for sesion_id in df["session_id"].unique():
        sub_df = df[df["session_id"] == sesion_id].sort_values(by=["fecha_inicio", "hora_inicio"])
        try:
            dt_inicio = pd.to_datetime(f"{sub_df['fecha_inicio'].iloc[0]} {pd.Timestamp('00:00:00') + sub_df['hora_inicio'].iloc[0]:%H:%M:%S}")
            dt_fin = pd.to_datetime(f"{sub_df['fecha_fin'].iloc[-1]} {pd.Timestamp('00:00:00') + sub_df['hora_fin'].iloc[-1]:%H:%M:%S}")
            duraciones.append({"session_id": sesion_id, "duracion_min": round((dt_fin - dt_inicio).total_seconds() / 60, 2)})
        except Exception as e:
            print(f"Error al calcular duración de la sesión {sesion_id}: {e}")
    df_duracion = pd.DataFrame(duraciones)
    return card(crear_grafico_bar(df_duracion, "session_id", "duracion_min", "⏱️ Duración de las sesiones", color="duracion_min", color_continuous_scale=px.colors.sequential.Tealgrn))

def grafico_radar_programa():
    categorias = ['Metrica 1', 'Metrica 2', 'Metrica 3', 'Metrica 4', 'Metrica 5']
    valores = [80, 70, 85, 75, 90]
    categorias_con_valores = [f"{cat}<br>{val}" for cat, val in zip(categorias, valores)]
    fig = go.Figure()
    fig.add_trace(go.Scatterpolar(r=valores + [valores[0]], theta=categorias_con_valores + [categorias_con_valores[0]], fill='toself'))
    fig.update_layout(polar=dict(radialaxis=dict(visible=True, range=[0, 100])), showlegend=False, title="Evaluación del programa")
    return card(fig)

def grafico_longitud_inputs_global(df, exito=True):
    fallo = df["fallo"]
    texto = "✅ Longitud de Inputs Válidos" if exito else "❌ Longitud de Inputs con Fallos"
    colores = px.colors.sequential.Greens if exito else px.colors.sequential.Reds
    filtro = ~fallo if exito else fallo
    orden = ['0-50', '51-100', '101-300', '301-1000', '1000+']
    grupo = df[filtro].groupby("length_category").size().reset_index(name='cantidad')
    grupo["length_category"] = pd.Categorical(grupo["length_category"], categories=orden, ordered=True)
    return card(crear_grafico_bar(grupo.sort_values("length_category"), "length_category", "cantidad", texto, color="cantidad", color_continuous_scale=colores))

def generar_graficos_globales(df_base, programa):
    df_global = df_base[df_base["programa"] == programa].copy()
    df_global = df_global.drop_duplicates(subset=["input", "exit_code"])
    df_global["exit_code"] = df_global["exit_code"].astype(int)
    df_global["fallo"] = df_global["exit_code"] != 0
    df_global["input_length"] = df_global["input"].apply(len)
    df_global["length_category"] = df_global["input_length"].apply(categorizar_longitud)

    return [
        grafico_validos_vs_errores_global(df_global),
        grafico_inputs_por_sesion(df_global),
        grafico_codigos_error_global(df_global),
        grafico_errores_por_sesion(df_global),
        grafico_duracion_sesiones(df_global),
        grafico_radar_programa(),
        grafico_longitud_inputs_global(df_global, exito=True),
        grafico_longitud_inputs_global(df_global, exito=False)
    ]

