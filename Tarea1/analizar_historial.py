import csv
import os
import matplotlib.pyplot as plt

def graficar_historial_promediado():
    archivo_csv = "historial_benchmarks_hpc.csv"
    
    if not os.path.exists(archivo_csv):
        print(f"Error: No se encontró '{archivo_csv}'.")
        return

    # Diccionario para agrupar las ejecuciones repetidas
    datos_agrupados = {}

    print(f"Leyendo y promediando datos de {archivo_csv}...")
    with open(archivo_csv, mode='r', encoding='utf-8') as f:
        lector = csv.DictReader(f)
        for fila in lector:
            etiqueta = f"{fila['Resolucion']}\n({fila['Iteraciones_Max']}i)"
            
            # Si es la primera vez que vemos esta configuración, la inicializamos
            if etiqueta not in datos_agrupados:
                datos_agrupados[etiqueta] = {'py': [], 'np': [], 'cy': []}
            
            # Guardamos todos los intentos de esta configuración
            datos_agrupados[etiqueta]['py'].append(float(fila['T_Python_s']))
            datos_agrupados[etiqueta]['np'].append(float(fila['T_NumPy_s']))
            datos_agrupados[etiqueta]['cy'].append(float(fila['T_Cython_s']))

    # Listas finales para graficar (ya promediadas)
    etiquetas_x = []
    tiempos_py_avg = []
    tiempos_np_avg = []
    tiempos_cy_avg = []

    for etiqueta, tiempos in datos_agrupados.items():
        etiquetas_x.append(etiqueta)
        
        # Calcular el promedio (Suma de los tiempos / Cantidad de intentos)
        promedio_py = sum(tiempos['py']) / len(tiempos['py'])
        promedio_np = sum(tiempos['np']) / len(tiempos['np'])
        promedio_cy = sum(tiempos['cy']) / len(tiempos['cy'])
        
        tiempos_py_avg.append(promedio_py)
        tiempos_np_avg.append(promedio_np)
        tiempos_cy_avg.append(promedio_cy)
        
        etiqueta_sin_saltos = etiqueta.replace('\n', ' ')
        print(f"  -> {etiqueta_sin_saltos}: Promediado sobre {len(tiempos['py'])} ejecución(es).")

    # --- Creación del Gráfico ---
    plt.figure(figsize=(10, 6))
    
    plt.plot(etiquetas_x, tiempos_py_avg, marker='o', color='#e74c3c', label='Python Puro', linewidth=2)
    plt.plot(etiquetas_x, tiempos_np_avg, marker='s', color='#3498db', label='NumPy', linewidth=2)
    plt.plot(etiquetas_x, tiempos_cy_avg, marker='^', color='#2ecc71', label='Cython', linewidth=2)

    plt.title('Rendimiento HPC Promediado según Carga de Trabajo', fontsize=14, pad=20)
    plt.xlabel('Configuración de Entrada (Resolución e Iteraciones)', fontsize=12, labelpad=10)
    plt.ylabel('Tiempo Promedio (Segundos)', fontsize=12)
    
    # Activar escala logarítmica si lo deseas (descomenta la siguiente línea)
    # plt.yscale('log')
    
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.legend(fontsize=11)
    plt.tight_layout()
    
    nombre_salida = "grafico_tendencias_promediado.png"
    plt.savefig(nombre_salida, dpi=300)
    print(f"\n-> Gráfico guardado exitosamente como: {nombre_salida}")
    plt.show()

if __name__ == "__main__":
    graficar_historial_promediado()