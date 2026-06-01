import time
import argparse
import os
import csv
import gc
import psutil
from datetime import datetime
import matplotlib.pyplot as plt
import numpy as np
import pyximport
pyximport.install(setup_args={"include_dirs": np.get_include()})

from v1_python import calcular_julia_python
from v2_numpy import calcular_julia_numpy
from julia_cython import calcular_julia_cython

def perfilar_recursos(etiqueta, func, *args):
    """Ejecuta una función y mide su consumo de RAM y CPU de forma aislada."""
    print(f"-> Ejecutando {etiqueta}...")
    
    # 1. Forzar limpieza de memoria de ejecuciones anteriores
    gc.collect()
    
    # 2. Capturar estado base del sistema
    proceso = psutil.Process(os.getpid())
    mem_base = proceso.memory_info().rss
    cpu_base = proceso.cpu_times()
    inicio_reloj = time.perf_counter()
    
    # 3. Ejecutar la carga de trabajo
    resultado = func(*args)
    
    # 4. Capturar estado final
    fin_reloj = time.perf_counter()
    cpu_final = proceso.cpu_times()
    mem_final = proceso.memory_info().rss
    
    # 5. Calcular deltas (diferencias)
    tiempo_total = fin_reloj - inicio_reloj
    cpu_user = cpu_final.user - cpu_base.user
    cpu_sys = cpu_final.system - cpu_base.system
    
    # Prevenir que la liberación instantánea muestre 0 o negativos
    mem_usada = max(0, mem_final - mem_base) / (1024 * 1024) # Convertir Bytes a Megabytes
    
    # Imprimir reporte en consola
    print(f"   [+] Tiempo Total: {tiempo_total:.4f} s | RAM: {mem_usada:.2f} MB")
    print(f"   [+] CPU User: {cpu_user:.4f} s | CPU Sys (Kernel): {cpu_sys:.4f} s\n")
    
    return resultado, tiempo_total, mem_usada, cpu_user, cpu_sys

def ejecutar_benchmark(width, height, max_iter):
    C = complex(-0.8, 0.156)
    datos_rendimiento = {}

    print(f"=== INICIANDO BENCHMARK HPC ({width}x{height} | {max_iter} iteraciones) ===\n")

    # V1: Python
    _, t_py, ram_py, usr_py, sys_py = perfilar_recursos("V1 (Python Puro)", calcular_julia_python, width, height, max_iter, C)
    datos_rendimiento['Python'] = {'tiempo': t_py, 'ram': ram_py, 'cpu_user': usr_py, 'cpu_sys': sys_py}

    # V2: NumPy
    _, t_np, ram_np, usr_np, sys_np = perfilar_recursos("V2 (NumPy Vectorizado)", calcular_julia_numpy, width, height, max_iter, C)
    datos_rendimiento['NumPy'] = {'tiempo': t_np, 'ram': ram_np, 'cpu_user': usr_np, 'cpu_sys': sys_np}

    # V3: Cython (Se guarda la matriz porque es la más eficiente)
    matriz_fractal, t_cy, ram_cy, usr_cy, sys_cy = perfilar_recursos("V3 (Cython Estático)", calcular_julia_cython, width, height, max_iter, C)
    datos_rendimiento['Cython'] = {'tiempo': t_cy, 'ram': ram_cy, 'cpu_user': usr_cy, 'cpu_sys': sys_cy}

    print("=== BENCHMARK FINALIZADO ===\nProcesando archivos e imágenes...")
    return datos_rendimiento, matriz_fractal

def guardar_historial_csv(datos, width, height, max_iter):
    directorio_actual = os.path.dirname(os.path.abspath(__file__))
    nombre_archivo = os.path.join(directorio_actual, "historial_benchmarks_hpc.csv")
    archivo_existe = os.path.isfile(nombre_archivo)
    
    fecha_actual = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    nombres_columnas = [
        'Fecha', 'Resolucion', 'Iteraciones_Max', 
        'T_Python_s', 'RAM_Python_MB', 'Sys_Python_s',
        'T_NumPy_s', 'RAM_NumPy_MB', 'Sys_NumPy_s',
        'T_Cython_s', 'RAM_Cython_MB', 'Sys_Cython_s'
    ]
    
    with open(nombre_archivo, mode='a', newline='', encoding='utf-8') as archivo_csv:
        escritor = csv.DictWriter(archivo_csv, fieldnames=nombres_columnas)
        
        if not archivo_existe:
            escritor.writeheader()
            
        escritor.writerow({
            'Fecha': fecha_actual,
            'Resolucion': f"{width}x{height}",
            'Iteraciones_Max': max_iter,
            
            'T_Python_s': round(datos['Python']['tiempo'], 4),
            'RAM_Python_MB': round(datos['Python']['ram'], 2),
            'Sys_Python_s': round(datos['Python']['cpu_sys'], 4),
            
            'T_NumPy_s': round(datos['NumPy']['tiempo'], 4),
            'RAM_NumPy_MB': round(datos['NumPy']['ram'], 2),
            'Sys_NumPy_s': round(datos['NumPy']['cpu_sys'], 4),
            
            'T_Cython_s': round(datos['Cython']['tiempo'], 4),
            'RAM_Cython_MB': round(datos['Cython']['ram'], 2),
            'Sys_Cython_s': round(datos['Cython']['cpu_sys'], 4)
        })
    print(f"-> Datos HPC registrados en: {nombre_archivo}")

def graficar_resultados(datos, width, height, max_iter):
    etiquetas = ['Python Puro', 'NumPy', 'Cython']
    tiempos = [datos['Python']['tiempo'], datos['NumPy']['tiempo'], datos['Cython']['tiempo']]

    fig, ax = plt.subplots(figsize=(9, 6))
    barras = ax.bar(etiquetas, tiempos, color=['#e74c3c', '#3498db', '#2ecc71'])

    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2., altura,
                f'{altura:.4f} s',
                ha='center', va='bottom', fontsize=12, fontweight='bold')

    ax.set_ylabel('Tiempo de ejecución (Segundos)', fontsize=12)
    ax.set_title(f'Perfil HPC: Conjunto de Julia ({width}x{height}, {max_iter} iteraciones)', fontsize=14, pad=20)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()

    nombre_grafico = f"benchmark_hpc_{width}x{height}_{max_iter}i.png"
    plt.savefig(nombre_grafico, dpi=300)
    print(f"-> Gráfico guardado exitosamente como: {nombre_grafico}")
    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Benchmark HPC del Conjunto de Julia")
    parser.add_argument("-w", "--width", type=int, default=1000, help="Ancho de la cuadrícula")
    parser.add_argument("-H", "--height", type=int, default=1000, help="Alto de la cuadrícula")
    parser.add_argument("-i", "--iter", type=int, default=100, help="Número máximo de iteraciones")
    
    args = parser.parse_args()
    
    datos_rendimiento, matriz_fractal = ejecutar_benchmark(args.width, args.height, args.iter)
    guardar_historial_csv(datos_rendimiento, args.width, args.height, args.iter)
    
    nombre_imagen = f"fractal_julia_{args.width}x{args.height}_{args.iter}i.png"
    plt.imsave(nombre_imagen, matriz_fractal, cmap='magma')
    print(f"-> Imagen del fractal guardada como: {nombre_imagen}")
    
    graficar_resultados(datos_rendimiento, args.width, args.height, args.iter)