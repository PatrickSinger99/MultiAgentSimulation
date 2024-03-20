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


print(line_intersection(((10, 10), (20, 10)), ((15, 15), (15, 8)), finite_line=True))
