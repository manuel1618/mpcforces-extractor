from mpcforces_extractor.force_extractor import (
    MPCForceExtractor,
    SPCForcesExtractor,
    FEMExtractor,
)
from mpcforces_extractor.datastructure.entities import Node, Element1D, Element
from mpcforces_extractor.datastructure.subcases import Subcase
from mpcforces_extractor.datastructure.rigids import MPC
from mpcforces_extractor.datastructure.loads import SPCCluster


def main():
    """
    This is the main function that is used to test the MPCForceExtractor class
    Its there because of a entry point in the toml file
    """

    input_folder = "data/input"
    # output_folder = "data/output"
    model_name = "m"
    # model_name = "Flange"
    blocksize = 8

    # Clear all Instances (important)
    Node.reset()
    Element1D.reset()
    Element.reset_graph()
    Subcase.reset()
    MPC.reset()

    fem_extractor = FEMExtractor(
        input_folder + f"/{model_name}.fem", block_size=blocksize
    )
    fem_extractor.build_fem_data()
    mpc_force_extractor = MPCForceExtractor(input_folder + f"/{model_name}.mpcf")
    mpc_force_extractor.build_subcase_data()
    spc_forces_extractor = SPCForcesExtractor(input_folder + f"/{model_name}.spcf")

    # Debug
    spc_forces_extractor.build_subcase_data()
    for subcase in spc_forces_extractor.subcases:
        print(subcase.subcase_id, subcase.time)
        print(subcase.node_id2spcforces)

    SPCCluster.build_spc_cluster()
    SPCCluster.calculate_force_sum()

    for spc_cluster in SPCCluster.id_2_instances.values():
        print(spc_cluster.id, len(spc_cluster.spcs))
        print(spc_cluster.spcs[0])
        print(spc_cluster.subcase_id2summed_force)


if __name__ == "__main__":
    main()
