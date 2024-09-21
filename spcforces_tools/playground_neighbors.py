from spcforces_tools.reader.modelreaders import FemFileReader
from spcforces_tools.reader.mpcforces_reader import MPCForcesReader
from spcforces_tools.datastructure.entities import Element


def main():
    """ "
    This is the main function that is used to test the MPCForceExtractor class
    Its there because of a entry point in the toml file
    """

    input_folder = "data/input"
    # output_folder = "data/output"

    # mpc_force_extractor = MPCForceExtractor(
    #     input_folder + "/PlateSimpleRBE3.fem",
    #     input_folder + "/PlateSimpleRBE3.mpcf",
    # )

    # mpc_force_extractor = MPCForceExtractor(
    #     input_folder + "/PlateSimpleRigid3DBolt.fem",
    #     input_folder + "/PlateSimpleRigid3DBolt.mpcf",
    # )
    blocksize = 8
    fem_file_path = input_folder + "/PlateSimpleRigid.fem"
    mpc_file_path = input_folder + "/PlateSimpleRigid.mpcf"

    reader = FemFileReader(fem_file_path, blocksize)
    reader.bulid_node2property()
    reader.get_rigid_elements()

    Element.get_neighbors()

    # Dobug the element neighbors -check if the neighbors are correct
    # counter = 0
    # for element in Element.all_elements:
    #     print(f"{counter} of {len(Element.all_elements)}")
    #     counter += 1

    #     neighbors = element.neighbors

    #     real_neigbours = []
    #     for potential_neighbor in Element.all_elements:
    #         if element.id == potential_neighbor.id:
    #             continue

    #         if set(element.nodes).intersection(potential_neighbor.nodes):
    #             real_neigbours.append(potential_neighbor)

    #     if len(set(neighbors).intersection(real_neigbours)) != len(
    #         set(neighbors)
    #     ) and len(neighbors) != len(real_neigbours):
    #         print(
    #             f"Element {element.id} has {len(neighbors)} neighbors but should have {len(real_neigbours)}"
    #         )
    #         print(f"Neighbors: {[neighbor.id for neighbor in neighbors]}")
    #         print(f"Real Neighbors: {[neighbor.id for neighbor in real_neigbours]}")
    #         print()

    for rigid_element in reader.rigid_elements:
        node2forces = MPCForcesReader(mpc_file_path).get_nodes2forces()
        print(rigid_element.sum_forces_by_connected_parts(node2forces))

    # print the element cendroids


if __name__ == "__main__":
    main()
