import pandas as pd
from scipy.spatial import KDTree
import numpy as np
import matplotlib.pyplot as plt
import streamlit as st
import time
import psutil


### CUANTOS RECURSOS CONSUME EL PROGRAMA ###
def get_resource_info(code_to_measure):
    resources_save_data = get_resource_usage(code_to_measure=code_to_measure)
    print(f"Tiempo de CPU: {resources_save_data['tiempo_cpu']} segundos")
    print(f"Uso de memoria virtual: {resources_save_data['memoria_virtual']} MB")
    print(f"Uso de memoria residente: {resources_save_data['memoria_residente']} MB")
    print(f"Porcentaje de uso de CPU: {resources_save_data['%_cpu']} %")

def get_resource_usage(code_to_measure):
    process = psutil.Process()
    #get cpu status before running the code
    cpu_percent = psutil.cpu_percent()
    start_time = time.time()
    code_to_measure()
    end_time = time.time()
    end_cpu_percent = psutil.cpu_percent() 
    cpu_percent = end_cpu_percent - cpu_percent
    cpu_percent = cpu_percent / psutil.cpu_count()
    
    return {
        'tiempo_cpu': end_time - start_time,
        'memoria_virtual': process.memory_info().vms / (1024 * 1024),  # Convertir a MB
        'memoria_residente': process.memory_info().rss / (1024 * 1024),  # Convertir a MB
        '%_cpu': cpu_percent # Porcentaje de uso de CPU
    }


def calculo_velocidad(grupo):
    distancia = np.sqrt((grupo['X'].diff(periods = 1))**2 + (grupo['Y'].diff(periods = 1))**2)
    tiempo = 1/25
    grupo['velocidad'] = distancia / tiempo
    return grupo


def mi_programa_1():
    data_frame_01 = pd.read_csv('Laboratorio-04/dataset/UNI_CORR_500_01.txt', delimiter="\t", skiprows=3)
    #print(data_frame_01.tail())


    grupo_01 = data_frame_01.groupby('# PersID', group_keys=False)
    df_vel_01 = grupo_01.apply(calculo_velocidad)
    #print(df_vel_01.head())

    #df_vel_01.to_csv(f"velocidades_01.csv", index=False, sep='\t')


    promedio_por_ID_01 = df_vel_01.groupby('# PersID')['velocidad'].mean()
    #print(promedio_por_ID_01)

    st.write("""
    # Laboratorio 04 Programación Científica
    ## Cálculo Sk y graficos de archivo UNI_CORR_500_01.txt
    """)
    st.write("""
    ## Histograma de la frecuencia de la velocidad promedio
    """)

    # Crear un histograma
    fig, ax = plt.subplots(figsize=(10,6))
    ax.hist(promedio_por_ID_01, bins=10, edgecolor='salmon', color='pink') 
    ax.set_xlabel('Promedio velocidad')
    ax.set_ylabel('Frecuencia')
    ax.set_title('Histograma UNI_CORR_500_01', loc='center', fontdict = {'fontsize':14,'fontweight':'bold','color':'black'})
    #plt.show() 
    st.pyplot(fig)

    # Obtener la lista de frames únicos
    frames_unicos = data_frame_01['Frame'].unique()

    # Radio de búsqueda
    radius = 3.0


    df_vel_01['sk'] = np.nan

    for frame_interes in frames_unicos:
        #print(f'|{"*" * 40}|')
        #print(f'Frame de interés: {frame_interes}')
    
        # Filtrar el DataFrame por el frame de interés
        df_frame = data_frame_01[data_frame_01['Frame'] == frame_interes]
    
        # Crear un array Numpy con las coordenadas
        coordinates = df_frame[['X', 'Y']].values
    
        # Crear un árbol KD con las coordenadas
        tree = KDTree(coordinates)
    
    

        for peaton_index in range(len(coordinates)):
            #print(f'Peatón de interés: {df_frame.iloc[peaton_index]}')
        
            # Coordenadas del peatón de interés
            query_point = coordinates[peaton_index]
        
            # Encontrar índices de peatones cercanos en el radio dado
            neighbor_indices = tree.query_ball_point(query_point, radius)
            neighbor_indices = [index for index in neighbor_indices if index != peaton_index]
        
            #print('Peatones cercanos en el mismo frame:')
            #for index in neighbor_indices:
                #print(df_frame.iloc[index].head())
    
            # Calcular sk
            num_neighbors = len(neighbor_indices)
            sk_sum = 0.0
         
            for index in neighbor_indices:
                dx = query_point[0] - coordinates[index][0]
                dy = query_point[1] - coordinates[index][1]
                sk_sum += np.sqrt(dx**2 + dy**2)
        
            if num_neighbors > 0:
                sk = (1.0 / num_neighbors) * sk_sum
                df_vel_01.at[df_frame.index[peaton_index], 'sk'] = sk

                #print(f'sk del peatón {int(df_frame.iloc[peaton_index][0])} en el frame {frame_interes}: {sk}')
            #else:
                #print('No hay peatones cercanos.')

    #print(df_vel_01.head(10))
    df_vel_01.to_csv(f"velocidades_01.txt", index=False, sep='\t')

    st.write("""
    ## Gráfico de dispersión Sk vs Velocidad
    """)

    # Crear el gráfico de dispersión
    figu, ax = plt.subplots(figsize=(10,6))
    #plt.figure(figsize=(10, 6))
    ax.scatter(x=df_vel_01['sk'], y=df_vel_01['velocidad'], color='blue', alpha=0.5)
    ax.set_xlabel('sk')
    ax.set_ylabel('Velocidad')
    ax.set_title('Gráfico de Dispersión: sk vs. Velocidad')
    ax.grid(True)
    #plt.show()
    st.pyplot(figu)

if __name__ == "__main__":
    print('|' + '*'*85 + '|')
    print('Los recursos utilizados por el programa 1 con el data set "UNI_CORR_500_01.txt" son: ')
    get_resource_info(mi_programa_1)