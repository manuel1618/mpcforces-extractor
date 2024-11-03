# CLI

## Usage

![cli-ouput](assets/img_cli_help.png)

### Command: ```mpcforces-extractor extract```

The main command is the ```extract``` command. This command will extract the mpc forces from the mpcf file and will output the summed up forces per connected part. The ouptput will be a text file with the summed up forces per connected part.

Additionally the tcl code needed for visualizing the connected parts in HyperMesh will be generated. The tcl code will be saved in the same directory as the output file in the subfolder tcl-visualization.

The command wants you to provide the path to the .fem model file as well as the path to the .mpcf file. Lastly, the output file path is needed.
The blocksize is optional and is needed for reading the files. The default value is 8 (8 chars per field in line). For long ouptut it is recommended to increase the blocksize to 16 (not tested).

### Command: ```mpcforces-extractor visualize```

The command ```visualize``` visualizes the connected parts in HyperMesh. The command wants you to provide the path to the .fem model file as well as the path to the output directory. The tcl file is the output of the extract command.
Know issue: If a compornent in the hypermesh model is named part1, part2, etc. the tcl script might not work as intended. This is due to the fact that the tcl script is using the part name to create the groups.

## Source Code

::: mpcforces_extractor.cli.extract
    options:
        show_source: true
        heading_level: 2
        show_signature: false
        show_docstring_parameters: false

::: mpcforces_extractor.cli.visualize
    options:
        show_source: true
        heading_level: 2
        show_signature: false
        show_docstring_parameters: false


