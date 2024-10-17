import os
import time
from pathlib import Path
import typer
from mpcforces_extractor.visualization.tcl_visualize import VisualizerConnectedParts
from mpcforces_extractor.reader.modelreaders import FemFileReader

visualize_cmd = typer.Typer(name="visualize", invoke_without_command=True)


@visualize_cmd.callback()
def visualize(
    input_path_fem: str = typer.Argument(..., help="Path to the .fem file (model)"),
    output_path: str = typer.Argument(..., help="Path to the output folder"),
    blocksize: int = typer.Option(8, help="Blocksize for the MPC forces"),
):
    """
    Visualizes the connected parts of the model by moving them into separate components
    """

    # Check if the files exist, if not raise an error
    if not Path(input_path_fem).exists():
        raise FileNotFoundError(f"File {input_path_fem} not found")

    # Visualize the connected parts
    start_time = time.time()
    output_vis = os.path.join(output_path, "tcl_visualization")

    # Read the fem file
    reader = FemFileReader(input_path_fem, blocksize)
    reader.create_entities()

    # Visualize
    visualizer = VisualizerConnectedParts(output_vis)
    visualizer.output_tcl_lines_for_part_vis()

    print("TCL visualization lines written to", output_vis)
    print("..took ", round(time.time() - start_time, 2), "seconds")
