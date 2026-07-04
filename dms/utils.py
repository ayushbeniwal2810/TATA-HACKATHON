import math


def euclidean(p1, p2):
    return math.dist(p1, p2)


def eye_aspect_ratio(eye6):
    # eye6 = [p1, p2, p3, p4, p5, p6]
    # EAR = (||p2-p6|| + ||p3-p5||) / (2*||p1-p4||)
    A = euclidean(eye6[1], eye6[5])
    B = euclidean(eye6[2], eye6[4])
    C = euclidean(eye6[0], eye6[3])
    if C == 0:
        return 0.0
    return (A + B) / (2.0 * C)


def mouth_aspect_ratio(mouth4):
    # mouth4 = [left, right, top, bottom]
    left, right, top, bottom = mouth4
    horizontal = euclidean(left, right)
    vertical = euclidean(top, bottom)
    if horizontal == 0:
        return 0.0
    return vertical / horizontal


def map_range(x, in_min, in_max, out_min, out_max):
    if in_max == in_min:
        return out_min
    x = max(in_min, min(in_max, x))
    return out_min + (x - in_min) * (out_max - out_min) / (in_max - in_min)