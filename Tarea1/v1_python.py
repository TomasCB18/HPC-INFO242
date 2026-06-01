def calcular_julia_python(width, height, max_iter, c):
    x_min, x_max = -1.5, 1.5
    y_min, y_max = -1.5, 1.5
    
    resultado = [[0 for _ in range(width)] for _ in range(height)]
    
    for y in range(height):
        im = y_min + (y_max - y_min) * y / height
        for x in range(width):
            re = x_min + (x_max - x_min) * x / width
            z = complex(re, im)
            
            for i in range(max_iter):
                if abs(z) > 2.0:
                    break
                z = z*z + c
            
            resultado[y][x] = i
            
    return resultado