# MPCForces-Extractor

This tool outputs the MPC forces via summing it up per connected part. It is used in combination with Optistruct.

## Motivation

When you have simple rigid elements for modelling bolts, the mpcforces can be written out to either .h3d or .mpcf file among other options. With these options there seems to be no easy way of getting the summed up forces per conneced part for every mpc elmeent. Below you can see an image with the mpc forses printed as a vector plot. In the image there are two connected parts. To manually get the desired force per part you have to go into hyperview, do a table export and sum them up. This also requires you to have sets or to manually select the nodes per part. For a multitude of mpc elements this process is a problem.

![Vector Forces Plot](docs/assets/img_rbe2_forceVector.png)

The desired process is this:

![Vector summed](docs/assets/img_rbe2_forceVectorSummed.png)

This tool is destined to solve this by automating it. The two major problems regarding this:

- Detect the connected parts with in an efficient way
- Read the mpcf File and assign each force to the mpc element (as this is not printed in the mpcf file)

## Overview

![v0 1 7 2-ProcessAndFrontend](https://github.com/user-attachments/assets/c36d6c6f-9d6c-431c-be13-b4dfd9fa7393)

As seen in the picture above, the .fem and .mpcf files are being transformed by the mpcforces-extractor in a .db file.
This can be triggered from the main page and the extracted entities are saved in the .db and  can be seen on the mpc and node page. 

If you have transformed files into a .db file already you can directly load them in on the bottom half of the main page. This way, the tool is not triggered again but just the entities are displayed on the mpc and node pages.

The mpcforces-extractor serves a small webserver with the pages when being called as descriebed in the quickstart section below.

## Quickstart

To use this tool, you can simply use the pip install command like so:

```bash
pip install mpcforces-extractor
```

After installing it, you can access the tool via: ```mpcforces-extractor``` which will launch a small webserver wher you can select input files and start the process:

If you need more documentation, you can access it [here](https://manuel1618.github.io/mpcforces-extractor/)

## Test Files

In order to make testing the tool easier, you can download the following files:

[m.fem](docs/assets/models/m.fem)

[m.mpcf](docs/assets/models/m.mpcf)

[m.spcf](docs/assets/models/m.spcf)

## Questions?

- Write me a e-mail :)
