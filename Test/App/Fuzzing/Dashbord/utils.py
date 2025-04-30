from dash import dcc, html
import plotly.express as px

def card(fig):
    return html.Div([dcc.Graph(figure=fig)], style={
        "backgroundColor": "#fff",
        "padding": "20px",
        "borderRadius": "12px",
        "boxShadow": "0 4px 8px rgba(0,0,0,0.1)"
    })

def crear_grafico_bar(df, x, y, title, color=None, color_discrete_sequence=None, color_continuous_scale=None, category_order=None, show_legend=False):
    fig = px.bar(
        df,
        x=x,
        y=y,
        title=title,
        color=color if color else x,
        color_discrete_sequence=color_discrete_sequence,
        color_continuous_scale=color_continuous_scale
    )
    if category_order:
        fig.update_xaxes(categoryorder='array', categoryarray=category_order)
    fig.update_layout(showlegend=show_legend, coloraxis_showscale=False)
    fig.update_xaxes(type="category", dtick=1)
    return fig

def categorizar_longitud(x):
    if x <= 50: return '0-50'
    elif x <= 100: return '51-100'
    elif x <= 300: return '101-300'
    elif x <= 1000: return '301-1000'
    return '1000+'