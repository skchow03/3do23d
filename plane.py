def get_plane(p1, p2, p3):

    max_value_32 = 2147483647
    max_value_64 = 9223372036854775807

    X1,Y1,Z1 = p1
    X2,Y2,Z2 = p2
    X3,Y3,Z3 = p3

    A = ((Y2-Y1)*(Z3-Z1))-((Z2-Z1)*(Y3-Y1))
    B = ((Z2-Z1)*(X3-X1))-((X2-X1)*(Z3-Z1))
    C = ((X2-X1)*(Y3-Y1))-((Y2-Y1)*(X3-X1))
    D = (-A*X1 - B*Y1 - C*Z1)

    while (abs(A) >= max_value_32) or (abs(B) >= max_value_32) or (abs(C) >= max_value_32) or (abs(D) >= max_value_64):
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

    zero = A*point[0] + B*point[1] + C*point[2] + D
    zero1 = A*point[0]*2 + B*point[1]*2 + C*point[2]*2 + D*2
    zero2 = A*point[0]*4 + B*point[1]*4 + C*point[2]*2 + D*4
    zero3 = A*point[0]*8 + B*point[1]*8 + C*point[2]*8 + D*8

    if zero == 0 or zero1 == 0 or zero2 == 0 or zero3 == 0:
        return True
    else:
        return False

def compare_planes(plane1, plane2):
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



def _extended_gcd(a, b):
    if b == 0:
        return (abs(a), 1 if a >= 0 else -1, 0)
    g, x1, y1 = _extended_gcd(b, a % b)
    return (g, y1, x1 - (a // b) * y1)


def _gcd3(a, b, c):
    import math
    return math.gcd(math.gcd(abs(a), abs(b)), abs(c))


def _find_integer_point_on_plane(A, B, C, D):
    """Return one integer point on A*x + B*y + C*z + D = 0, or None."""
    if A == 0 and B == 0 and C == 0:
        return None

    for coeff, axis in ((A, 0), (B, 1), (C, 2)):
        if coeff != 0 and -D % coeff == 0:
            point = [0, 0, 0]
            point[axis] = -D // coeff
            return tuple(point)

    g, x_coeff, y_coeff = _extended_gcd(A, B)
    if C:
        g, xy_scale, z_coeff = _extended_gcd(g, C)
        if -D % g != 0:
            return None
        scale = -D // g
        return (x_coeff * xy_scale * scale, y_coeff * xy_scale * scale, z_coeff * scale)

    if -D % g != 0:
        return None
    scale = -D // g
    return (x_coeff * scale, y_coeff * scale, 0)


def _primitive_plane_directions(A, B, C):
    """Return two integer vectors perpendicular to primitive normal (A,B,C)."""
    import itertools

    # Small bounded search is enough for primitive integer normals and avoids
    # special-casing the many possible zero-component combinations.
    candidates = []
    for x, y, z in itertools.product(range(-8, 9), repeat=3):
        if (x, y, z) == (0, 0, 0):
            continue
        if A * x + B * y + C * z == 0:
            candidates.append((x, y, z))

    for d1, d2 in itertools.permutations(candidates, 2):
        cross = (
            d1[1] * d2[2] - d1[2] * d2[1],
            d1[2] * d2[0] - d1[0] * d2[2],
            d1[0] * d2[1] - d1[1] * d2[0],
        )
        if cross == (A, B, C):
            return d1, d2
        if cross == (-A, -B, -C):
            return d2, d1

    return None


def calculate_points_for_plane(A, B, C, D):
    """Return three non-collinear integer points whose plane matches A,B,C,D.

    Returns None when no integer point can satisfy the plane or when suitable
    integer direction vectors cannot be found.
    """
    g = _gcd3(A, B, C)
    if g == 0 or D % g != 0:
        return None

    p1 = _find_integer_point_on_plane(A, B, C, D)
    if p1 is None:
        return None

    primitive_normal = (A // g, B // g, C // g)
    directions = _primitive_plane_directions(*primitive_normal)
    if directions is None:
        return None

    d1, d2 = directions
    p2 = (p1[0] + d1[0] * g, p1[1] + d1[1] * g, p1[2] + d1[2] * g)
    p3 = (p1[0] + d2[0], p1[1] + d2[1], p1[2] + d2[2])

    calculated_plane = get_plane(p1, p2, p3)
    if calculated_plane != (A, B, C, D) and compare_planes(calculated_plane, (A, B, C, D)) != 0:
        return None

    max_value_32 = 2147483647
    if any(abs(coord) > max_value_32 for point in (p1, p2, p3) for coord in point):
        return None

    return p1, p2, p3
