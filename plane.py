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
