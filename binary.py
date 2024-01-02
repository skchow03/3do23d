def get_int16(input_bytes, offset):
    return int.from_bytes(input_bytes[offset:offset+2],
                          byteorder='little',
                          signed=False)

# def get_int16_2(input_bytes, offset):
#     return int.from_bytes(input_bytes[offset:offset+2],
#                           byteorder='little',
#                           signed=False)

def get_int32(input_bytes, offset):
    return int.from_bytes(input_bytes[offset:offset+4],
                          byteorder='little',
                          signed=True)

def get_int64(input_bytes, offset):
    return int.from_bytes(input_bytes[offset:offset+8],
                          byteorder='little',
                          signed=True)

def get_hex(input_bytes, offset, size=4):
    return input_bytes[offset:offset+size].hex()

def print_hex_lines(bytes, start, length):
    """Use this for debugging. It will return the hex values and int32 values
    where you specify."""
    for i in range(start,start+length,4):
        print ('{} {} {}'.format(i, get_hex(bytes,i), get_int32(bytes,i)))
