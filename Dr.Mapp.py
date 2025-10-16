# Dr. Mapp
# Access app via: https://dr-mapp.streamlit.app/

# Cargamos las librerías necesarias
import streamlit as st
import pandas as pd
import folium
from geopy.distance import geodesic
from geopy.geocoders import Nominatim

global df_filtrado_global

# Definimos el fondo
page_bg_img = '''
<style>
.stApp {
    background-color: #FFFFFF;
}
</style>
'''
st.markdown(page_bg_img, unsafe_allow_html=True)


# Insertamos el logo y el título
# Crear columnas vacías para centrar la imagen
col1, col2, col3 = st.columns([1, 2, 1])

# Usar col2 para centrar la imagen
with col2:
    st.image("./dr_mapp_01.jpg", width=300)

# Centrar un título usando HTML y CSS
st.markdown("<h1 style='text-align: center;'>¡Podemos ayudarte a encontrar el establecimiento de salud más cercano!</h1>", unsafe_allow_html=True)
#st.title('¡Podemos ayudarte a encontrar el establecimiento de salud más cercano!')
# Línea divisora
st.markdown("---")
st.markdown("<h2 style='text-align: center;'>Dinos dónde estás y qué distancia puedes recorrer.</h2>", unsafe_allow_html=True)
#st.header('Dinos dónde estás y qué distancia puedes recorrer.')


# Cargo los datos del rígido
filepath_HD = 'establecimientos_salud_todos_limpio.csv'
df_final = pd.read_csv(filepath_HD)
df_final.dropna(inplace=True)


# Función para convertir una dirección en coordenadas
def direccion_a_coordenadas(direccion):
    # Inicializar el geocodificador
    geolocator = Nominatim(user_agent="mi_aplicacion_geopy")

    # Obtener la ubicación a partir de la dirección
    ubicacion = geolocator.geocode(direccion)

    # Verificar si se encontró la dirección
    if ubicacion:
        return (ubicacion.latitude, ubicacion.longitude)
    else:
        return None

# Función para calcular la distancia entre dos puntos usando Haversine
def calcular_distancia(lat1, lon1, lat2, lon2):
    point1 = (lat1, lon1)
    point2 = (lat2, lon2)
    return geodesic(point1, point2).kilometers

# Función para encontrar las 10 localizaciones más cercanas
#def encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset, n, distanciamax):
def encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset, distanciamax):
    # Crear una lista para almacenar las distancias calculadas
    distancias = []
    cantidad_establecimientos = 0

    # Calcular la distancia para cada localización
    for index, row in dataset.iterrows():
        lat = row['LATITUD']
        lon = row['LONGITUD']
        nombre = row['NOMBRE']
        domicilio = row['DOMICILIO']
        servicio = row['CATEGORIA_TIPOLOGIA']

        # Calcular la distancia desde la referencia
        distancia = calcular_distancia(latitud_referencia, longitud_referencia, lat, lon)

        # Considerar los registros correspondientes a la distancia límite que puede viajar el usuario
        if distancia <= distanciamax:

          # Añadir el nombre de la ubicación y la distancia a la lista
          distancias.append({'nombre': nombre, 'latitud': lat, 'longitud': lon, 'distancia': distancia, 'domicilio': domicilio, 'servicio': servicio})
          cantidad_establecimientos += 1

    # Convertir la lista de distancias a un DataFrame
    distancias_df = pd.DataFrame(distancias)

    if distancias_df.empty:
        st.warning("Aún no hay resultados. Seleccione uno o más servicios, amplíe el rango de distancia máxima o reinicie la búsqueda.")
        st.stop()

    # Ordenar el DataFrame por la distancia en orden ascendente
    distancias_df = distancias_df.sort_values(by='distancia')

    # Devolver las 'n' localizaciones más cercanas
    return distancias_df.head(cantidad_establecimientos)


# EJECUCIÓN
# Solicitar la dirección al usuario
direccion = st.text_input('Ingresar la dirección (sin acentos, el formato es: dirección, ciudad, país): ')

if not direccion:
    st.stop()  # Detener la ejecución aquí

# Cantidad de establecimientos a mostrar
##cantidad = int(input("Ingrese la cantidad de establecimientos a mostrar: "))

# El usuario tiene que definir una distancia máxima para filtrar los establecimientos
dist_maxima = st.slider('Seleccionar distancia máxima (en KM): ', min_value=0, max_value=100)

if not dist_maxima or dist_maxima == 0:
    st.stop()  # Detener la ejecución aquí

