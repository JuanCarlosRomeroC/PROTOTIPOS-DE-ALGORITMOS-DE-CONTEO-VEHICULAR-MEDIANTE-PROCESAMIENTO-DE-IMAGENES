# para video de archivo
# python conteo_clasificacion_vehicular.py --input videos/koper_highway.mp4 --display 1 --output koper_highway.avi --mask 200,350,650,550 --resize 1024
# python conteo_clasificacion_vehicular.py --input videos/koper_highway.mp4 --display 1 --output koper_highway.avi --mask 150,300,510,450 --resize 800

#"para web cam" 
# python conteo_clasificacion_vehicular.py  --display 1 --output koper_highway.avi --mask 210,260,630,420 --resize 640

# importa los paquetes necesarios

import os
from imutils.video import VideoStream
from imutils.video import FPS
import argparse
import time
from datetime import datetime
import cv2
import numpy as np
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
import dlib
import sqlite3
running_on_rpi = False
os_info = os.uname()
if os_info[4][:3] == 'arm':
    running_on_rpi = True

# Comprobar si la optimización está habilitada

if not cv2.useOptimized():
    print("Por defecto, OpenCV no ha sido optimizado")
    cv2.setUseOptimized(True)

writer = None
W = None
H = None

observation_mask = None
display_bounding_boxes = False

display_settings = True

# inicializa el número total de fotogramas procesados ​​hasta ahora, a lo largo
# con el número total de objetos que se han movido hacia arriba o hacia abajo

totalFrames = 0
totalOverall = 0
labels=""
ids=""
labelprocent=0
AUTOCAMIONETA=0
camiontetas=0
MOTO=0
CAMIONTRAYLER=0
BUSFURGONETA=0
tipos = ""
image_for_result = None

#conexion con base de datos
conn = sqlite3.connect('bd/bd_conteo_clasificacion.db')
c = conn.cursor()

#crear tabla 
def crear_tabla():
    c.execute("CREATE TABLE IF NOT EXISTS tclasificacion(Idcount INTEGER PRIMARY KEY AUTOINCREMENT,Id VARCHAR,tipos VARCHAR(100)  NULL,porcentajes VARCHAR(100)  NULL, hora VARCHAR(100),fecha VARCHAR(100),UNIQUE(Id))")
  
def insertar_datos():
    params = (Id,tipos, porcentajes, hora,fecha)
    c.execute("INSERT OR IGNORE INTO tclasificacion VALUES (NULL, ?, ?, ?, ?, ?)", params) 
    conn.commit()
def eliminar_duplicados():
    params = (Id,tipos, porcentajes, hora,fecha)
    c.execute("DELETE FROM tclasificacion WHERE Idcount > 1")
    conn.commit()
def obteneridconteo():
    params = (Idcount)
    c.execute("SELECT Idcount FROM tclasificacion ")
    conn.commit()

# inicializar la lista de etiquetas de clase para las que nuestra red recibió capacitación
# detectar, luego generar un conjunto de colores de cuadro delimitador para cada clase

#CLASSES = ("background", "aeroplane", "bicycle", "bird",
 #          "boat", "bottle", "bus", "car", "cat", "chair", "cow",
  #         "diningtable", "dog", "horse", "motorbike", "person",
   #        "pottedplant", "sheep", "sofa", "train","tvmonitor")
   
CLASSES = ("background", "Avion", "bici", "pajaro",
           "barco", "botella", "BUS/FURGONETA", "AUTO/CAMIONETA", "gato", "silla", "vaca",
           "comedor", "perro", "caballo", "MOTO", "persona",
           "maceta", "sheep", "sofa", "CAMION/TRAYLER","tvmonitor")
           
