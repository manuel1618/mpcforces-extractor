import typer
from pathlib import Path
from mpcforces_extractor.force_extractor import MPCForceExtractor

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
    mpc_force_extractor.write_suammry(rigidelement2forces)
    mpc_force_extractor.write_tcl_vis_lines()
