from binary import *

def papy_angle_to_deg(angle):
    return round((180/2147483648 * angle) * 10)


class Vertex:
    """ Vertices can be Type 0 (coordinates only), Type 1 (includes mip coords),
    or Type 2 (nil)
    """
    def __init__(self, type,x,y,z,mip_x,mip_y):
        self.flav = 0
        self.type = type
        self.x = x
        self.y = y
        self.z = z
        self.mip_x = mip_x
        self.mip_y = mip_y

    def output_text(self):
        if self.type == 1:
            cmd = '[<{}, {}, {}>, T=<{}, {}>]'.format(
                self.x, self.y, self.z, self.mip_x, self.mip_y
            )
        elif self.type == 2:
            cmd = 'NIL'
        elif self.type == 0:
            cmd = '[<{}, {}, {}>]'.format(
                self.x, self.y, self.z
            )
        return cmd

class List:
    def __init__(self):
        self.pointers = []
        self.flav = 11
        self.data = None

    def output_text(self):
        pointer_count = 0
        cmd = 'LIST {'
        if len(self.pointers) == 0:
            return cmd + '}'
        for i in range(0,len(self.pointers)):
            cmd += '_{}'.format(self.pointers[i])
            if i >= len(self.pointers)-1:
                if not self.data:
                    cmd += '}'
                else:
                    cmd += (', '+self.data + '}')
            else:
                if pointer_count > 8:       # Make line break after every 8
                    cmd += ',\n'
                    pointer_count = 0
                else:
                    cmd += ', '
                    pointer_count += 1
        return cmd

class Dynamic:
    def __init__(self, x, y, z, z_rot, y_rot, x_rot, obj_name):
        self.x = x
        self.y = y
        self.z = z
        self.z_rot = papy_angle_to_deg(z_rot)
        self.y_rot = papy_angle_to_deg(y_rot)
        self.x_rot = papy_angle_to_deg(x_rot)
        self.obj_name = obj_name
        self.flav = 15

    def output_text(self):
        return 'DYNAMIC {}, {}, {}, {}, {}, {}, 1, EXTERN "{}"'.format(
                            self.x, self.y, self.z,
                            self.z_rot, self.y_rot, self.x_rot,
                            self.obj_name)

class Poly:
    def __init__(self):
        self.pointers = []
        self.color = 0
        self.flav = 1

    def output_text(self):
        if len(self.unique_pointers) > 2:
            # Check if we have a POLY of only two unique points. If so, it's a LINE. But this should never happen for ICR2 which doesn't support LINE.
            cmd = 'POLY <{}> '.format(self.color) + '{'
            for i in range(0,len(self.pointers)):
                cmd += '_{}'.format(self.pointers[i])
                if i == len(self.pointers)-1:
                    cmd += '}'
                else:
                    cmd += ', '
            return cmd
        else:
            cmd = 'LINE <{}> '.format(self.color) + '{'
            for i in range(0,len(self.unique_pointers)):
                cmd += '_{}'.format(self.unique_pointers[i])
                if i == len(self.unique_pointers)-1:
                    cmd += '}'
                else:
                    cmd += ', '
            return cmd

    def check_unique(self):
        self.unique_pointers = []
        for i in self.pointers:
            if i not in self.unique_pointers:
                self.unique_pointers.append(i)

class PolyT:
    def __init__(self):
        self.pointers = []
        self.color = 0
        self.group = 0
        self.flav = 2

    def output_text(self):
        if len(self.unique_pointers) > 2:
            cmd = 'POLY [T] <{}> '.format(self.color, self.group) + '{'
            for i in range(0,len(self.pointers)):
                cmd += '_{}'.format(self.pointers[i])
                if i == len(self.pointers)-1:
                    cmd += '}'
                else:
                    cmd += ', '
            return cmd
        else:
            cmd = 'LINE <{}> '.format(self.color) + '{'
            for i in range(0,len(self.unique_pointers)):
                cmd += '_{}'.format(self.unique_pointers[i])
                if i == len(self.unique_pointers)-1:
                    cmd += '}'
                else:
                    cmd += ', '
            return cmd

    def check_unique(self):
        self.unique_pointers = []
        for i in self.pointers:
            if i not in self.unique_pointers:
                self.unique_pointers.append(i)

