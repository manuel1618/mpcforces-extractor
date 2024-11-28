# Quickstart

## Installation

To install this tool, you can simply use the pip install command like so:

```bash
pip install mpcforces-extractor
```

After installing it, you can access the tool via: ```mpcforces-extractor``` which will start the [app](app.md).

## Test Files

In order to make testing the tool easier, you can download the following files:

[m.fem](assets/models/m.fem)

[m.mpcf](assets/models/m.mpcf)

## Taskfile

The below described approach is for more development oriented people. If you are not interested in this, you can skip this section and use the CLI tool described above.

The project has a Taskfile.yaml for your conveinience. Taskfile is an executeable file which you can download on: [Taskfile](https://taskfile.dev/) and it makes your life easier.

In the Taskfile you have commands available to start the program namely:

```bash
task run
```

which does the following:

```bash
poetry run python -m mpcforces_extractor.main
```

alternatively you can start the tool also with the ```python -m```  command.

If you want to run the program in the APP / Browser mode:

```bash
task app
```

which runs:

```bash
poetry run python -m mpcforces_extractor.app
```

which in turn stats the uvicorn server and let's you run it in your browser.
