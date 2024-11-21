import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
import streamlit as st

# ATENCIÓN: Coloca la URL de tu aplicación de Streamlit aquí
# url = 'https://tp-8-59158-luciano-corral.streamlit.app'  # URL del deploy

# Función para mostrar la información de los alumnos
def mostrar_informacion_alumno():
    st.markdown('**Legajo:** 59.158')
    st.markdown('**Nombre:** Luciano Corral')
    st.markdown('**Comisión:** C7')

# Función para cargar el archivo CSV desde el sidebar
def cargar_archivo():
    archivo = st.sidebar.file_uploader("Sube un archivo CSV", type="csv")
    if archivo:
        return pd.read_csv(archivo)
    return None

# Función para calcular las métricas y generar los gráficos
def calcular_metricas_y_graficos(datos, sucursal):
    # Filtramos por sucursal si no es "Todas"
    if sucursal != "Todas":
        datos = datos[datos["Sucursal"] == sucursal]

    productos = datos["Producto"].unique()
    for producto in productos:
        datos_producto = datos[datos["Producto"] == producto]

        # Validaciones de datos
        if datos_producto["Ingreso_total"].isnull().any() or datos_producto["Unidades_vendidas"].isnull().any():
            st.error(f"El producto '{producto}' tiene valores nulos.")
            continue
        if (datos_producto["Ingreso_total"] < 0).any():
            st.error(f"El producto '{producto}' tiene valores negativos en 'Ingreso_total'.")
            continue
        if (datos_producto["Unidades_vendidas"] <= 0).any():
            st.error(f"El producto '{producto}' tiene valores no positivos en 'Unidades_vendidas'.")
            continue

        # Cálculo de las métricas
        unidades_vendidas = datos_producto["Unidades_vendidas"].sum()
        ingreso_total = datos_producto["Ingreso_total"].sum()
        costo_total = datos_producto["Costo_total"].sum()

        precio_promedio = ingreso_total / unidades_vendidas
        margen_promedio = (ingreso_total - costo_total) / ingreso_total * 100

        # Cálculo de precios y márgenes de 2023 y 2024
        precio_promedio_2024 = calcular_precio_promedio_por_anio(datos_producto, 2024)
        precio_promedio_2023 = calcular_precio_promedio_por_anio(datos_producto, 2023)

        margen_promedio_2024 = calcular_margen_promedio_por_anio(datos_producto, 2024)
        margen_promedio_2023 = calcular_margen_promedio_por_anio(datos_producto, 2023)

        # Unidades vendidas en 2024 y 2023
        unidades_2024 = calcular_unidades_por_anio(datos_producto, 2024)
        unidades_2023 = calcular_unidades_por_anio(datos_producto, 2023)

        # Mostrar métricas en la interfaz de Streamlit
        st.header(f"{producto}")
        st.metric("Precio Promedio", f"${precio_promedio:,.2f}", delta=f"{((precio_promedio_2024 / precio_promedio_2023) - 1) * 100:.2f}%")
        st.metric("Margen Promedio", f"{margen_promedio:.2f}%", delta=f"{((margen_promedio_2024 / margen_promedio_2023) - 1) * 100:.2f}%")
        st.metric("Unidades Vendidas", f"{unidades_vendidas:,}", delta=f"{((unidades_2024 / unidades_2023) - 1) * 100:.2f}%")

        # Preparar los datos para el gráfico
        datos_producto['Fecha'] = pd.to_datetime(datos_producto['Año'].astype(str) + '-' + datos_producto['Mes'].astype(str) + '-01')
        datos_producto.sort_values('Fecha', inplace=True)

        # Generación del gráfico de evolución de ventas
        fig, ax = plt.subplots(figsize=(10, 6))
        ax.plot(datos_producto["Fecha"], datos_producto["Unidades_vendidas"], label=f"Ventas de {producto}", color="blue")

        # Agregar la línea de tendencia
        x = np.arange(len(datos_producto))
        y = datos_producto["Unidades_vendidas"].values
        slope, intercept, _, _, _ = stats.linregress(x, y)
        tendencia = slope * x + intercept
        ax.plot(datos_producto["Fecha"], tendencia, label="Tendencia", color="red", linestyle="--")

        ax.set_title(f"Evolución de Ventas Mensual - {producto}", fontsize=14)
        ax.set_xlabel("Fecha", fontsize=12)
        ax.set_ylabel("Unidades Vendidas", fontsize=12)
        ax.legend(loc="upper left")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# Funciones auxiliares para el cálculo de métricas anuales
def calcular_precio_promedio_por_anio(datos_producto, anio):
    df_anio = datos_producto[datos_producto["Año"] == anio]
    return df_anio["Ingreso_total"].sum() / df_anio["Unidades_vendidas"].sum() if df_anio["Unidades_vendidas"].sum() > 0 else 0

def calcular_margen_promedio_por_anio(datos_producto, anio):
    df_anio = datos_producto[datos_producto["Año"] == anio]
    ingreso_total = df_anio["Ingreso_total"].sum()
    costo_total = df_anio["Costo_total"].sum()
    return (ingreso_total - costo_total) / ingreso_total * 100 if ingreso_total > 0 else 0

def calcular_unidades_por_anio(datos_producto, anio):
    df_anio = datos_producto[datos_producto["Año"] == anio]
    return df_anio["Unidades_vendidas"].sum()

# Función principal para ejecutar la aplicación
def main():
    st.sidebar.title("Carga de Datos de Ventas")
    mostrar_informacion_alumno()

    # Cargar el archivo CSV
    datos = cargar_archivo()
    if datos is not None:
        sucursales = ["Todas"] + datos["Sucursal"].unique().tolist()
        sucursal_seleccionada = st.sidebar.selectbox("Seleccionar Sucursal", sucursales)

        st.header(f"Datos de {'Todas las Sucursales' if sucursal_seleccionada == 'Todas' else sucursal_seleccionada}")
        calcular_metricas_y_graficos(datos, sucursal_seleccionada)
    else:
        st.write("Por favor, sube un archivo CSV desde la barra lateral.")

# Ejecutar la aplicación
if __name__ == "__main__":
    main()