class Material:
    def __init__(self, mip_number, mip_name, color, flavor_offset):
        self.mip_number = mip_number
        self.mip_name = mip_name
        self.color = color
        self.flavor_offset = flavor_offset
        self.flav = 4
        self.group = 0

    def output_text(self):
        cmd = 'MATERIAL MIP="{}", GROUP={}, _{}'.format(
            self.mip_name, self.group, self.flavor_offset)
        return cmd

class Dyno:
    def __init__(self,start_dlong, end_dlong,dlat1,dlat2):
        self.start_dlong = start_dlong
        self.end_dlong = end_dlong
        self.dlat1 = dlat1
        self.dlat2 = dlat2
        self.flav = 12

    def output_text(self):
        cmd = 'DYNO { '+'{}, {}, {}, {}'.format(
            self.start_dlong, self.end_dlong, self.dlat1, self.dlat2) + ' }'
        return cmd

class Face:
    """ FACE (Flavor 5) and FACE2 (Flavor 6)
    """
    def __init__(self, body, cur_pos, type):
        self.v1 = get_int32(body, cur_pos+4)
        self.v2 = get_int32(body, cur_pos+8)
        self.v3 = get_int32(body, cur_pos+12)
        self.v4 = get_int64(body, cur_pos+16)
        self.flavor1 = get_int32(body, cur_pos+24)
        self.type = type
        if type == 6:
            self.flav = 6
            self.flavor2 = get_int32(body, cur_pos+28)
        elif type == 5:
            self.flav = 5
        self.plane = (self.v1, self.v2, self.v3, self.v4)
        self.plane_pointers = None

    def output_text(self):
        if self.type == 5:
            cmd = 'FACE '
        elif self.type == 6:
            cmd = 'FACE2 '

        if self.plane_pointers:
            ptr1, ptr2, ptr3 = self.plane_pointers
            cmd += '(_{}, _{}, _{}), _{}'.format(ptr1, ptr2, ptr3, self.flavor1)
        else:
            cmd += '({}, {}, {}, {}), _{}'.format(
                self.v1, self.v2, self.v3, self.v4, self.flavor1)

        if self.type == 6:
            cmd += ', _{}'.format(self.flavor2)
        elif self.type == 5:
            cmd += ''

        return cmd

class BSP:
    def __init__(self, body, cur_pos, type):
        self.v1 = get_int32(body,cur_pos+4)
        self.v2 = get_int32(body,cur_pos+8)
        self.v3 = get_int32(body,cur_pos+12)
        self.v4 = get_int64(body,cur_pos+16)
        self.p1 = get_int32(body,cur_pos+24)
        self.p2 = get_int32(body,cur_pos+28)
        if type == 7 or type == 8 or type == 9:
             self.p3 = get_int32(body,cur_pos+32)
        if type == 9:
             self.p4 = get_int32(body,cur_pos+36)
        self.flav = type
        self.plane_pointers = None

    def output_text(self):
        if self.plane_pointers:
            ptr1, ptr2, ptr3 = self.plane_pointers
            plane_cmd = '(_{}, _{}, _{}),'.format(ptr1, ptr2, ptr3)
        else:
            plane_cmd = '({}, {}, {}, {}),'.format(self.v1, self.v2, self.v3, self.v4)

        if self.flav == 7:
            cmd = 'BSPF {} _{}, _{}, _{}'.format(
                plane_cmd, self.p1, self.p3, self.p2)
            return cmd
        elif self.flav == 8:
            cmd = 'BSPA {} _{}, _{}, _{}'.format(
                plane_cmd, self.p1, self.p3, self.p2)
            return cmd
        elif self.flav == 9:
            cmd = 'BSP2 {} _{}, _{}, _{}, _{}'.format(
                plane_cmd, self.p1, self.p4, self.p3, self.p2)
            return cmd
        elif self.flav == 10:
            cmd = 'BSPN {} _{}, _{}'.format(
                plane_cmd, self.p1, self.p2)
            return cmd

    def get_pointers(self):
        if self.flav == 10:
            return (self.p1, self.p2)
        if self.flav == 9:
            return (self.p1, self.p2, self.p3, self.p4)
        else:
            return (self.p1, self.p2, self.p3)

class Data:
    def __init__(self, sw1, sw2, sw3, sw4):
        self.sw1 = sw1
        self.sw2 = sw2
        self.sw3 = sw3
        self.sw4 = sw4
        self.flav = 17

    def output_text(self):
        cmd = 'DATA { ' + '{}, {}, {}, {}'.format(
            self.sw1, self.sw2, self.sw3, self.sw4) + ' }'
        return cmd

