# App

This is the first version to support a small frontend which is accessible from the browser and documented below.

## Run the Frontend

To start the app, please run the Taskfile (-> [quick-start](quick_start.md)) command

```bash
task app
```

this runs basically:

```python
uvicorn.run(app, host="127.0.0.1", port=8000)
```

So, this starts a uvicorn server at your localhost which has a FastAPI instance (app).

## Pages

The Server gives access to the following pages, which are very briefly documented here:

### Main Page

Allows for:

- Start the tool with custom files. Needed Files:
    - .fem File (Basically your Input Deck for Optistruct)
    - .mpcf File (The forces on the RBE Slave Nodes). Its exported by Optistruct via the loadstep output request - mpcf: Format: Opti
- Alternatively import a database (from a previous run) directly

In both ways, the database will be filled and the following pages can be used.

### MPC Page

- Shows the MPCs and their slave nodes (also separated by part)
- The copy buttons copy the node ids as a comma separated string into the clipboard. This can be then used e.g. in Hypermesh entity selector
- The summed up force per part is displayed

### Nodes Page

Sometimes the summed up force is not enough detail and oyu want to see the force distribution. This page can do this.

In its default way:

- It displays all the nodes and their forces
- With the filter option you can use the node ids from the copy button from the MPC Page to quickly select the nodes you are interested in





