import _3do_v2_icr2 as c
import argparse

# # EXAMPLES:
# #c.convert_3do23d('elkhart.3do', combine_data_with_list=False, sort_vertices=True)
# #c.convert_3do23d("watglen.3do",'watglen.txt', tolerance=0.5)
# #c.convert_3do23d("lhouse2.3do","lhouse2.3d")
# #c.convert_3do23d('cars.3do','cars.txt', tolerance=1)
# c.convert_3do23d('indycar.3do','indycar.3d', tolerance=10, sort_vertices=True)
# c.convert_3do23d('camaro.3do','camaro.txt', tolerance=3)

def main():
    parser = argparse.ArgumentParser(description="Convert ICR2 3DO files to N3 3D format.")
    parser.add_argument("input_file", help="The path to the ICR2 3DO file to be converted.")
    parser.add_argument("--output_file", help="The path to the output N3 3D file. If not specified, a default name will be used.")
    parser.add_argument("--tolerance", type=float, default=1, help="Tolerance level for conversion. Default is 1.")
    parser.add_argument("--sort_vertices", action="store_true", help="Enable sorting of vertices.")
    parser.add_argument("--combine_data_with_list", action="store_true", help="For tracks, combine DATA with LIST if enabled.")

    args = parser.parse_args()

    # Call the function with the parsed arguments
    c.convert_3do23d(
        filename=args.input_file,
        output_file=args.output_file,
        tolerance=args.tolerance,
        sort_vertices=args.sort_vertices,
        combine_data_with_list=args.combine_data_with_list
    )

if __name__ == "__main__":
    main()