def predict(frame, net):

    # Preparar blob de entrada y realizar una inferencia
    blob = cv2.dnn.blobFromImage(frame, 0.007843, size=(300, 300), mean=(127.5, 127.5, 127.5), swapRB=False, crop=False)
    net.setInput(blob)
    out = net.forward()
    out = out.flatten()

    predictions = []

    for box_index in range(100):
        if out[box_index + 1] == 0.0:
            break
        base_index = box_index * 7
        if (not np.isfinite(out[base_index]) or
                not np.isfinite(out[base_index + 1]) or
                not np.isfinite(out[base_index + 2]) or
                not np.isfinite(out[base_index + 3]) or
                not np.isfinite(out[base_index + 4]) or
                not np.isfinite(out[base_index + 5]) or
                not np.isfinite(out[base_index + 6])):
            continue


        object_info_overlay = out[base_index:base_index + 7]

        base_index = 0
        class_id = int(object_info_overlay[base_index + 1])
        conf = object_info_overlay[base_index + 2]
        #Clasificacion para 1 tipo de objeto class_id != ?
        #if (conf <= args["confidence"] or class_id != 0):
        #Clasificacion para varios tipos de Vehiculos
        if (conf <= args["confidence"] or class_id != 6 and class_id !=7 and class_id !=14):
           continue

        box_left = object_info_overlay[base_index + 3]
        box_top = object_info_overlay[base_index + 4]
        box_right = object_info_overlay[base_index + 5]
        box_bottom = object_info_overlay[base_index + 6]

        prediction_to_append = [class_id, conf, ((box_left, box_top), (box_right, box_bottom))]
        predictions.append(prediction_to_append)

    return predictions


def resize(frame, width, height=None):
    h, w, _ = frame.shape
    if height is None:
        # Mantener Relacion
        factor = width * 1.0 / w
        height = int(factor * h)
    frame_resized = cv2.resize(frame, (width, height), interpolation=cv2.INTER_AREA)
    return frame_resized


def crop(frame, top, left, height, width):
    h, w, _ = frame.shape
    cropped = frame[top:top + height, left: left + width]
    return cropped

#color Rojo
#def draw_observation_mask(frame, top_left, bottom_right, alpha=0.5, color=(0, 0, 255)):
#color azul
def draw_observation_mask(frame, top_left, bottom_right, alpha=0.5, color=(250, 125, 0)):
    
    # cree dos copias de la imagen original, una para
    # la superposición y una para la imagen de salida final
    
    overlay = frame.copy()
    output = frame.copy()

       
    # dibuja un rectángulo rojo alrededor de la region de interes en la imagen
    # usando la libreria "PyImageSearch" en la esquina superior izquierda
    # esquina
    
    
    cv2.rectangle(overlay, top_left, bottom_right,
                  color, -1)
      
    # aplica la superposición
    cv2.addWeighted(overlay, alpha, output, 1 - alpha,
                    0, output)
    return output



#construir el analizador de argumentos y analizar los argumentos
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--confidence", default=.5,
                help="confidence threshold")
ap.add_argument("-d", "--display", type=int, default=0,
                help="switch to display image on screen")
ap.add_argument("-i", "--input", type=str,
                help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
                help="path to optional output video file")
ap.add_argument("-s", "--skip-frames", type=int, default=15,
	help="# of skip frames between detections")
ap.add_argument("-r", "--resize", type=str, default=None,
                help="resized frames dimensions, e.g. 320,240")
ap.add_argument("-m", "--mask", type=str, default=None,
                help="observation mask x_min,y_min,x_max,y_max, e.g. 50,70,220,300")
args = vars(ap.parse_args())

if args["mask"] is not None:
    try:
        x_min, y_min, x_max, y_max = [int(item.replace(" ", "")) for item in args["mask"].split(",")]
        observation_mask = [(x_min, y_min), (x_max, y_max)]
    except ValueError:
        print("Formato de máscara inválido!")

# instanciar nuestro rastreador centroide, luego inicializar una lista para almacenar
# cada uno de nuestros rastreadores de correlación dlib, seguido de un diccionario para
# asigna cada ID de objeto único a un TrackableObject

centroidTracker_max_disappeared = 15
centroidTracker_max_distance = 100
ct = CentroidTracker(maxDisappeared=centroidTracker_max_disappeared, maxDistance=centroidTracker_max_distance, mask=observation_mask)
#Array del Rastreador de objetos
trackers = []
trackableObjects = {}

