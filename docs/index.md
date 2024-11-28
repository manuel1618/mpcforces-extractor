# Welcome to MPCForces-Extractor

This tool extracts the forces of RBEs from Altair Optistruct Runs. It sums the forces up by part for connected parts of the RBE autoamtically.

## Motivation

When you have simple rigid elements for modelling bolts, the mpcforces can be written out to either .h3d or .mpcf file among other options. With these options there seems to be no easy way of getting the summed up forces per conneced part for every mpc elmeent. Below you can see an image with the mpc forses printed as a vector plot. In the image there are two connected parts. To manually get the desired force per part you have to go into hyperview, do a table export and sum them up. This also requires you to have sets or to manually select the nodes per part. For a multitude of mpc elements this process is a problem.

![Vector Forces Plot](assets/img_rbe2_forceVector.png)

The desired process is this:

![Vector summed](assets/img_rbe2_forceVectorSummed.png)

This tool is destined to solve this by automating it. The two major problems regarding this:

- Detect the connected parts with in an efficient way
- Read the mpcf File and assign each force to the mpc element (as this is not printed in the mpcf file)

## Functionality

This tool comes now as an [App](app.md) with a webserver for using it (recommended).
You also can use the tool directly. Exmaple is provided [here](source_code.md).

## Basic Functionality (Backend)

The tool operates in the following way:

- Detect RBE2 and RBE3 elements in your model
- Do a group segmentation to dotect the connected parts per RBE Element
- Ouput sums of forces per RBE Element and therefore showing you how much force is being transfereed by which RBE Element to which part

where:

- Part: A connected element collection (ignoring all RBE Elements)
- RBE: Rigid Body Element. Currently RBE2 and RBE3 Elements are supported

## Acknowledgements

- Thanks to [Codie](https://github.com/codie3611), because without him my python skills would not be nearly as mediocre as they are ;)
- Thank you dear Wulu Tea for keeping me running at night
