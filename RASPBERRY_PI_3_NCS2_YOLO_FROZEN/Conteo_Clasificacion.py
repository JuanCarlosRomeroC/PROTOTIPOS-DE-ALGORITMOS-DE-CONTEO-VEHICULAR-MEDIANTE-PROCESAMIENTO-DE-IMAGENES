# AUTORES: - JUAN CARLOS ROMERO CHALCO
#          - ELVIS ANCALLE VILLCAS
# FECHA DE CREACION:
# PROPOSITO: REALIZA DETECCION DE VEHICULOS EN TIEMPO REAL DE UNA INFRAESTRUCTURA VIAL
# FECHA DE CREACION: 
# USAR EL SIGUIENTE COMANDO PARA EJECUTAR EL PROGRAMA
# python detect_realtime_tinyyolo_ncs.py --conf config/config.json --input videos/test_video.mp4

# Importar Librerias y Paquetes de instalacion
from openvino.inference_engine import IENetwork
from openvino.inference_engine import IEPlugin
from intel.yoloparams import TinyYOLOV3Params
from intel.tinyyolo import TinyYOLOv3
from imutils.video import VideoStream
from pyimagesearch.utils import Conf
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import cv2
import os
import urllib

# Construccion de la Clase Analisador
ap = argparse.ArgumentParser()
ap.add_argument("-c", "--conf", required=True,
    help="RUTA DEL ARCHIVO DE CONFIGURACION DE ENTRADA - JSON")
ap.add_argument("-i", "--input", help="RUTA DE ENTRADA DE VIDEO")
args = vars(ap.parse_args())

# CARGAR EL ARCHIVO DE CONFIGURACION
conf = Conf(args["conf"])

# Cargar las etiquetas de clase COCO en las que se capacitó nuestro modelo YOLO y
# inicializar una lista de colores para representar cada clase posible
# Etiquetas
LABELS = open(conf["labels_path"]).read().strip().split("\n")
np.random.seed(42)
COLORS = np.random.uniform(0, 255, size=(len(LABELS), 3))

# Inicializar el complemento (USB NCS2 INTEL) para el dispositivo especificado
plugin = IEPlugin(device="MYRIAD")

# Leer las inferencias (IR) Generadas por el modelo optimizado de Openvino (.xml and .bin archivos)
print("[INFO] Cargando  Modelos...")
net = IENetwork(model=conf["xml_path"], weights=conf["bin_path"])

# Preparando Modelos
print("[INFO] Preparando Entradas...")
inputBlob = next(iter(net.inputs))

# establezca el tamaño de lote predeterminado en 1 y obtenga el número de blobs de entrada,
# número de canales, la altura y el ancho del blob de entrada
net.batch_size = 1
(n, c, h, w) = net.inputs[inputBlob].shape

# si no se proporcionó una ruta de video, tome una referencia a la cámara web
if args["input"] is None:
    print("[INFO] Iniciando la Transmision de Video...")
    vs = VideoStream(src=0).start()
    #vs = VideoStream(usePiCamera=True).start()
    time.sleep(2.0)

# de lo contrario, tome una referencia al archivo de video
else:
    print("[INFO] Abriendo el Archivo de Video ...")
    vs = cv2.VideoCapture(os.path.abspath(args["input"]))

# cargar el modelo en el complemento e iniciar los cuadros por segundo
# estimador de rendimiento
print("[INFO] Cargando el modelo al plugin...")
execNet = plugin.load(network=net, num_requests=1)
fps = FPS().start()

car = 0
bicycle = 0
motorbike = 0
person = 0
start = time.time()

#linea roi
#start_point = (70, 0) 
#end_point = (70, 500) 
#color = (0, 255, 0) 
#thickness = 4

start_point = (260, 0) 
end_point = (260, 500) 
color = (0, 255, 0) 
thickness = 4



# bucle sobre los cuadros de la secuencia de video

