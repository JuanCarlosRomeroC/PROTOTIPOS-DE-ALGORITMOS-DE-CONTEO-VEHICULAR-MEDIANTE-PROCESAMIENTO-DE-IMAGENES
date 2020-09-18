# linea de comando
# python intersection_over_union.py

# importar los paquetes necesarios
from collections import namedtuple
import numpy as np
import cv2

# definir el objeto "Detección"
Detection = namedtuple("Detection", ["image_path", "gt", "pred"])

def bb_intersection_over_union(boxA, boxB):
	# determinar las coordenadas (x, y) del rectángulo de intersección
	xA = max(boxA[0], boxB[0])
	yA = max(boxA[1], boxB[1])
	xB = min(boxA[2], boxB[2])
	yB = min(boxA[3], boxB[3])

	# calcular el área del rectángulo de intersección
	interArea = max(0, xB - xA + 1) * max(0, yB - yA + 1)

	# calcular el área tanto de la predicción como de la verdad fundamental
    # rectángulos
	boxAArea = (boxA[2] - boxA[0] + 1) * (boxA[3] - boxA[1] + 1)
	boxBArea = (boxB[2] - boxB[0] + 1) * (boxB[3] - boxB[1] + 1)

	# calcula la intersección sobre la unión tomando la intersección
    # área y dividiéndola por la suma de la predicción + la verdad del terreno
    # áreas - el área de intersección
	iou = interArea / float(boxAArea + boxBArea - interArea)

	# devuelve la intersección sobre el valor de unión
	return iou

# definir la lista de detecciones de ejemplo
examples = [
	#Detection("image_0002.jpg", [39, 63, 203, 112], [54, 66, 198, 114]),
	#Detection("image_0016.jpg", [49, 75, 203, 125], [42, 78, 186, 126]),
	#Detection("image_0075.jpg", [31, 69, 201, 125], [18, 63, 235, 135]),
	#Detection("image_0090.jpg", [50, 72, 197, 121], [54, 72, 198, 120]),
	#Detection("image_0120.jpg", [35, 51, 196, 110], [36, 60, 180, 108]),
    Detection("2.jpg", [60, 90, 334, 206], [62, 92, 339, 209])]

# recorrer las detecciones de ejemplo
for detection in examples:
	# cargar la imagen
	image = cv2.imread(detection.image_path)

	# dibuje el cuadro delimitador de la verdad del terreno junto con el
    # cuadro delimitador
	cv2.rectangle(image, tuple(detection.gt[:2]), 
		tuple(detection.gt[2:]), (0, 255, 0), 2)
	cv2.rectangle(image, tuple(detection.pred[:2]), 
		tuple(detection.pred[2:]), (0, 0, 255), 2)

	# calcular la intersección sobre la unión y mostrarla
	iou = bb_intersection_over_union(detection.gt, detection.pred)
	cv2.putText(image, "IoU: {:.4f}".format(iou), (10, 30),
		cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
	print("{}: {:.4f}".format(detection.image_path, iou))

	# mostrar la imagen de salida
	cv2.imshow("Image", image)
	cv2.waitKey(0)
