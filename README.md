# PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES

ALGORITMO SUBSTRACTOR MOG2

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoSubstractorMOG2/Resultado.png" width="600" height="360" border="10" align="center"/>

DESCRIPCION
>SubtractorMog2 tiene la ventaja de trabajar con un historial de cuadros, funciona de forma predeterminada con los últimos 120 cuadros, primer 
fotograma de manera alta durante el día, después de algunas horas cuando se pone el sol, calculando la diferencia con el primer fotograma tomado 
unas horas antes no funcionaría.
El valor umbral es el valor utilizado al calcular la diferencia para extraer el fondo. Un umbral más bajo encontrará más diferencias con la 
ventaja de una imagen más ruidosa.
Las coordenadas y diámetro del auto se encuentra en Vehiculo.py para la detección de múltiples autos.
Menú principal del algoritmo Menu.py


ALGORITMO FILTRO KALMAN:

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoFiltroKalman/Resultado.png" width="600" height="360" border="10" align="center"/> 

DESRIPCION

- OBTENER CENTROIDE
- OBTENER CONTORNO DE RECTANGULO
- LIMPIAR IMAGEN Y ENCONTRAR VEHICULOS
- MASCARA DE FILTRO
- CREA UNA IMAGEN BINARIA 
- CALCULAR FONDO (PROMEDIO Y MEDIANA)
- BUSQUEDA DE CONTORNOS
- DETECTAR VEHICULOS

>COMPATIBILIDAD (CPU)
>CODEC: H264, AVI, MP4
>FOTOGRAMAS POR SEGUNDO (FPS): 23.84
>CALIDAD DE IMAGEN: 1 MEGAPIXEL
>RESOLUCION OUT: 640X360
>LIBRERÍAS:(RANDOM, SYS, UUID, CV2, NUMPY, SCIPY)
>VERSION DE OPENCV: 3.3 – 3.4
>OS.WIN 10 EDU
>CORE i5 2.3GHz RAM 4GB 


ALGORITMO HAAR CASCADE:

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoHaarCascade/autos.png" width="600" height="360" border="10" align="center"/> 
<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoHaarCascade/buses.PNG" width="600" height="360" border="10" align="center"/> 

Algoritmo Iou:

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoIoU/resultado.PNG" width="" height="412" border="238" align="center"/> 

Referencia
----
>https://pysource.com/2018/05/17/background-subtraction-opencv-3-4-with-python-3-tutorial-32/

>https://www.pyimagesearch.com20161107intersection-over-union-iou-for-object-detection

>https://github.com/PINTO0309/OpenVINO-YoloV3

License
----

GNU Versión 3