class Superobj:
    def __init__(self):
        self.pointers = []
        self.prev_flavor = 0
        self.flav = 16

    def output_text(self):
        pointer_count = 0
        cmd = 'SUPEROBJ _{}, '.format(self.prev_flavor) + '{ '

        for i in range(0,len(self.pointers)):
            cmd += '_{}'.format(self.pointers[i])
            if i == len(self.pointers)-1:
                cmd += ' }'
            else:
                if pointer_count > 8:       # Make line break after every 8
                    cmd += ',\n'
                    pointer_count = 0
                else:
                    cmd += ', '
                    pointer_count += 1
        return cmd

class Recolor:
    # This function is not converted using any available 3d23do tool. You may need to
    # manually hex edit the 3do file

    def __init__(self):
        self.recolors = []
        self.flav = 14

    def output_text(self):
        cmd = 'RECOLOR ('
        for i in range(0, len(self.recolors)):
            cmd += '{}: {}'.format(self.recolors[i][0], self.recolors[i][1])
            if i == len(self.recolors)-1:
                cmd += ')'
            else:
                cmd += ', '
        return cmd

class SwitchDistance:
    # ICR2 only uses SWITCH DISTANCE for car models. Not used in tracks. N3 tracks
    # have SWITCH DISTANCE with fewer parameters. ICR2 cars have 9 (i.e. including 4 distances).

    def __init__(self, res1, res2, res3, res4, res5, res6, res7, res8, res9):
        self.res1 = res1
        self.res2 = res2
        self.res3 = res3
        self.res4 = res4
        self.res5 = res5
        self.res6 = res6
        self.res7 = res7
        self.res8 = res8
        self.res9 = res9
        self.flav = 13

    def output_text(self):
        if self.res2 == 0:
            cmd = 'SWITCH DISTANCE (_{}) > {{({} ? _{})}}'.format(
                self.res1,
                self.res2,
                self.res3,
            )
        elif self.res4 == 0:
            cmd = 'SWITCH DISTANCE (_{}) > {{({} ? _{}), ({} ? _{})}}'.format(
                self.res1,
                self.res2,
                self.res3,
                self.res4,
                self.res5,
            )
        elif self.res6 == 0:
            cmd = 'SWITCH DISTANCE (_{}) > {{({} ? _{}), ({} ? _{}), ({} ? _{})}}'.format(
                self.res1,
                self.res2,
                self.res3,
                self.res4,
                self.res5,
                self.res6,
                self.res7,
            )
        elif self.res8 == 0:
            cmd = 'SWITCH DISTANCE (_{}) > {{({} ? _{}), ({} ? _{}), ({} ? _{}), ({} ? _{})}}'.format(
                self.res1,
                self.res2,
                self.res3,
                self.res4,
                self.res5,
                self.res6,
                self.res7,
                self.res8,
                self.res9
            )
        return cmd

class PMP:
    def __init__(self, val1, val2, pmp_name):
        self.val1 = val1
        self.val2 = val2
        self.pmp_name = pmp_name
        self.flav = 3

    def output_text(self):
        cmd = 'PMAP _{}, {}, "{}")'.format(
            self.val1,
            self.val2,
            self.pmp_name
        )
        return cmd

def get_flavor(flavor, mode='name'):
    """Return the English name of an ICR2 flavor given a hex string."""

    flavor_names = {
    '00000000':('VERTEX','F00'),
    '01000080':('POLY','F01'),
    '02000080':('POLY [T]','F02'),
    '03000080':('PMP','F03'),
    '04000080':('MATERIAL MIP','F04'),
    '05000080':('FACE','F05'),
    '06000080':('FACE2','F06'),
    '07000080':('BSPF','F07'),
    '08000080':('BSPA','F08'),
    '09000080':('BSP2','F09'),
    '0a000080':('BSPN','F10'),
    '0b000080':('LIST','F11'),
    '0c000080':('DYNO','F12'),
    '0d000080':('SWITCH','F13'),
    '0e000080':('REDEF','F14'),
    '0f000080':('DYNAMIC','F15'),
    '10000080':('SUPEROBJ','F16'),
    '11000080':('DATA2','F17'),
    '12000080':('PMP2','F18')
    }

    if mode=='name':
        if flavor in flavor_names:
            return flavor_names[flavor][0]
        else:
            return False
    else:
        if flavor in flavor_names:
            return flavor_names[flavor][1]
        else:
            return False