# Convertir la dirección en coordenadas
try:
    coordenadas = direccion_a_coordenadas(direccion)



    latitud_ref = coordenadas[0]
    longitud_ref = coordenadas[1]

    # # Definir las opciones del desplegable, incluyendo la opción 'Todos'

    opciones = ['Todos'] + df_final['CATEGORIA_TIPOLOGIA'].unique().tolist()
    #opciones = df_final['CATEGORIA_TIPOLOGIA'].unique().tolist()
    opciones = sorted(opciones)
except TypeError as e:
    #st.error(f"Ocurrió un error: {e}")
    st.warning("Dirección no encontrada. Ingrese nuevamente el dato.")
    st.stop()

# ---------------- DUDA ----------------
# Acá intento adaptar la selección de tipos de estableciemietos al tipo de widget de streamlit

tipo_elegido = st.multiselect('Elegir el tipo de servicio/establecimiento: ', opciones)

# Lógica para restringir la selección
#if 'Todos' in tipo_elegido:


# Si se selecciona 'Todos', mostrar todo el DataFrame
if 'Todos' in tipo_elegido:  # Cambiar la condición para verificar si 'Todos' está en la lista
    
    # Si se selecciona 'Todos', deseleccionar las demás opciones
    tipo_elegido = ['Todos']
    st.warning("Al seleccionar 'Todos', no aplicarán otras opciones en la búsqueda.")
    df_filtrado_global = df_final
else:
# Filtrar el DataFrame según el servicio seleccionado
    df_filtrado_global = df_final[df_final['CATEGORIA_TIPOLOGIA'].isin(tipo_elegido)]

#df_filtrado_global = df_final[df_final['CATEGORIA_TIPOLOGIA'].isin(tipo_elegido)]

#print(df_flitrado_global)
# --------------------------------------

# Encontrar las localizaciones más cercanas
##localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_ref, longitud_ref, df_final, cantidad, dist_maxima)
localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_ref, longitud_ref, df_filtrado_global, dist_maxima)

# Mostrar las localizaciones cercanas, si existen
try:
    if localizaciones_cercanas is not None and not localizaciones_cercanas.empty:
    #if not localizaciones_cercanas.empty:
        #st.write(localizaciones_cercanas[['nombre', 'distancia', 'domicilio', 'servicio']])
        # Renombrar columnas
        localizaciones_cercanas.rename(columns={
        'nombre': 'Nombre del Establecimiento',
        'distancia': 'Distancia (km)',
        'domicilio': 'Dirección',
        'servicio': 'Tipo de Servicio'
        }, inplace=True)
        #st.dataframe(localizaciones_cercanas[['nombre', 'distancia', 'domicilio', 'servicio']], hide_index=True)

        # Mostrar el DataFrame sin el índice y con los nuevos nombres de columnas
        st.dataframe(localizaciones_cercanas[['Nombre del Establecimiento', 'Distancia (km)', 'Dirección', 'Tipo de Servicio']], hide_index=True)
    else:
        st.warning("No hay localizaciones dentro del rango especificado.")
        #st.write("No hay localizaciones dentro del rango especificado.")
except Exception as e:
    #st.error(f"Ocurrió un error: {e}")
    st.warning("No hay localizaciones dentro del rango especificado.")
    st.stop()




# ------------ Creamos el mapa -----------

from streamlit.components.v1 import html

# Función para generar el mapa con las localizaciones más cercanas
def generar_mapa_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset):
    # Encontrar las 5 localizaciones más cercanas
    ##localizaciones_cercanas = encontrar_localizaciones_cercanas(latitud_referencia, longitud_referencia, dataset)

    # Crear el mapa centrado en la localización de referencia
    mapa = folium.Map(location=[latitud_ref, longitud_ref], zoom_start=12)

    # Añadir un marcador para la localización de referencia
    folium.Marker(
        [latitud_ref, longitud_ref],
        popup="Punto de referencia",
        icon=folium.Icon(color='blue')
    ).add_to(mapa)

    # Añadir marcadores para las 10 localizaciones más cercanas
    for index, row in localizaciones_cercanas.iterrows():
        lat = row['latitud']
        lon = row['longitud']
        nombre = row['Nombre del Establecimiento']
        distancia = row['Distancia (km)']
        tipo = row['Tipo de Servicio']

        # Añadir un marcador para cada localización cercana
        folium.Marker(
            [lat, lon],
            popup=f"{nombre} | {tipo} ({distancia:.2f} km)",
            icon=folium.Icon(color='red')
        ).add_to(mapa)
    
    # Creamos una representación en HTML del mapa
    mapa_html = mapa._repr_html_()

    # Devolver el mapa
    return mapa_html


# Generar el mapa con las localizaciones más cercanas
mapa = generar_mapa_localizaciones_cercanas(latitud_ref, longitud_ref, df_filtrado_global)

# Mostrar el mapa
html(mapa, height=700)
