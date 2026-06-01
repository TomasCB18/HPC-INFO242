import numpy as np
cimport numpy as cnp
cimport cython

@cython.boundscheck(False)
@cython.wraparound(False)
def calcular_julia_cython(int width, int height, int max_iter, double complex c):
    cdef int x, y, i
    cdef double complex z
    cdef double re, im
    cdef double x_min = -1.5, x_max = 1.5
    cdef double y_min = -1.5, y_max = -1.5
    
    cdef cnp.ndarray[cnp.int32_t, ndim=2] resultado = np.zeros((height, width), dtype=np.int32)
    
    for y in range(height):
        im = -1.5 + (3.0 * y) / height
        for x in range(width):
            re = -1.5 + (3.0 * x) / width
            z = re + im * 1j
            
            for i in range(max_iter):
                if (z.real * z.real + z.imag * z.imag) > 4.0:
                    break
                z = z * z + c
                
            resultado[y, x] = i
            
    return resultado