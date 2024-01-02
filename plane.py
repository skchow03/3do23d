import math

def get_plane(p1, p2, p3):
    """ Given three points, returns the coefficients of the plane 
    equation which corresponds to the first 4 values in the BSP 
    functions"""

    max_value_32 = 2147483647
    max_value_64 = 9223372036854775807

    X1,Y1,Z1 = p1
    X2,Y2,Z2 = p2
    X3,Y3,Z3 = p3

    A = ((Y2-Y1)*(Z3-Z1))-((Z2-Z1)*(Y3-Y1))
    B = ((Z2-Z1)*(X3-X1))-((X2-X1)*(Z3-Z1))
    C = ((X2-X1)*(Y3-Y1))-((Y2-Y1)*(X3-X1))
    D = (-A*X1 - B*Y1 - C*Z1)

    # Keep dividing by 2 until we get A, B, C and D below the maximum
    # values allowed.
    while (abs(A) >= max_value_32) \
           or (abs(B) >= max_value_32) \
           or (abs(C) >= max_value_32) \
           or (abs(D) >= max_value_64):
        A /= 2
        B /= 2
        C /= 2
        D /= 2

    A = int(A)
    B = int(B)
    C = int(C)
    D = int(D)

    return A, B, C, D

def is_on_plane(A,B,C,D,point):
    """Given a plane and a point, returns True if the point is on the
    plane and False if it isn't."""

    zero = A*point[0] + B*point[1] + C*point[2] + D
    zero1 = A*point[0]*2 + B*point[1]*2 + C*point[2]*2 + D*2
    zero2 = A*point[0]*4 + B*point[1]*4 + C*point[2]*2 + D*4
    zero3 = A*point[0]*8 + B*point[1]*8 + C*point[2]*8 + D*8

    if zero == 0 or zero1 == 0 or zero2 == 0 or zero3 == 0:
        return True
    else:
        return False

def compare_planes2(plane1, plane2):
    """
    Calculate the angle between the normal vectors of two planes.
    Each plane is defined by a tuple of 4 values (A, B, C, D) corresponding to the plane equation Ax + By + Cz + D = 0.

    :param plane1: Tuple (A, B, C, D) for the first plane
    :param plane2: Tuple (A, B, C, D) for the second plane
    :return: Angle in degrees between the two normal vectors, or None if one of the planes is not well-defined.
    """
    # Extract coefficients
    A1, B1, C1, _ = plane1
    A2, B2, C2, _ = plane2

    # Calculate the magnitudes of the normal vectors
    magnitude1 = math.sqrt(A1**2 + B1**2 + C1**2)
    magnitude2 = math.sqrt(A2**2 + B2**2 + C2**2)

    # Check if either magnitude is zero, indicating a non-well-defined plane
    if magnitude1 == 0 or magnitude2 == 0:
        return None

    # Calculate the dot product of the normals
    dot_product = A1 * A2 + B1 * B2 + C1 * C2

    # Calculate the cosine of the angle
    cos_angle = dot_product / (magnitude1 * magnitude2)

    # Clamp the cos_angle to the range [-1, 1]
    cos_angle = max(-1.0, min(1.0, cos_angle))

    # Calculate the angle in radians and then convert to degrees
    angle_radians = math.acos(cos_angle)
    angle_degrees = math.degrees(angle_radians)

    return angle_degrees

def compare_planes(plane1, plane2):
    """Compares the coefficients for two planes and returns the largest
    difference between two corresponding coefficients."""

    A1,B1,C1,D1 = plane1
    A2,B2,C2,D2 = plane2

    diffA = A2-A1
    if A2 != 0:
        diffA = diffA / A2

    diffB = B2-B1
    if B2 != 0:
        diffB = diffB / B2

    diffC = C2-C1
    if C2 != 0:
        diffC = diffC / C2

    diffD = D2-D1
    if D2 != 0:
        diffD = diffD / D2

    max_diff = max([abs(diffA), abs(diffB), abs(diffC), abs(diffD)])

    return max_diff

## TO DO: generate points given a plane

def get_integer_points_from_any_plane(A, B, C, D):
    """ Generate three integer points on any plane given the coefficients A, B, C, D of the plane equation """

    # Check if A, B, and C are all zero
    if A == 0 and B == 0 and C == 0:
        raise ValueError("Invalid plane coefficients")

    # Helper functions to calculate x, y, z
    def calculate_x(y, z):
        if A == 0:
            raise ValueError("Cannot calculate x when A is zero")
        return int(round(-(B * y + C * z + D) / A))

    def calculate_y(x, z):
        if B == 0:
            raise ValueError("Cannot calculate y when B is zero")
        return int(round(-(A * x + C * z + D) / B))

    def calculate_z(x, y):
        if C == 0:
            raise ValueError("Cannot calculate z when C is zero")
        return int(round(-(A * x + B * y + D) / C))

    # Generate points based on which coefficients are non-zero
    if A != 0:
        # A is non-zero, calculate x
        p1 = (calculate_x(0, 0), 0, 0)
        p2 = (calculate_x(1, 0), 1, 0)
        p3 = (calculate_x(0, 1), 0, 1)
    elif B != 0:
        # B is non-zero, calculate y
        p1 = (0, calculate_y(0, 0), 0)
        p2 = (1, calculate_y(1, 0), 0)
        p3 = (0, calculate_y(0, 1), 1)
    else:
        # C is non-zero, calculate z
        p1 = (0, 0, calculate_z(0, 0))
        p2 = (1, 0, calculate_z(1, 0))
        p3 = (0, 1, calculate_z(0, 1))

    return p1, p2, p3