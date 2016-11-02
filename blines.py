"""
Implementation of the Bresenham Algorithm
This method returns the discrete (integral) coordinates
of all points along a line between two arbitrary points in
an array.

For vertical or horizontal lines this trivially returns the
row or column. For diagonal lines, it discerns which array
elements are crossed by the line and returns the points
"""
import numpy as np


def b_line(x0, y0, xf, yf):
    """ Implementation of Bresenham Algorithm - Adapted from Java
    Based on algorithm listed here: http://tech-algorithm.com/articles/drawing-line-using-bresenham-algorithm/
    Translated to Python by Maxwell Grady

    :param x0: int initial x location of line segment
    :param y0: int initial y location of line segment
    :param xf: int final x location of line segment
    :param yf: int final y location of line segment
    :returns:  list of points in (r,c) format for pixels along the line segment
    """
    # TODO: if w or h is zero, simply return a list of slice points
    # This may require knowledge of the data source, however

    w = xf - x0  # run
    h = yf - y0  # rise
    dx1 = 0
    dy1 = 0
    dx2 = 0
    dy2 = 0

    # configure settings for which Octant the line falls in
    if w < 0:
        dx1 = -1
        dx2 = -1
    elif w > 0:
        dx1 = 1
        dx2 = 1

    if h < 0:
        dy1 = -1
    elif h > 0:
        dy1 = 1

    longest = abs(w)
    shortest = abs(h)
    if not longest > shortest:
        longest = abs(h)
        shortest = abs(w)
        if h < 0:
            dy2 = -1
        elif h > 0:
            dy2 = 1
        dx2 = 0

    # start calculation
    numerator = longest >> 1
    x = x0
    y = y0  # the first point appended will be the initial point of the line
    points = []
    for i in range(longest + 1):
        # arrays use (r,c) indexing
        # thus we swap x and y
        # x labels the collumn, y labels the row
        points.append((y, x))
        numerator += shortest
        if not numerator < longest:
            numerator -= longest
            x += dx1
            y += dy1
        else:
            x += dx2
            y += dy2
    return points

"""
def main():
    print("Testing b_line algorithm ...")
    test = np.arange(25).reshape((5, 5))
    print("Testing 5x5 array: \n")
    print(test)


if __name__ == '__main__':
    main()
"""