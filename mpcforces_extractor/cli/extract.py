import os
from pathlib import Path
import typer
from mpcforces_extractor.force_extractor import MPCForceExtractor
from mpcforces_extractor.writer.summary_writer import SummaryWriter
from mpcforces_extractor.visualize.tcl_visualize import VisualizerConnectedParts
from mpcforces_extractor.datastructure.entities import Element

extractor_cmd = typer.Typer(name="extract", invoke_without_command=True)


@extractor_cmd.callback()
def extract(
    input_path_fem: str = typer.Argument(..., help="Path to the .fem file (model)"),
    input_path_mpcf: str = typer.Argument(..., help="Path to the .mpcf file"),
    output_path: str = typer.Argument(..., help="Path to the output folder"),
    blocksize: int = typer.Option(8, help="Blocksize for the MPC forces"),
):
    """
    Extracts the mpc forces and also writes the tcl lines for visualization
    """

    # Check if the files exist, if not raise an error
    if not Path(input_path_fem).exists():
        raise FileNotFoundError(f"File {input_path_fem} not found")
    if not Path(input_path_mpcf).exists():
        raise FileNotFoundError(f"File {input_path_mpcf} not found")

    mpc_force_extractor = MPCForceExtractor(
        input_path_fem, input_path_mpcf, output_path
    )

    rigidelement2forces = mpc_force_extractor.get_mpc_forces(blocksize)
    # Write Summary
    rigidelement2forces = mpc_force_extractor.get_mpc_forces(blocksize)
    summary_writer = SummaryWriter(
        mpc_force_extractor, mpc_force_extractor.output_folder
    )
    summary_writer.add_header()
    summary_writer.add_mpc_lines(rigidelement2forces)
    summary_writer.write_lines()
    # Visualization
    part_id2connected_node_ids = Element.get_part_id2node_ids_graph()
    output_vis = os.path.join(output_path, "tcl_visualization")
    visualizer = VisualizerConnectedParts(part_id2connected_node_ids, output_vis)
    visualizer.output_tcl_lines_for_part_vis()
