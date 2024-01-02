from binary import *
from flavors_icr2 import *
from plane import *
import itertools

def print_list(list):
    new_list = [x.decode('ascii').rstrip('\x00') for x in list]
    print (new_list)

def convert_3do23d(filename, output_file=None, tolerance=1, sort_vertices=False, combine_data_with_list=False):

    if not output_file:
        output_file = filename[:len(filename)-4] + '.3d'

    print ('3do file: {}'.format(filename))
    print ('Output .3d file: {}'.format(output_file))
    print ('Plane matching tolerance: {}'.format(tolerance))

    body_dict = {}

    # Read whole file
    with open(filename, 'rb') as f:
        bytes = f.read()

    # Read header
    body_size = get_int32(bytes,0)
    root_offset = get_int32(bytes,4)
    num_mip_files = get_int32(bytes,8)
    num_pmp_files = get_int32(bytes,12)
    num_3do_files = get_int32(bytes,16)
    total_num_files = num_mip_files + num_pmp_files + num_3do_files
    file_list = []

    for i in range(0,total_num_files):
        byte_offset = (i * 8) + 20
        file_list.append(bytes[byte_offset:byte_offset + 8])
    body_offset = 20 + total_num_files * 8
    header_size = 20 + total_num_files * 8

    header = bytes[0:header_size]
    body = bytes[header_size:]

    # Print header info
    print ('Header size {}'.format(header_size))
    print ('Body size per header {} vs per file {}'.format(body_size,
                                                           len(body)))
    print ('Root offset {}'.format(root_offset))

    # Create mip, pmp and 3do file lists
    mip_file_list = file_list[0:num_mip_files]
    pmp_file_list = file_list[num_mip_files:num_mip_files+num_pmp_files]
    obj_file_list = file_list[num_mip_files+num_pmp_files:total_num_files]

    # Create vertex list
    vertices_nomip = set()
    vertices_mip = set()
    flavors = set()
    expected_pointers = set()

    root = [root_offset]

    body_dict = {}
    flavor_pointers = []

    exitloop = False

    print ('Reading body...')

    while True:
        # If root offset has not been checked, check it. This should
        # run only during the first loop.
        if root:
            cur_pos = root.pop()
            pos_read_order = []

        # Go through everything in flavors if list is not empty
        elif flavor_pointers:
            cur_pos = flavor_pointers.pop()
            pos_read_order.append(cur_pos)

        # If all the lists are empty, then exit the loop
        else:
            break

        flavor = get_hex(body, cur_pos)
        flavor_type = get_flavor(flavor, mode='type')

        # TO DO: clean up the code below so that the file reading occurs in
        # flavors_icr2.py

        if flavor_type == "F00":            # nil
            body_dict[cur_pos] = Vertex(2,0,0,0,0,0)

        elif flavor_type == "F01":
            color = get_int32(body,cur_pos+4)
            num_verts = get_int32(body,cur_pos+8) + 1
            body_dict[cur_pos] = Poly()
            body_dict[cur_pos].color = color
            for i in range(0,num_verts):
                pointer = get_int32(body, cur_pos + 4*(i+3))
                vertices_nomip.add(pointer)
                body_dict[cur_pos].pointers.append(pointer)
            body_dict[cur_pos].check_unique()

        elif flavor_type == "F02":       #POLY T
            group = get_int32(body,cur_pos+4)
            color = get_int32(body,cur_pos+8)
            num_verts = get_int32(body,cur_pos+12) + 1
            body_dict[cur_pos] = PolyT()
            body_dict[cur_pos].color = color
            body_dict[cur_pos].group = group
            for i in range(0,num_verts):
                pointer = get_int32(body, cur_pos + 4*(i+4))
                vertices_mip.add(pointer)
                body_dict[cur_pos].pointers.append(pointer)
            body_dict[cur_pos].check_unique()

        elif flavor_type == "F03":
            val1 = get_int32(body,cur_pos + 4)
            val2 = get_int32(body,cur_pos + 8)
            pmp_num = get_int32(body,cur_pos + 12)
            body_dict[cur_pos] = PMP(val1, val2, pmp_file_list[pmp_num].decode('ascii')).rstrip('\x00')
            flavor_pointers.append(val1)

        elif flavor_type == "F04":
            mip_number = get_int32(body,cur_pos+4)
            color = get_int32(body,cur_pos+8)
            flavor_offset = get_int32(body,cur_pos+12)
            mip_name = mip_file_list[mip_number].decode('ascii').rstrip('\x00')
            body_dict[cur_pos] = Material(mip_number, mip_name, color, flavor_offset)
            flavor_pointers.append(flavor_offset)

        elif flavor_type == "F05":
            body_dict[cur_pos] = Face(body, cur_pos, 5)
            flavor_pointers.append(body_dict[cur_pos].flavor1)

        elif flavor_type == "F06":
            body_dict[cur_pos] = Face(body, cur_pos, 6)
            flavor_pointers.extend((body_dict[cur_pos].flavor1,
                                    body_dict[cur_pos].flavor2))

        elif flavor_type == "F07":
            body_dict[cur_pos] = BSP(body, cur_pos, 7)
            flavor_pointers.extend(body_dict[cur_pos].get_pointers())

        elif flavor_type == "F08":          # BSPA
            body_dict[cur_pos] = BSP(body, cur_pos, 8)
            flavor_pointers.extend(body_dict[cur_pos].get_pointers())

        elif flavor_type == "F09":
            body_dict[cur_pos] = BSP(body, cur_pos, 9)
            flavor_pointers.extend(body_dict[cur_pos].get_pointers())

        elif flavor_type == "F10":
            body_dict[cur_pos] = BSP(body, cur_pos, 10)
            flavor_pointers.extend(body_dict[cur_pos].get_pointers())

        elif flavor_type == "F11":                # List
            num_list_obj = get_int32(body,cur_pos+4)
            body_dict[cur_pos] = List()
            for i in range(0,num_list_obj):
                list_pointer = get_int32(body, cur_pos + 4*(i+2))
                body_dict[cur_pos].pointers.append(list_pointer)
                flavor_pointers.append(list_pointer)

            # If we have a LIST towards the end of a track file, it may be followed
            # by an F17 not referenced by anywhere else in 3D file but the game
            # may read it anyway
            
            cur_pos = cur_pos + 8 + (4 * num_list_obj)
            flavor = get_hex(body, cur_pos)
            flavor_type = get_flavor(flavor, mode='type')
            if flavor_type == "F17" and cur_pos not in body_dict:
