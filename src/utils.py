import math


def calculate_distance(point1, point2):
    x1, y1 = point1
    x2, y2 = point2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def minimum_distance(line, point):
    # v, w are points defining the line segment, and p is the point.
    v, w, p = line[0], line[1], point

    l2 = math.dist(v, w) ** 2  # i.e., |w-v|^2 - avoid a sqrt
    if l2 == 0:
        return math.dist(p, v)  # v == w case
    t = max(0, min(1, ((p[0] - v[0]) * (w[0] - v[0]) + (p[1] - v[1]) * (w[1] - v[1])) / l2))
    projection = (v[0] + t * (w[0] - v[0]), v[1] + t * (w[1] - v[1]))
    return math.dist(p, projection)


def line_intersection(line1, line2, finite_line=True):
    xdiff = (line1[0][0] - line1[1][0], line2[0][0] - line2[1][0])
    ydiff = (line1[0][1] - line1[1][1], line2[0][1] - line2[1][1])

    def det(a, b):
        return a[0] * b[1] - a[1] * b[0]

    div = det(xdiff, ydiff)

    # Lines do not intersect
    if div == 0:
        return None

    d = (det(*line1), det(*line2))
    x = round(det(d, xdiff) / div)
    y = round(det(d, ydiff) / div)

    if finite_line:
        # Check if the intersection is within the bounds of line1
        if not (min(line1[0][0], line1[1][0]) <= x <= max(line1[0][0], line1[1][0]) and
                min(line1[0][1], line1[1][1]) <= y <= max(line1[0][1], line1[1][1])):
            return None

        # Check if the intersection is within the bounds of line2
        if not (min(line2[0][0], line2[1][0]) <= x <= max(line2[0][0], line2[1][0]) and
                min(line2[0][1], line2[1][1]) <= y <= max(line2[0][1], line2[1][1])):
            return None

    return x, y


def rotate_polygon(polygon, angle):
    # Convert angle to radians
    angle_rad = math.radians(angle)
    # Define the rotation matrix
    rotation_matrix = [
        [math.cos(angle_rad), -math.sin(angle_rad)],
        [math.sin(angle_rad), math.cos(angle_rad)]
    ]
    # Apply the rotation matrix to each point
    rotated_polygon = []
    for point in polygon:
        rotated_point = [
            point[0] * rotation_matrix[0][0] + point[1] * rotation_matrix[0][1],
            point[0] * rotation_matrix[1][0] + point[1] * rotation_matrix[1][1]
        ]
        rotated_polygon.append(rotated_point)
    return rotated_polygon


def elem_wise_add(list_1, list_2):
    return [x + y for x, y in zip(list_1, list_2)]
