"""
    Vehicle Tracker
    This module tracks vehicles in a video of a highway where the camera is still.
    Usage:
        python tracker.py [options]
    Options:
        -v <video_path>     A path from the current directory to the input video. Default value: ./input/Highway1.mp4
        -b <bg_path>        A path from the current directory to an image file with a background model that fits the
                            input video. Default value: ./input/background.jpg, fits the given video files Highway1.mp4,
                            Highway3.mp4, Highway4.mp4.
                            Notice: using AVI files are problematic on some systems.
        --hide-blobs        If this parameter is used, the window showing the current frame's vehicle blobs is not
                            shown. In default, this window is shown.
        --fbf               Frame-by-frame. This changes the mode from video mode to manual mode. Moving between the
                            video frames stops being automatic, and a keypress (i.e. spacebar) is needed to continue to
                            the next frame.
        -l <height>         The height of the counting-line. This is a floating point number between 0 and 1, exclusive.
                            It measures the distance from the top of the video, where a line will be, and every vehicle
                            that passes the line will be counted. After each frame, the number of vehicles that have
                            already passed the line will be outputted to the screen.
                            The default value for this parameter is 0.7, and values under 0.7 are discouraged because
                            the vehicles are far away and in some cases multiple vehicles appear as one. The best values
                            for this parameter are between 0.7 and 0.9 .
        -h, --help          Display this help and exit
    The module is based on tools from the following libraries: NumPy, SciPy, OpenCV
    Code examples that helped build the module:
        Moving Object Recognition -
            http://stackoverflow.com/questions/36254452/counting-cars-opencv-python-issue?rq=1
        Kalman Filter -
            http://stackoverflow.com/questions/29012038/is-there-any-example-of-cv2-kalmanfilter-implementation
"""
import random
import sys
import uuid

import cv2
import detector
import numpy as np
import scipy.spatial.distance as distance

# Tuple indices
X_POS, Y_POS = 0, 1

# Colours for drawing on processed frames
DIVIDER_COLOUR = (255, 255, 0)
BOUNDING_BOX_COLOUR = (255, 0, 0)
CENTROID_COLOUR = (0, 0, 255)

# Keyboard
ESC_KEY = 27


# --------------- Utils -----------------

def euclid(a, b):
    """
    :param a: Array a
    :param b: Array b of the same shape as a
    :return: Euclidean distance between a and b
    """
    return distance.euclidean(a, b)


def are_same_picture(pic1, pic2):
    """
    :param pic1: A Numpy array of shape (width, height, 3), representing a picture
    :param pic2: A Numpy array of the same shape as pic1
    :return: A heuristic guess of whether the two pictures are actually the same one (plus noise) or truly different.
     Useful for comparing following frames in a video
    """
    if pic1 is None or pic2 is None:
        return False
    if pic1.shape != pic2.shape:
        return False
    pixels = pic1.shape[0] * pic1.shape[1]
    return np.sum(np.abs(pic1 - pic2)) < pixels * 35


def random_color():
    """
    :return: List with three random values in the range 0-255
    """
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return [r, g, b]


# --------- Vehicle and Tracker ----------

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
        Allows updating the contour of the vehicle according to the new values in the current frame. Also updates the
         Kalman filter so that predictions are more accurate in the future
        :param contour: A tuple (x, y, w, h) representing the new contour
        """
        self._x, self._y, self._w, self._h = contour
        self._kalman_position.correct(np.array([[self.centroid[X_POS]], [self.centroid[Y_POS]]], np.float32))

    def predict_kalman_position(self):
        """
        :return: Predicted (x, y) position of the vehicle's centroid
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

        self._vehicles = []  # The vehicles being tracked in the current frame

        self._passed_count = 0

        self._cur_frame = None
        self._fg_mask = None

    def increment_frame(self):
        """
        Reads the next frame from the given video. Recalculates what vehicles are in the frame and where.
        :return: A tuple (vehicles_count, success) where vehicles_count is the number of vehicles that crossed the line
         until the current frame (inclusive), and success is whether there really was another frame, i.e. the video
         has not yet ended
        """

        # 1. Read the next frame from the input source
        ret, frame = self._frame_reader.read()
        if not ret:
            return self._passed_count, False
        if are_same_picture(frame, self._cur_frame):
            return self.increment_frame()  # next frame

        # 2. Detect vehicles in the current frame
        self._cur_frame = frame
        frame_vehicles = self.detect_vehicles()

        # 3. Match between old vehicles and frame vehicles - create new vehicles where needed
        #    Also count the number of vehicles that passed the line
        new_vehicles = []
        for contour, centroid in frame_vehicles:
            nearest = self.find_near_vehicle(centroid)
            if nearest is None:
                new_vehicles.append(Vehicle(contour))
            else:
                self._vehicles.remove(nearest)  # so that no other contour points to it
                new_vehicles.append(nearest)
                # check if the vehicle just crossed the line
                old_centroid = nearest.centroid
                nearest.update_contour(contour)
                if old_centroid[Y_POS] <= self._counter_line_px < centroid[Y_POS]:
                    self._passed_count += 1
        self._vehicles = new_vehicles

        return self._passed_count, True

    def detect_vehicles(self):
        """
        Uses self's background subtractor and current frame to calculate the current frame's foreground mask and detect
         the vehicles in the current frame
        :return: A list of vehicle contours from the current frame
        """
        self._fg_mask = self._bg_subtractor.apply(self.current_frame, None, 0.005)
        self._fg_mask = detector.filter_mask(self._fg_mask)
        return detector.detect_vehicles(self._fg_mask)

    def find_near_vehicle(self, centroid, threshold=30):
        """
        :param centroid: A point on the 2d plane of the frame
        :param threshold: A distance, that is considered too far for an object to pass in two consecutive frames
        :return: A near vehicle or None
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
        :return: The current frame, with markings around the vehicles and the separating line
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


# ---------------- Main ------------------

def input_params(args):
    default_params = {
        'video': './input/Highway0.mp4',
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