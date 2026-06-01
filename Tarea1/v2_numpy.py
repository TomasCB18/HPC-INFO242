import numpy as np

def calcular_julia_numpy(width, height, max_iter, c):
    x = np.linspace(-1.5, 1.5, width)
    y = np.linspace(-1.5, 1.5, height)
    
    X, Y = np.meshgrid(x, y)
    Z = X + 1j * Y
    
    resultado = np.zeros(Z.shape, dtype=int)
    activos = np.ones(Z.shape, dtype=bool)
    
    for i in range(max_iter):
        Z[activos] = Z[activos]**2 + c
        escaparon = np.abs(Z) > 2.0
        nuevos_escapes = escaparon & activos
        resultado[nuevos_escapes] = i
        activos[nuevos_escapes] = False
        
    return resultado