# 3do23d

## Description
`3do23d` is a tool to convert ICR2 3DO files into N3 3D text files. For simpler objects, the resulting N3 3D file should be ready to re-convert back to ICR2 format using a tool such as Noorok's 3d23do tool.

## Usage
Run the script from the command line using Python. The basic command structure is:

```
python 3do23d.py <input 3DO file> [options]
```

### Arguments

- `<input 3DO file>`: The name of the ICR2 .3DO file to be converted.

### Options

- `--output_file <output 3D file>`: Specify the name of the output N3 .3D file. If not provided, a default name will be used.
- `--tolerance`: When searching for matching polygons for the BSP function coefficients, this option allows matching polygons that deviate slightly from the coefficients in the .3DO file.
- `--sort_vertices`: Moves all the vertices to the beginning of the output file. This may be required to ensure compatibility with Papyrus 3d23do.
- `--combine_data_with_list`: In N3 .3D files, the DATA with DLONGs is within the LIST lines, whereas in ICR2 .3DO files, DATA is a separate statement. This option makes the file conform to N3 format.

## Example
```
python 3do23d.py example.3do --output_file example.3d --tolerance 1 --sort_vertices --combine_data_with_list
```

This command will convert `example.3do` into `example.3d` with a tolerance of 1, sorted vertices, and DATA statement within the LIST statements.
```
