"""
    Rastreador de vehículos
    Este módulo rastrea vehículos en un video de una carretera donde la cámara está quieta.
    Uso:
        python tracker.py [opciones]
    Opciones:
        -v <video_path> Una ruta desde el directorio actual al video de entrada. Valor predeterminado: ./input/Av28julio.mp4
        -b <bg_path> Una ruta desde el directorio actual a un archivo de imagen con un modelo de fondo que se ajusta al
                            entrada de video. Valor predeterminado: ./input/background.jpg, se ajusta a los archivos de video dados xxx.mp4,
                            Aviso: el uso de archivos AVI es problemático en algunos sistemas.
        --hide-blobs Si se usa este parámetro, la ventana que muestra las manchas de vehículos del marco actual no
                            mostrado. De forma predeterminada, se muestra esta ventana.
        --fbf Cuadro por cuadro. Esto cambia el modo de video a modo manual. Moviéndose entre el
                            Los fotogramas de video dejan de ser automáticos y se necesita presionar una tecla (es decir, barra espaciadora) para continuar
                            el siguiente cuadro.
        -l <altura> La altura de la línea de conteo. Este es un número de coma flotante entre 0 y 1, exclusivo.
                            Mide la distancia desde la parte superior del video, donde estará una línea, y cada vehículo
                            que pase la línea será contado. Después de cada cuadro, el número de vehículos que tienen
                            ya pasada la línea se mostrará en la pantalla.
                            El valor predeterminado para este parámetro es 0,7 y los valores inferiores a 0,7 no se recomiendan porque
                            los vehículos están lejos y, en algunos casos, varios vehículos aparecen como uno solo. Los mejores valores
                            para este parámetro están entre 0,7 y 0,9.
        -h, --help Muestra esta ayuda y sale
    El módulo se basa en herramientas de las siguientes bibliotecas: NumPy, SciPy, OpenCV
    Ejemplos de código que ayudaron a construir el módulo:
        Reconocimiento de objetos en movimiento -
            http://stackoverflow.com/questions/36254452/counting-cars-opencv-python-issue?rq=1
        Filtro de Kalman -
            http://stackoverflow.com/questions/29012038/is-there-any-example-of-cv2-kalmanfilter-implementation
"""
import random
import sys
import uuid

import cv2
import detector
import numpy as np
import scipy.spatial.distance as distance

# Tabla indices
X_POS, Y_POS = 0, 1

# Colours for drawing on processed frames
DIVIDER_COLOUR = (255, 255, 0)
BOUNDING_BOX_COLOUR = (255, 0, 0)
CENTROID_COLOUR = (0, 0, 255)

# Keyboard Tecla para Salir
ESC_KEY = 27


# --------------- Utils -----------------

def euclid(a, b):
    """
     : param a: Array a
     : param b: Array b de la misma forma que a
     : return: distancia euclidiana entre ay b
    """
    return distance.euclidean(a, b)


def are_same_picture(pic1, pic2):
    """
     : param pic1: Un conjunto de formas Numpy (ancho, alto, 3), que representa una imagen
     : param pic2: Una matriz Numpy de la misma forma que pic1
     : return: una suposición heurística de si las dos imágenes son realmente la misma (más ruido) o realmente diferentes.
     Útil para comparar los siguientes cuadros en un video
    """
    if pic1 is None or pic2 is None:
        return False
    if pic1.shape != pic2.shape:
        return False
    pixels = pic1.shape[0] * pic1.shape[1]
    return np.sum(np.abs(pic1 - pic2)) < pixels * 35


