import cv2
import numpy as np
from scipy.ndimage import measurements
from scipy.signal import convolve2d


# ------------------- Utils ---------------------

def get_centroid(x, y, w, h):
    """
    :param x: Low x value of the rectangle
    :param y: Low y value of the rectangle
    :param w: Width of the rectangle
    :param h: Height of the rectangle
    :return: The (x, y) point that is the center of the rectangle
    """
    x1 = int(w / 2)
    y1 = int(h / 2)

    cx = x + x1
    cy = y + y1

    return cx, cy


def rectangle_contour(x, y, w, h):
    """
    :param x: Low x value of the rectangle
    :param y: Low y value of the rectangle
    :param w: Width of the rectangle
    :param h: Height of the rectangle
    :return: A list of the four points that make up the rectangle's contour
    """
    point1 = (x, y)
    point2 = (x + w - 1, y)
    point3 = (x, y + h - 1)
    point4 = (x + w - 1, y + h - 1)
    return [point1, point2, point3, point4]


# -------- Clean Image and Find Vehicles ---------

def filter_mask(fg_mask):
    """
    :param fg_mask: A noisy foreground mask
    :return: A cleaner version of the foreground mask, clearer objects, ready for further processing
    """
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    opening = cv2.dilate(cv2.erode(fg_mask, kernel), kernel)

    mask_colors = sorted(np.unique(fg_mask))
    BLACK, GRAY, WHITE = 0, 1, 2
    mask_white = (opening == mask_colors[WHITE])
    mask_gray = (opening == mask_colors[GRAY])

    spread_kernel = np.ones((20, 1))
    white_spread = convolve2d(mask_white, spread_kernel, mode='same')
    filling = np.logical_and(white_spread > 0, mask_gray)

    filled = np.where(np.logical_or(filling, mask_white), mask_colors[WHITE], mask_colors[BLACK])

    return cv2.dilate(filled, kernel)


def find_contours(binary_image):
    """
    :param binary_image: A binary image with different objects inside, objects are 4-connected
    :return: A list of 4-point contours of the objects in the picture
    """
    labeled_image, contours_count = measurements.label(binary_image)

    # rectangles = []
    # for label in range(1, contours_count):
    #     points = np.nonzero(np.equal(labeled_image, label))
    #     points = np.transpose(np.array(points))
    #     rectangles.append(cv2.boundingRect(points))
    #
    # ans = [rect_to_contour(r[1], r[0], r[3], r[2]) for r in rectangles]

    slices = measurements.find_objects(labeled_image)

    ans = []
    for slice_y, slice_x in slices:
        x, y, w, h = slice_x.start, slice_y.start, slice_x.stop - slice_x.start, slice_y.stop - slice_y.start
        ans.append([(x, y), (x + w - 1, y), (x, y + h - 1), (x + w - 1, y + h - 1)])

    return ans


def detect_vehicles(fg_mask):
    """
    :param fg_mask: A clean foreground mask, given as a 2d array image
    :return: A list of objects of type (rectange_dimensions, centroid) where rectange_dimensions is (x, y, w, h) and
     centroid is (x, y)
    """

    MIN_CONTOUR_WIDTH = 10
    MIN_CONTOUR_HEIGHT = 10

    # Find the contours of any vehicles in the image
    # _, contours, _ = cv2.findContours(fg_mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = find_contours(fg_mask)

    matches = []
    for (i, contour) in enumerate(contours):
        (x, y, w, h) = cv2.boundingRect(np.array(contour))
        contour_valid = (w >= MIN_CONTOUR_WIDTH) and (h >= MIN_CONTOUR_HEIGHT)

        if not contour_valid:
            continue

        centroid = get_centroid(x, y, w, h)

        matches.append(((x, y, w, h), centroid))

    return matches


# -------------- Calculate Background --------------

class Averager:
    def __init__(self):
        self._average = None
        self._elements_count = 0

    def add_element(self, x):
        if self._average is None:
            self._average = x
            self._elements_count = 1
        else:
            self._average = (self._average * self._elements_count + x) / (self._elements_count + 1)
            self._elements_count += 1

    @property
    def outcome(self):
        return self._average


class Medianer:
    def __init__(self):
        self._elements = []  # a list of 4d arrays of the same shape

    def add_element(self, x):
        self._elements.append(x)

    @property
    def outcome(self):
        print(np.array(self._elements).shape)
        median = np.median(np.array(self._elements), axis=0)
        print(median.shape)
        return median


def get_background(video):
    """
    :param video: A path to a video on the hard disk
    :return: The background of the video, using averaging or median techniques
    """
    cap = cv2.VideoCapture()
    cap.open(video)

    frame_mixer = Medianer()
    _, frame = cap.read()
    frame_mixer.add_element(frame)
    frame_num = -1
    while True:
        frame_num += 1
        ret, frame = cap.read()
        if not ret:
            break
        if frame_num >= 70:
            frame_mixer.add_element(frame)

    cv2.imwrite('background.jpg', frame_mixer.outcome)
    return frame_mixer.outcome