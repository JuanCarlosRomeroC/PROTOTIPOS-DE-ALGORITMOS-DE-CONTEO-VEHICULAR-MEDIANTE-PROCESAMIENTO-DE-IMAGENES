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

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoIoU/Resultados.png" width="" height="320" border="240" align="center"/> 

Algoritmo Caffe Mobilenet:

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoCaffeMobilenet/prototipo.png" width="" height="320" border="240" align="center"/> 

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoCaffeMobilenet/prototipo2.png" width="" height="300" border="260" align="center"/> 

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoCaffeMobilenet/prototipo3.png" width="" height="320" border="240" align="center"/> 

Algoritmo YOLO:

<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/AlgoritmoYoloV3/resultados.PNG" width="" height="480" border="320" align="center"/> 

Prototipo de Sistema en Python + OpenCV + NCS2 + Mobilenet + Framework Dash + Xls:
<img src="https://github.com/JuanCarlosRomeroC/PROTOTIPOS-DE-ALGORITMOS-DE-CONTEO-VEHICULAR-MEDIANTE-PROCESAMIENTO-DE-IMAGENES/blob/master/RASPBERRY_PI_3_NCS2_MOBILENET/mobilenet_ncs2.PNG" width="" height="480" border="320" align="center"/> 

Referencia
----
| Algoritmo | Fuente |
| ------------- | ------------- |
| Mog2 | https://pysource.com/2018/05/17/background-subtraction-opencv-3-4-with-python-3-tutorial-32/ |
| Filtro Kalman | https://stackoverflow.com/questions/29012038/is-there-any-example-of-cv2-kalmanfilter-implementation, https://stackoverflow.com/questions/36254452/counting-cars-opencv-python-issue?rq=1  |
| Haar Cascade | https://github.com/AdityaPai2398/UI-For-Vehicle-and-Pedestrian-Detection-/tree/master/Vehicle%20and%20pedestrain%20detection |
| IoU | https://www.pyimagesearch.com/2016/11/07/intersection-over-union-iou-for-object-detection/ |
| Caffe Mobilenet | https://answers.opencv.org/answers/225675/revisions/ |
| YOLO | https://github.com/PINTO0309/OpenVINO-YoloV3 |

License
----

GNU Versión 3
