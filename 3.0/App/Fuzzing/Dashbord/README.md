# 📊 Dashboard Fuzzing — Documentación de Código

Este proyecto visualiza los resultados de fuzzing usando Dash, Plotly y Pandas, con análisis global y por sesión.

---

## 📁 Estructura del Proyecto

| Archivo                        | Rol principal                                                      |
|-------------------------------|---------------------------------------------------------------------|
| `dash2.py`                    | Lanza la app Dash, gestiona el layout y los callbacks              |
| `config_db.py`                | Establece la conexión a la base de datos                           |
| `utils.py`                    | Contiene funciones auxiliares para estilizar y crear gráficos      |
| `graficos_sesion.py` | Contiene los gráficos de análisis de una sesión específica         |
| `graficos_globales.py`| Contiene los gráficos de análisis global por programa              |

---

## 🧩 `utils.py`

Funciones auxiliares comunes:

| Función                   | Descripción                                                                 |
|---------------------------|-----------------------------------------------------------------------------|
| `card(fig)`               | Estiliza un gráfico dentro de una tarjeta visual                           |
| `crear_grafico_bar(...)`  | Crea un gráfico de barras estandarizado                                     |
| `categorizar_longitud(x)` | Clasifica la longitud de un input en rangos: `0-50`, `51-100`, ..., `1000+` |

---

## 🔷 `graficos_globales.py`

Funciones para análisis por **programa**:

| Función                                 | Descripción                                                             |
|-----------------------------------------|-------------------------------------------------------------------------|
| `grafico_validos_vs_errores_global(df)`| Muestra válidos vs errores globalmente                                  |
| `grafico_codigos_error_global(df)`     | Muestra la distribución de códigos de error                             |
| `grafico_inputs_por_sesion(df)`        | Muestra cuántos inputs se generaron por sesión                          |
| `grafico_errores_por_sesion(df)`       | Muestra cuántos errores hubo por sesión                                 |
| `grafico_duracion_sesiones(df)`        | Calcula la duración total de cada sesión                                |
| `grafico_radar_programa()`             | Radar de métricas del programa (actualmente con valores estáticos)      |
| `grafico_longitud_inputs_global(df, exito=True/False)` | Longitud de inputs válidos o fallidos                        |
| `generar_graficos_globales(df_base, programa)` | Llama a todos los anteriores y devuelve las tarjetas             |

---

## 🔶 `graficos_sesion.py`

Funciones para análisis de una **sesión concreta**:

| Función                             | Descripción                                                             |
|-------------------------------------|-------------------------------------------------------------------------|                         
| `grafico_errores_por_codigo(df)`   | Muestra códigos de error únicos en la sesión                            |
| `grafico_validos_vs_errores(df)`   | Comparativa entre válidos y errores                                     |
| `grafico_longitud_histograma(df)`  | Histograma de longitudes de inputs                                      |
| `grafico_inputs_unicos_repetidos(df)` | Conteo de inputs únicos vs repetidos                                |
| `tabla_inputs_repetidos(df)`       | Tabla visual de inputs repetidos en dos columnas                        |
| `grafico_longitud_inputs(df, exito=True/False)` | Longitud de inputs válidos o fallidos                         |
| `generar_graficos_sesion(df_base, programa, sesion)` | Ejecuta todos los gráficos para una sesión                  |

---

## 🚀 `dash2.py` (archivo principal de la app)

### Contenido clave:

- **Conexión a la base de datos**
- **Layout** con filtros de programa/sesión
- **Callbacks** que actualizan gráficos globales y de sesión
- **`generar_graficos()`**:
  - Llama a `generar_graficos_globales(...)`
  - Llama a `generar_graficos_sesion(...)` si hay sesión seleccionada