def random_color():
    """
    : return: Lista con tres valores aleatorios en el rango 0-255
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return [r, g, b]


# --------- Vehiculo y Rastreador ----------

class Vehicle:
    def __init__(self, contour):
        self._id = uuid.uuid1()
        self._x, self._y, self._w, self._h = contour
        self.color = random_color()
        self._kalman_position = kalman = cv2.KalmanFilter(4, 2)
        kalman.measurementMatrix = np.array([[1, 0, 0, 0], [0, 1, 0, 0]], np.float32)
        kalman.transitionMatrix = np.array([[1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32)
        kalman.processNoiseCov = np.array([[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]], np.float32) * 0.05
        kalman.statePre = np.array([[self.centroid[X_POS]], [self.centroid[Y_POS]], [0], [5]], np.float32)
        kalman.statePost = np.array([[self.centroid[X_POS]], [self.centroid[Y_POS]], [0], [5]], np.float32)
        # self._kalman_position.correct(np.array(self.centroid))

    def update_contour(self, contour):
        """
         Permite actualizar el contorno del vehículo de acuerdo con los nuevos valores en el cuadro actual. También actualiza el
         Filtro de Kalman para que las predicciones sean más precisas en el futuro
         : param contour: una tupla (x, y, w, h) que representa el nuevo contorno
        """
        self._x, self._y, self._w, self._h = contour
        self._kalman_position.correct(np.array([[self.centroid[X_POS]], [self.centroid[Y_POS]]], np.float32))

    def predict_kalman_position(self):
        """
        : return: posición predicha (x, y) del centroide del vehículo
        """
        prediction = self._kalman_position.predict()
        return prediction[X_POS][0], prediction[Y_POS][0]

    @property
    def id(self):
        return id

    @property
    def centroid(self):
        return self._x + self._w // 2, self._y + self._h // 2

    @property
    def contour(self):
        return self._x, self._y, self._w, self._h


class VehicleTracker:
    def __init__(self, frame_source, initial_background, counter_line=0.7):
        self._frame_source = frame_source

        self._bg_subtractor = cv2.createBackgroundSubtractorMOG2()
        self._bg_subtractor.apply(cv2.imread(initial_background), None, 1.0)

        self._frame_reader = cv2.VideoCapture()
        self._frame_reader.open(frame_source)

        self._counter_line = counter_line

        self._width = int(self._frame_reader.get(cv2.CAP_PROP_FRAME_WIDTH))
        self._height = int(self._frame_reader.get(cv2.CAP_PROP_FRAME_HEIGHT))

        self._counter_line_px = int(self._counter_line * self._height)

        self._vehicles = []  # Los vehículos que se están rastreando en el cuadro actual

        self._passed_count = 0

        self._cur_frame = None
        self._fg_mask = None

    def increment_frame(self):
        """
         Lee el siguiente fotograma del video dado. Vuelve a calcular qué vehículos están en el cuadro y dónde.
         : return: una tupla (número_vehículos, éxito) donde cuenta_vehículos es el número de vehículos que cruzaron la línea
         hasta el fotograma actual (incluido), y el éxito es si realmente hubo otro fotograma, es decir, el video
         aún no ha terminado
        """

        # 1. Lea el siguiente cuadro de la fuente de entrada
        ret, frame = self._frame_reader.read()
        if not ret:
            return self._passed_count, False
        if are_same_picture(frame, self._cur_frame):
            return self.increment_frame()  # next frame

        # 2. Detecta vehículos en el marco actual
        self._cur_frame = frame
        frame_vehicles = self.detect_vehicles()

        # 3. Coincidencia entre vehículos antiguos y vehículos con estructura: cree vehículos nuevos donde sea necesario
        # También cuente la cantidad de vehículos que pasaron la línea
        new_vehicles = []
        for contour, centroid in frame_vehicles:
            nearest = self.find_near_vehicle(centroid)
            if nearest is None:
                new_vehicles.append(Vehicle(contour))
            else:
                self._vehicles.remove(nearest)  # para que ningún otro contorno lo señale
                new_vehicles.append(nearest)
                # compruebe si el vehículo acaba de cruzar la línea
                old_centroid = nearest.centroid
                nearest.update_contour(contour)
                if old_centroid[Y_POS] <= self._counter_line_px < centroid[Y_POS]:
                    self._passed_count += 1
        self._vehicles = new_vehicles

        return self._passed_count, True

    def detect_vehicles(self):
        """
        Utiliza el sustractor de fondo propio y el marco actual para calcular la máscara de primer plano del marco actual y detectar
        los vehículos en el marco actual
        : volver: una lista de los contornos del vehículo del cuadro actual
        """
        self._fg_mask = self._bg_subtractor.apply(self.current_frame, None, 0.005)
        self._fg_mask = detector.filter_mask(self._fg_mask)
        return detector.detect_vehicles(self._fg_mask)

    def find_near_vehicle(self, centroid, threshold=30):
        """
         : param centroide: un punto en el plano 2d del marco
         : umbral de parámetro: una distancia que se considera demasiado lejana para que un objeto pase en dos fotogramas consecutivos
         : return: Un vehículo cercano o Ninguno
        """
        if len(self._vehicles) == 0:
            return None

        nearest = self._vehicles[0]
        for vehicle in self._vehicles:
            predicted_pos = vehicle.predict_kalman_position()
            if euclid(predicted_pos, centroid) < euclid(nearest.centroid, centroid):
                nearest = vehicle

        if euclid(nearest.centroid, centroid) > threshold:
            return None
        else:
            return nearest

    def mark_vehicles(self):
        """
        : retorno: el cuadro actual, con marcas alrededor de los vehículos y la línea de separación
        """
        processed = self.current_frame.copy()

        line_dimensions = (0, self._counter_line_px), (self.current_frame.shape[1], self._counter_line_px)
        cv2.line(processed, line_dimensions[0], line_dimensions[1], DIVIDER_COLOUR, 1)
        for vehicle in self._vehicles:
            x, y, w, h = vehicle.contour
            cv2.rectangle(processed, (x, y), (x + w - 1, y + h - 1), vehicle.color, 1)
            cv2.circle(processed, vehicle.centroid, 2, CENTROID_COLOUR, -1)

        return processed

    @property
    def current_frame(self):
        return self._cur_frame

    @property
    def foreground(self):
        return self._fg_mask


# ---------------- MENU ------------------

def input_params(args):
    default_params = {
        'video': './input/Av28julio.mp4',
        'background': './input/background.jpg',
        'show_blobs': True,
        'frame_by_frame': False,
        'line_height': 0.7
    }
    ans = default_params
    i = 1
    while i < len(args):
        if args[i] == '-v':
            ans['video'] = args[i + 1]
            i += 2
        elif args[i] == '-b':
            ans['background'] = args[i + 1]
            i += 2
        elif args[i] == '--hide-blobs':
            ans['show_blobs'] = False
            i += 1
        elif args[i] == '--fbf':
            ans['frame_by_frame'] = True
            i += 1
        elif args[i] == '-l':
            ans['line_height'] = float(args[i + 1])
            i += 2
            if not 0 < ans['line_height'] < 1:
                print('La altura de la línea de entrada debe ser un punto flotante entre 0 y 1.')
                exit(1)
        elif args[i] == '-h' or args[i] == '--help':
            print(__doc__)
            exit(0)
        else:
            print('Comando desconocido {}.'.format(args[i]))
            print(__doc__)
            exit(1)
    return ans


if __name__ == '__main__':
    parameters = input_params(sys.argv)

    tracker = VehicleTracker(parameters['video'], parameters['background'], counter_line=parameters['line_height'])
    while True:

        # 1. Increment Frame
        vehicles_count, success = tracker.increment_frame()
        if not success:
            break

        # 2. Output Results
        if parameters['show_blobs']:
            cv2.imshow('Blobs', tracker.foreground)
        cv2.imshow('Cuadro actual', tracker.mark_vehicles())
        print('Hasta ahora, {} vehículos cruzaron la línea'.format(vehicles_count))

        # 3. Wait before next frame
        wait_time = 0 if parameters['frame_by_frame'] else 20
        key = cv2.waitKey(wait_time)
        if key == ESC_KEY:
            break
