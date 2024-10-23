import os
import time
import uvicorn
from mpcforces_extractor.force_extractor import MPCForceExtractor
from mpcforces_extractor.visualization.tcl_visualize import VisualizerConnectedParts
from mpcforces_extractor.writer.summary_writer import SummaryWriter
from mpcforces_extractor.visualization.api import app


def main():
    """
    This is the main function that is used to test the MPCForceExtractor class
    Its there because of a entry point in the toml file
    """

    input_folder = "data/input"
    output_folder = "data/output"
    model_name = "m"
    model_name = "Flange"
    blocksize = 8

    mpc_force_extractor = MPCForceExtractor(
        input_folder + f"/{model_name}.fem",
        input_folder + f"/{model_name}.mpcf",
        output_folder + f"/{model_name}",
    )

    # Write Summary
    mpc_force_extractor.build_fem_and_subcase_data(blocksize)
    summary_writer = SummaryWriter(
        mpc_force_extractor, mpc_force_extractor.output_folder
    )
    summary_writer.add_header()
    summary_writer.add_mpc_lines()
    summary_writer.write_lines()

    # Visualize the connected parts
    start_time = time.time()
    output_vis = os.path.join(output_folder, model_name, "tcl_visualization")
    visualizer = VisualizerConnectedParts(output_vis)
    visualizer.output_tcl_lines_for_part_vis()

    print("TCL visualization lines written to", output_vis)
    print("..took ", round(time.time() - start_time, 2), "seconds")


if __name__ == "__main__":
    main()
    uvicorn.run(app, host="127.0.0.1", port=8000)