while True:
    # agarra el siguiente cuadro y maneja si estamos leyendo
    # VideoCapture or VideoStream
    orig = vs.read()
    orig = orig[1] if args["input"] is not None else orig

    # si estamos viendo un video y no tomamos un cuadro, entonces
    # ha llegado al final del video
    if args["input"] is not None and orig is None:
        break

    # cambiar el tamaño del marco original para tener un ancho máximo de 500 píxeles y
    # input_frame al tamaño de la red
    orig = imutils.resize(orig, width=500)
    orig = cv2.line(orig, start_point, end_point, color, thickness) 
    frame = cv2.resize(orig, (w, h))

    # cambiar el diseño de datos de HxWxC a CxHxW
    frame = frame.transpose((2, 0, 1))
    frame = frame.reshape((n, c, h, w))

    # iniciar inferencia e inicializar lista para recopilar detección de objetos
    # resultados
    output = execNet.infer({inputBlob: frame})
    objects = []

    # bucle sobre los elementos de salida
    for (layerName, outBlob) in output.items():
        # crear un nuevo objeto que contenga el tinyYOLOv3 requerido
        # parámetros
        layerParams = TinyYOLOV3Params(net.layers[layerName].params,
            outBlob.shape[2])

        # analizar la región de salida
        objects += TinyYOLOv3.parse_yolo_region(outBlob,
            frame.shape[2:], orig.shape[:-1], layerParams,
            conf["prob_threshold"])

    # loop over each of the objects
    for i in range(len(objects)):
        # comprobar si la confianza del objeto detectado es cero, si
        # es, luego omita esta iteración, indicando que el objeto
        # debe ser ignorado
        
        if objects[i]["confidence"] == 0:
            continue

        # loop over remaining objects
        for j in range(i + 1, len(objects)):
            # compruebe si la IoU de ambos objetos excede un
            # umbral, si lo hace, establezca la confianza de ese
            # objeto a cero
            if TinyYOLOv3.intersection_over_union(objects[i],
                objects[j]) > conf["iou_threshold"]:
                objects[j]["confidence"] = 0

    # filtrar objetos usando el umbral de probabilidad - si un
    # objeto está por debajo del umbral, ignórelo
    
    objects = [obj for obj in objects if obj['confidence'] >= \
        conf["prob_threshold"]]

    # almacenar la altura y el ancho del frame original
    (endY, endX) = orig.shape[:-1]

    # recorrer todos los objetos restantes
    for obj in objects:
        # validar el cuadro delimitador del objeto detectado, asegurando
        # no tenemos cuadros delimitadores no válidos
        
        if obj["xmax"] > endX or obj["ymax"] > endY or obj["xmin"] \
            < 0 or obj["ymin"] < 0:
            continue
        
        # construir una etiqueta que consista en la clase prediccion y
        # probabilidad asociada
        label = "{}: {:.2f}%".format(LABELS[obj["class_id"]],
            obj["confidence"] * 100)

        # Calcular la coordenada y es usada para escribir la etiqueta en el
        # frame (marco)
        # marco dependiendo de la coordenada del cuadro delimitador
        y = obj["ymin"] - 15 if obj["ymin"] - 15 > 15 else \
            obj["ymin"] + 15

        # Dibuja un rectángulo del cuadro delimitador y una etiqueta en el marco
        cv2.rectangle(orig, (obj["xmin"], obj["ymin"]), (obj["xmax"],
            obj["ymax"]), COLORS[obj["class_id"]], 2)
        cv2.putText(orig, label, (obj["xmin"], y),
            cv2.FONT_HERSHEY_SIMPLEX, 1, COLORS[obj["class_id"]], 3)
        
        if obj["xmin"] < 70 and obj["class_id"] == 0:
            person = person + 1
        elif obj["xmin"] < 70 and obj["class_id"] == 1:
            bicycle = bicycle + 1
        elif obj["xmin"] < 70 and obj["class_id"] == 2:
            car = car + 1
        elif obj["xmin"] < 70 and obj["class_id"] == 3:
            motorbike = motorbike + 1
                
    # Muestra el cuadro actual en la pantalla y registra si un usuario
    # Presione una Tecla
    cv2.imshow("TinyYOLOv3", orig)
    key = cv2.waitKey(1) & 0xFF
    
    if time.time() - start > 3:
        start = time.time()
        #urllib.request.urlopen("http://192.168.1.2/skripsi2/api/data/insert_data/" + str(person) + "/" + str(bicycle) + "/" + str(car) + "/" + str(motorbike))
        #print("Detectando %s car, %s truck, %s bus, %s bicycle, %s motorbike" % (car,truck,bus,bicycle,motorbike))
        print("deteksi %s person, %s bicycle, %s car, %s motorbike" % (person,bicycle,car,motorbike))
        person = 0
        bicycle = 0
        car = 0
        motorbike = 0
        # Insertando Datos a la Sqlite
        #
        #
    # Si Presiona la Tecla "q" sale del bucle
    if key == ord("q"):
        break

    # Actualizar el contador de FPS
    fps.update()

# Detener el temporizador y mostrar información FPS
fps.stop()
print("[INFO] Tiempo Transcurrido: {:.2f}".format(fps.elapsed()))
print("[INFO] Aproximacion FPS: {:.2f}".format(fps.fps()))

# Detener la Transmision del video y cerrar cualquier ventana cargada
vs.stop() if args["input"] is None else vs.release()
cv2.destroyAllWindows()
