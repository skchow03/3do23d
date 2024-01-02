# 3do23d
Convert ICR2 3DO file to N3 3D text file

Usage:
python 3do23d.py <input 3DO file> --output_file <output 3D file> --tolerance <value> --sort_vertices --combine_data_with_list

input 3DO file - name of the ICR2 .3DO file

Optional:
--output_file <name of the N3 .3D file>
--tolerance <value> - when the program is looking for matching polygons for the BSP function coefficients, it will match polygons that are <value> away from the coefficients in the .3DO file
--sort_vertices - moves all the vertices to the beginning of the output file
--combine_data_with_list - N3 .3D files have the DATA with DLONGs within the LIST lines, while ICR2 .3DO files have DATA as their own separate statement
