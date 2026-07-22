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
    """Return (g, x, y) where ax + by = g = gcd(a, b)."""
    old_r, r = abs(a), abs(b)
    old_s, s = 1, 0
    old_t, t = 0, 1

    while r:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    if a < 0:
        old_s = -old_s
    if b < 0:
        old_t = -old_t

    return old_r, old_s, old_t

def _cross(u, v):
    return (
        u[1] * v[2] - u[2] * v[1],
        u[2] * v[0] - u[0] * v[2],
        u[0] * v[1] - u[1] * v[0],
    )

def _is_zero_vector(vector):
    return all(value == 0 for value in vector)

def _are_collinear(u, v):
    return _is_zero_vector(_cross(u, v))

def get_points_on_plane(A, B, C, D):
    """Return three integer points on Ax + By + Cz + D = 0.

    Returns None if the plane has no integer solution or has an invalid normal.
    """
    if A == 0 and B == 0 and C == 0:
        return None

    gcd_ab, x_ab, y_ab = _extended_gcd(A, B)
    gcd_abc, z_ab, z_c = _extended_gcd(gcd_ab, C)

    if D % gcd_abc != 0:
        return None

    scale = -D // gcd_abc
    p0 = (x_ab * z_ab * scale, y_ab * z_ab * scale, z_c * scale)
    normal = (A, B, C)

    directions = [
        _cross(normal, (1, 0, 0)),
        _cross(normal, (0, 1, 0)),
        _cross(normal, (0, 0, 1)),
    ]
    directions = [direction for direction in directions if not _is_zero_vector(direction)]

    for i, direction1 in enumerate(directions):
        for direction2 in directions[i + 1:]:
            if not _are_collinear(direction1, direction2):
                return (
                    p0,
                    (p0[0] + direction1[0], p0[1] + direction1[1], p0[2] + direction1[2]),
                    (p0[0] + direction2[0], p0[1] + direction2[1], p0[2] + direction2[2]),
                )

    return None