#                print ('Unreferenced Flavor 17 identified in offset {}'.format(cur_pos))
                sw1 = get_int32(body,cur_pos+4)
                sw2 = get_int32(body,cur_pos+8)
                sw3 = get_int32(body,cur_pos+12)
                sw4 = get_int32(body,cur_pos+16)
                body_dict[cur_pos] = Data(sw1, sw2, sw3, sw4)

        elif flavor_type == "F12":
            start_dlong = get_int32(body,cur_pos+4)
            end_dlong = get_int32(body,cur_pos+8)
            dlat1 = get_int32(body,cur_pos+12)
            dlat2 = get_int32(body,cur_pos+16)
            body_dict[cur_pos] = Dyno(start_dlong, end_dlong,dlat1,dlat2)

        elif flavor_type == "F13":
            res1 = get_int32(body,cur_pos + 4)
            res2 = get_int32(body,cur_pos + 8)
            res3 = get_int32(body,cur_pos + 12)
            res4 = get_int32(body,cur_pos + 16)
            res5 = get_int32(body,cur_pos + 20)
            res6 = get_int32(body,cur_pos + 24)
            res7 = get_int32(body,cur_pos + 28)
            res8 = get_int32(body,cur_pos + 32)
            res9 = get_int32(body,cur_pos + 36)
            body_dict[cur_pos] = SwitchDistance(res1, res2, res3, res4, res5, res6, res7, res8, res9)

            
            if res2 == 0:
                flavor_pointers.extend((res3))
            elif res4 == 0:
                flavor_pointers.extend((res3, res5))
            elif res6 == 0:
                flavor_pointers.extend((res3, res5, res7))
            elif res8 == 0:
                flavor_pointers.extend((res3, res5, res7, res9))

        elif flavor_type == "F14":
            num_recs = get_int32(body,cur_pos+4)
            body_dict[cur_pos] = Recolor()
            for i in range(0,num_recs):
                record_num = get_int32(body,cur_pos + 8 + (i*8))
                color = get_int32(body,cur_pos + 12 + (i*8))
                body_dict[cur_pos].redef.append((record_num,color))

        elif flavor_type == "F15":                  # Dynamic
            x = get_int32(body,cur_pos+4)
            y = get_int32(body,cur_pos+8)
            z = get_int32(body,cur_pos+12)
            z_rot = get_int32(body,cur_pos+16)
            y_rot = get_int32(body,cur_pos+20)
            x_rot = get_int32(body,cur_pos+24)
            obj_num = -get_int32(body,cur_pos+28)
            obj_name = obj_file_list[obj_num-1].decode('ascii').rstrip('\x00')
            body_dict[cur_pos] = Dynamic(x, y, z, z_rot, y_rot, x_rot,
                                         obj_name.strip())

        elif flavor_type == "F16":                          # Root data
            prev_flavor = get_int32(body,cur_pos+4)
            num_data_obj = get_int32(body,cur_pos+8)
            body_dict[cur_pos] = Superobj()
            body_dict[cur_pos].prev_flavor = prev_flavor
            for i in range(0,num_data_obj):
                pointer = get_int32(body, cur_pos + 4*(i+3))
                body_dict[cur_pos].pointers.append(pointer)
                flavor_pointers.append(pointer)
            flavor_pointers.append(prev_flavor)

        else:
            print (f'Pointer to {cur_pos} not found. Flavor {flavor} type is {flavor_type}. Last pointers were {pos_read_order[-3:]}')

    # Identify vertices in nomip that is already in mip
    print ('Identifying vertices')
    to_remove = []
    for pointer in vertices_nomip:
        if pointer in vertices_mip:
            to_remove.append(pointer)
    for pointer in to_remove:
        vertices_nomip.remove(pointer)

    vertex_set = set()

    # Get Vertices
    for pointer in vertices_nomip:
        x = get_int32(body,pointer+4)
        y = get_int32(body,pointer+8)
        z = get_int32(body,pointer+12)
        body_dict[pointer] = Vertex(0,x,y,z,0,0)
        vertex_set.add((x,y,z))

    for pointer in vertices_mip:
        x = get_int32(body,pointer+4)
        y = get_int32(body,pointer+8)
        z = get_int32(body,pointer+12)
        mip_x = get_int16(body,pointer+16)
        mip_y = get_int16(body,pointer+18)
        body_dict[pointer] = Vertex(1,x,y,z,mip_x,mip_y)
        vertex_set.add((x,y,z))


    print ('Number of commands in body: {}'.format(len(body_dict)))
    print ('Vertices in set: {}'.format(len(vertex_set)))


    # Create dictionary of POLYs and their 4-value planes based on the first
    # 3 pointers
    poly_plane_dict = {}
    num_polys = 0

    # Iterate through all POLYs
    for i in body_dict:
        flavor = body_dict[i]

        if flavor.flav == 1 or flavor.flav == 2:
            num_polys += 1
            points = [x for x in range(0, len(flavor.pointers))]
            combos = itertools.permutations(points, 3)
            for combo in combos:
                ptr1 = flavor.pointers[combo[0]]
                ptr2 = flavor.pointers[combo[1]]
                ptr3 = flavor.pointers[combo[2]]
                pt1 = (body_dict[ptr1].x, body_dict[ptr1].y, body_dict[ptr1].z)
                pt2 = (body_dict[ptr2].x, body_dict[ptr2].y, body_dict[ptr2].z)
                pt3 = (body_dict[ptr3].x, body_dict[ptr3].y, body_dict[ptr3].z)
                v1, v2, v3, v4 = get_plane(pt1, pt2, pt3)
                poly_plane_dict[(v1,v2,v3,v4)] = (ptr1,ptr2,ptr3)

    print ('Number of polys = {}'.format(num_polys))
    print ('Number of possible poly planes = {}'.format(len(poly_plane_dict)))

    # For each FACE or BSP function, find 3 points that make a plane that matches the plane equation of those functions:
    print (f'Finding points for planes at tolerance {tolerance}...')
    poly_plane_list = poly_plane_dict.keys()
    total_count = 0
    exact_matches = 0
    approx_matches = 0
    diffs = []
    for i in body_dict:

        if 5 <= body_dict[i].flav <= 10:    # Check for all FACE and BSP functions
            success_flag = False
            total_count += 1

            # Get plane from FACE or BSP function
            v1 = int(body_dict[i].v1)
            v2 = int(body_dict[i].v2)
            v3 = int(body_dict[i].v3)
            v4 = int(body_dict[i].v4)

            #print ('Matching for {} - {} {} {} {}'.format(i, v1,v2,v3,v4))

            # Compare this plane to all the planes in poly_plane_dict
            if (v1,v2,v3,v4) in poly_plane_dict:
                ptr1 = poly_plane_dict[(v1,v2,v3,v4)][0]
                ptr2 = poly_plane_dict[(v1,v2,v3,v4)][1]
                ptr3 = poly_plane_dict[(v1,v2,v3,v4)][2]
                body_dict[i].plane_pointers = (ptr1,ptr2,ptr3)
                exact_matches += 1
                success_flag = True
            else:
                # Compare the plane to planes in list and compute differences
                # TO DO: THIS MATCHES TO THE FIRST MATCH BELOW TOLERANCE AND MAY NOT ACTUALLY BE THE CLOSEST MATCH.
                # LEAVING IT LIKE THIS OTHERWISE FOR TRACKS IT WOULD TAKE A LONG TIME TO COMPUTE ALL POSSIBILITIES
                for plane in poly_plane_list:
                    diff = compare_planes(plane, (v1,v2,v3,v4))         # compare_planes2 is also available but less reliable
                    if diff and diff < tolerance:
                        ptr1 = poly_plane_dict[plane][0]
                        ptr2 = poly_plane_dict[plane][1]
                        ptr3 = poly_plane_dict[plane][2]
                        body_dict[i].plane_pointers = (ptr1,ptr2,ptr3)
                        approx_matches += 1
                        success_flag = True
                        diffs.append(diff)
                        break
            if not success_flag:
                print ('   No plane match for BSP on offset {} ({},{},{},{})'.format(i, v1,v2,v3,v4))


    if diffs:
        print (f'   Plane matching complete with {exact_matches} exact matches and {approx_matches} approximate matches')
        print (f'   Approximate matches have min {min(diffs)} and max {max(diffs)} difference. Average difference is {sum(diffs)/len(diffs)}')
        
    else:
        print ('   No matches')

    #print ('Matching success {} out of {}, or {}%'.format(success, total_count, success/total_count * 100))

    # Transfer group from PolyT to Material
    print ('Transferring GROUP value from POLY [T] to MATERIAL')
    for i in body_dict:
        if body_dict[i].flav == 4:              # If we find MATERIAL
            poly_flavor = body_dict[i].flavor_offset

            if body_dict[poly_flavor].flav == 2:        # If we find POLY [T]
                # If ICR2 group is available, it will use that
                body_dict[i].group = body_dict[poly_flavor].group
            else:
                # Otherwise default to N2 regular group
                print (f'   MATERIAL at offset {i} is not directly linked to a POLY [T]. Manual check needed. Group set to 3 by default.')
                body_dict[i].group = 3

    # Output to file
    pointers = list(body_dict.keys())
    pointers.sort()

    # Combine all DATA with preceding LIST
    if combine_data_with_list:
        for j in range(len(pointers)):
            if body_dict[pointers[j]].flav == 17:
                if body_dict[pointers[j-1]].flav == 11:
                    body_dict[pointers[j-1]].data = body_dict[pointers[j]].output_text()

    # Final sort
    if sort_vertices:
        sorted_pointers = []
        for i in pointers:                  # Put vertices at beginning of file. This may be needed for Papy 3d23do
            if body_dict[i].flav == 0:
                sorted_pointers.append(i)
        for i in pointers:                  # Then flavors
            if combine_data_with_list:
                if body_dict[i].flav > 0 and body_dict[i].flav != 17:
                    sorted_pointers.append(i)
            else:
                if body_dict[i].flav > 0:
                    sorted_pointers.append(i)
    else:
        if combine_data_with_list:
            sorted_pointers = []
            for i in pointers:
                if body_dict[i].flav != 17:
                    sorted_pointers.append(i)
        else:
            sorted_pointers = pointers

    # Show lists
    print ('MIP files: ',end='')
    print_list(mip_file_list)
    print ('3DO files: ',end='')
    print_list(obj_file_list)
    print ('PMP files: ',end='')
    print_list(pmp_file_list)

    with open(output_file, 'w') as o:
        print ('Writing to {}...'.format(output_file), end='')
        o.write('3D VERSION 3.0;\n')
        for i in sorted_pointers:
            o.write('_{}: '.format(i))
            o.write(body_dict[i].output_text() + ';\n')

    print ('done')
