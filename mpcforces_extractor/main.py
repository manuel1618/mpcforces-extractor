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
    model_name = "flange2"
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
    spc_forces_extractor.build_subcase_data()

    SPCCluster.build_spc_cluster()
    SPCCluster.calculate_force_sum()

    for spc_cluster in SPCCluster.id_2_instances.values():
        print(spc_cluster.id, len(spc_cluster.spcs))
        print(spc_cluster.spcs[0])
        print(spc_cluster.subcase_id2summed_force)

    # building partid2forces for each mpc
    for subcase in Subcase.subcases:
        for _, mpcs in MPC.config_2_id_2_instance.items():
            for mpc in mpcs.values():
                mpc.get_part_id2force(subcase)

    # Axial / Radial Forces
    for mpc in MPC.all_instances:
        mpc.get_part_id2axial_radial_forces(Subcase.subcases[0])
        _, _, max_radial_force, _, _, max_axial_force = (
            mpc.get_max_axial_and_radial_force()
        )

        shear_stress = mpc.get_stress(max_radial_force)
        axial_stress = mpc.get_stress(max_axial_force)

        print(
            f"MPC: {mpc.element_id} - Max Radial Force: {round(max_radial_force,2)},\
                  Area: {round(mpc.area,2)}, Shear Stress: {round(shear_stress,2)},\
                    Max Axial Force: {round(max_axial_force,2)}, Axial Stress: {round(axial_stress,2)}"
        )


if __name__ == "__main__":
    main()
