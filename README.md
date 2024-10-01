# MPCForces-Extractor

This CLI tool outputs the MPC forces via summing it up per connected part. It is used in combination with Optistruct.
Part connection detection can be visulized in Hpypermish through generated TCL Code.

## Motivation

When you have simple rigid elements for modelling bolts, the mpcforces can be written out to either .h3d or .mpcf file among other options. With these options there seems to be no easy way of getting the summed up forces per conneced part for every mpc elmeent. Below you can see an image with the mpc forses printed as a vector plot. In the image there are two connected parts. To manually get the desired force per part you have to go into hyperview, do a table export and sum them up. This also requires you to have sets or to manually select the nodes per part. For a multitude of mpc elements this process is a problem.

![Vector Forces Plot](docs/assets/img_rbe2_forceVector.png)

The desired process is this:

![Vector summed](docs/assets/img_rbe2_forceVectorSummed.png)

This tool is destined to solve this by automating it. The two major problems regarding this:

- Detect the connected parts with in an efficient way
- Read the mpcf File and assign each force to the mpc element (as this is not printed in the mpcf file)

## Quickstart

To use this tool, you can simply use the pip install command like so:

```bash
pip install mpcforces-extractor
```

After installing it, you can access the cli tool via: ```mpcforces-extractor``` which will give you the following output:

![cli-ouput](docs/assets/img_cli_help.png)

If you need more documentation, you can access it [here](https://manuel1618.github.io/mpcforces-extractor/)

## Questions?

- Write me a e-mail :)