# Cargar el modelo
net = cv2.dnn.readNet('models/mobilenet-ssd/FP16/mobilenet-ssd.xml', 'models/mobilenet-ssd/FP16/mobilenet-ssd.bin')
# Especificar dispositivo de destino "USB Movidius Neural Compute Stick 2"
net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

# si no se proporcionó una ruta de video, tome una referencia a la cámara web

if not args.get("input", False):
    print("[INFO] Iniciando la Transmision del Video")
    vs = VideoStream(src=0).start()
    time.sleep(2.0)

# de lo contrario, tome una referencia al archivo de video
else:
    print("[INFO] abriendo archivo de video ...")
    vs = cv2.VideoCapture(args["input"])

time.sleep(1)
fps = FPS().start()

# bucle sobre cuadros de la secuencia del archivo de video
while True:
    try:
        # agarra el cuadro de la secuencia de video enhebrada
        # hacer una copia del marco y cambiar su tamaño para fines de visualización / video
        frame = vs.read()
        frame = frame[1] if args.get("input", False) else frame

        # si estamos viendo un video y no tomamos un cuadro, entonces
        # ha llegado al final del video
        if args["input"] is not None and frame is None:
            break

        if args["resize"] is not None:
            if "," in args["resize"]:
                w, h = [int(item) for item in args["resize"].split(",")]
                frame = resize(frame, width=w, height=h)
            else:
                frame = resize(frame, width=int(args["resize"]))

        # el frame de BGR a RGB para dlib
        
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

        H, W, _ = frame.shape

        # Imprimir Configuraciones
        if display_settings:
            print("[INFO] frame tamaño (W x H): %d x %d" % (W, H))
            preview_image = frame.copy()
            preview_image_file = "screenshots/preview_%d_%d" % (W, H)
            if observation_mask is not None:
                print("Observation mask (top left, bottom right): %s" % str(observation_mask))
                preview_image = draw_observation_mask(preview_image, observation_mask[0], observation_mask[1])
                preview_image_file += "_mask_%d_%d_%d_%d" % (observation_mask[0][0], observation_mask[0][1], observation_mask[1][0], observation_mask[1][1])
            preview_image_file += ".jpg"
            cv2.imwrite(preview_image_file, preview_image)
            display_settings = False

        if args["display"] > 0 or args["output"] is not None:
            image_for_result = frame.copy()
            if observation_mask is not None:
                image_for_result = draw_observation_mask(image_for_result, observation_mask[0], observation_mask[1])

        # si se supone que estamos escribiendo un video en el disco, inicialice
        # el escritor
        if args["output"] is not None and writer is None:
            fourcc = cv2.VideoWriter_fourcc(*"MJPG")
            writer = cv2.VideoWriter(args["output"], fourcc, 30,
                                     (frame.shape[1], frame.shape[0]), True)

        
        # inicializa el estado actual junto con nuestra lista de límites
        # rectángulos de caja devueltos por (1) nuestro detector de objetos o
        # (2) los rastreadores de correlación
        
        
        status = "Esperando"
        rects = []

        # verifique si deberíamos ejecutar una computadora más costosa
        # método de detección de objetos para ayudar a nuestro rastreador
        
        if totalFrames % args["skip_frames"] == 0:
            # establecer el estado e inicializar nuestro nuevo conjunto de rastreadores de objetos
            status = "Detectando"
            trackers = []


            # usa el NCS2 para adquirir predicciones
            if observation_mask is not None:
                cropped_frame = frame[observation_mask[0][1]:observation_mask[1][1], observation_mask[0][0]:observation_mask[1][0]]
                predictions = predict(cropped_frame, net)
            else:
                predictions = predict(frame, net)

            # bucle sobre nuestras predicciones
            for (i, pred) in enumerate(predictions):
                # extract prediction data for readability
                (class_id, pred_conf, pred_boxpts) = pred
                ((x_min, y_min), (x_max, y_max)) = pred_boxpts

                # filtra las detecciones débiles asegurando la `confianza`
                # es mayor que la confianza mínima
                if pred_conf > args["confidence"]:
                    # imprimir predicción a la terminal
                    print("[INFO] Prediction #{}: confidence={},class={}, "
                          "boxpoints={}".format(i, pred_conf,class_id,
                                                pred_boxpts))
                                          
                    # si la etiqueta de la clase no es un automóvil, ignórelo
                    #if CLASSES[class_id] != "car" and "Autobus" and "motorbike" and "bicycle" and "Hatchback":
                    if CLASSES[class_id] != "BUS/FURGONETA" and CLASSES[class_id] !="AUTO/CAMIONETA" and CLASSES[class_id] != "MOTO":
                        continue
                    if observation_mask is not None:
                        mask_width = observation_mask[1][0] - observation_mask[0][0]
                        mask_height = observation_mask[1][1] - observation_mask[0][1]
                        x_min = int(x_min * mask_width) + observation_mask[0][0]
                        y_min = int(y_min * mask_height) + observation_mask[0][1]
                        x_max = int(x_max * mask_width) + observation_mask[0][0]
                        y_max = int(y_max * mask_height) + observation_mask[0][1]
                        
                    else:
                        x_min = int(x_min * W)
                        y_min = int(y_min * H)
                        x_max = int(x_max * W)
                        y_max = int(y_max * H)

                    
                    # construir un objeto rectángulo dlib a partir del límite
                    # coordenadas del cuadro y luego iniciar la correlación dlib
                    # tracker
                    
                    tracker = dlib.correlation_tracker()
                    rect = dlib.rectangle(x_min, y_min, x_max, y_max)
                    tracker.start_track(rgb, rect)

                    # agregue el rastreador a nuestra lista de rastreadores para que podamos
                    # utilízalo durante los cuadros de salto
                    trackers.append(tracker)

        
        # de lo contrario, deberíamos utilizar nuestro objeto * rastreadores * en lugar de
        # objeto * detectores * para obtener un rendimiento de procesamiento de trama más alto
        else:
            # Bucle sobre Rastreador
            for tracker in trackers:
                
                # establecer el estado de nuestro sistema para que sea 'seguimiento' en lugar
                # que 'esperar' o 'detectar'
                status = "Rastreo"
                
                # actualizar el rastreador y tomar la posición actualizada
                tracker.update(rgb)
                pos = tracker.get_position()
                # descomprime el objeto de posición
                startX = int(pos.left())
                startY = int(pos.top())
                endX = int(pos.right())
                endY = int(pos.bottom())

                # agregar las coordenadas del cuadro delimitador a la lista de rectángulos
                rects.append((startX, startY, endX, endY))

        # use el rastreador centroide para asociar el (1) objeto antiguo
        # centroides con (2) los centroides de objetos recién calculados
        objects = ct.update(rects)

        
        # bucle sobre los objetos rastreados
        for (objectID, centroid) in objects.items():
            
            # comprobar para ver si existe un objeto rastreable para el actual
            # ID de objeto
            to = trackableObjects.get(objectID, None)

            
            # si no hay ningún objeto rastreable existente, cree uno
            if to is None:
                to = TrackableObject(objectID, centroid)

            
            # de lo contrario, hay un objeto rastreable para que podamos utilizarlo
            # para determinar la dirección
            else:
                y = [c[1] for c in to.centroids]
                to.centroids.append(centroid)

               
                # verifique si el objeto ha sido contado o no
                if not to.counted:
                    totalOverall += 1
                    to.counted = True
                    if tipos == "AUTO/CAMIONETA":
                        AUTOCAMIONETA += 1
                        to.counted = True
                    elif tipos == "BUS/FURGONETA":
                        BUSFURGONETA += 1
                        to.counted = True
                    elif tipos == "MOTO":
                        MOTO += 1
                        to.counted = True
                    #insertar a la base de datos solo si el total de vehiculos incrementa     
                    insertar_datos()
            
            # almacenar el objeto rastreable en nuestro diccionario
            trackableObjects[objectID] = to
           
            # construir una etiqueta
            label = "{}: {:.2f}%".format(CLASSES[class_id], pred_conf * 100)
            labels = "{}".format(CLASSES[class_id])
            labelprocent = "{:.2f}%".format(pred_conf * 100)
            
            # extraer información de los puntos de cuadro de predicción
            y = y_min - 15 if y_min - 15 > 15 else y_min + 15

            if image_for_result is not None:
                if display_bounding_boxes:
                    
                    # muestra el rectángulo y el texto de la etiqueta
                    cv2.rectangle(image_for_result, (x_min, y_min), (x_max, y_max),
                                  (255, 0, 0), 2)
                    cv2.putText(image_for_result, label, (x_min, y),
                                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 3)

                # dibuja tanto la ID del objeto como el centroide del
                # objeto en el marco de salida
                text = "ID {}".format(objectID)
                cv2.putText(image_for_result, text, (centroid[0] - 10, centroid[1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
                cv2.circle(image_for_result, (centroid[0], centroid[1]), 4, (0, 255, 0), -1)
                ids = "{}".format(objectID)
        
        # construir una tupla de información que mostraremos en el
        # cuadro
        # Variables Resultados
        # id + tiempo
        now = datetime.now()
        idtime = str(now.hour) + str(now.minute) + "-"+ str(now.year) + str(now.month)+str(now.day)
        
        #camiontetas=0
        tipos = ""
        Id=ids + "-" + idtime
        tipos=labels
        porcentajes=labelprocent
        mensaje = ""
        
        #Mostrar en Pantalla Fecha y Hora Actual    
        fecha_hora_actual = datetime.now()
        fecha= fecha_hora_actual.strftime("%Y/%m/%d")
        hora= fecha_hora_actual.strftime("%H:%M:%S")
                         
        #Texto en Pantalla
        
        info = [
            ("Presione q para salir",mensaje),
            ("Conteo Total", totalOverall),
            ("MOTO",MOTO),
            ("BUS FURGONETA",BUSFURGONETA),
            ("AUTO CAMIONETA:",AUTOCAMIONETA),
            ("CAMION TRAYLER:",CAMIONTRAYLER),
            ("Porcentaje",porcentajes),
            ("Tipo",tipos),
            ("ID",Id),
            ("Estado", status),
            ("Hora",hora),
            ("Fecha",fecha),
        ]
        #Quitar Comentario despues de Crear la tabla
        crear_tabla()
        
        
        if image_for_result is not None:
            # recorrer las tuplas de información y dibujarlas en nuestro marco
            for (i, (k, v)) in enumerate(info):
                text = "{}: {}".format(k, v)
                cv2.putText(image_for_result, text, (10, H - ((i * 20) + 200)),
                            #Tamaño de Letra Color de Resultados
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 120), 2)
            
           
        # verifique si debemos escribir el marco en el disco
        if writer is not None:
            writer.write(image_for_result)
        # comprobar si deberíamos mostrar el marco en la pantalla
        # con datos de predicción (puede lograr un FPS más rápido si
        # no salir a la pantalla)
        if args["display"] > 0:
            # se muestra los frames en pantalla
            cv2.imshow("Output", image_for_result)
            key = cv2.waitKey(1) & 0xFF
            # si se presionó la tecla `q`, salga del bucle
            if key == ord("q"):
                break
        # incrementa el número total de tramas procesadas hasta el momento y
        # luego actualice el contador FPS
        totalFrames += 1
        fps.update()
    # si se presiona "ctrl + c" en el terminal, salga del bucle
    except KeyboardInterrupt:
        break
    # si hay un problema al leer un frame, se detiene y rompe la secuancia
    except AttributeError:
        break
# detener el temporizador del contador FPS
fps.stop()
# destruir todas las ventanas si las estamos mostrando
if args["display"] > 0:
    cv2.destroyAllWindows()
# si no estamos usando un archivo de video, detenga la transmisión de video de la cámara
if not args.get("input", False):
    vs.stop()
# de lo contrario, suelte el puntero del archivo de video
else:
    vs.release()
# muestra información de FPS
print("[INFO] Tiempo Transcurrido: {:.2f}".format(fps.elapsed()))
print("[INFO] Aproximacion. FPS: {:.2f}".format(fps.fps()))

