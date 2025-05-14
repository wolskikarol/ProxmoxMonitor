# Proxmox Monitoring Script

Video demo: https://youtu.be/btgY9CufjnE

A Python script for monitoring a **Proxmox VE** cluster using its API. It provides information about nodes, LXC containers, and storage devices.

## Features

- Connects to the Proxmox API using an API token.
- Lists all nodes in the cluster.
- Lists all LXC containers on a specified node or across all nodes.
- Filters containers based on IDs listed in a `lxc.csv` file.
- Lists available storage on each node.

## Requirements

- Python 3.6+
- Access to a working Proxmox cluster
- Proxmox API token **with appropriate permissions**
- `.env` file with credentials

## Installation

1. Install required packages:

   ```bash
   pip install -r requirements.txt
   ```

2. Create a `.env` file in the project directory with the following content:

   ```
   HOST=your_proxmox_host_or_ip
   USER=your_user@pam
   TOKEN_NAME=your_token_name
   TOKEN_VALUE=your_token_value
   ```

3. (Optional) Create a `lxc.csv` file with a list of LXC VMIDs (one per line) to enable container filtering.

## Usage

### Available options:

Run the script with the desired options:

```bash
python project.py [options]
```

### Available options:

- `--nodes` – list all nodes in the cluster
- `--lxc` – list LXC containers
- `--storage` – list storage information
- `--node NODE_NAME` – specify the node to query
- `--lxc-list` – only list containers whose IDs are in `lxc.csv`
- `--all` – show all information (nodes, LXC, and storage)

### Examples:

- List all nodes:

  ```bash
  python project.py --nodes
  ```

- List containers on a specific node:

  ```bash
  python project.py --lxc --node pve1
  ```

- List only containers specified in `lxc.csv`:

  ```bash
  python project.py --lxc-list --node pve1
  ```

- Show all information:
  ```bash
  python project.py --all
  ```

## Function Descriptions

| Function                                          | Description                                                                              |
| ------------------------------------------------- | ---------------------------------------------------------------------------------------- |
| `configure_proxmox()`                             | Connects to the Proxmox API using environment variables loaded from `.env`.              |
| `list_nodes(proxmox)`                             | Returns a list of all cluster nodes with their status.                                   |
| `load_container_ids(file_path)`                   | Loads VMIDs of containers from a file (e.g., `lxc.csv`) into a set.                      |
| `list_lxc(proxmox, node_name, lxclist_path=None)` | Returns a list of LXC containers on a given node; optionally filters using `lxc.csv`.    |
| `list_storage(proxmox, node_name)`                | Returns a list of storage devices available on the given node.                           |
| `main()`                                          | Handles command-line arguments, connects to the API, and dispatches actions accordingly. |

## Detailed Function Descriptions

### `configure_proxmox()`

**Purpose:**  
Initializes a connection to the Proxmox API using credentials from the `.env` file.

**Details:**

- Loads environment variables: `HOST`, `USER`, `TOKEN_NAME`, `TOKEN_VALUE`.
- Raises an exception if any required variable is missing.
- Creates and returns a `ProxmoxAPI` object for interacting with the cluster.

**Returns:**  
A `ProxmoxAPI` connection object.

---

### `list_nodes(proxmox)`

**Purpose:**  
Retrieves and returns a list of physical nodes in the cluster with their status.

**Details:**

- Uses `.nodes.get()` from the API.
- Returns a human-readable list with each node’s name and current status.

**Returns:**  
List of strings like: `Node: pve1 - Status: online`.

---

### `load_container_ids(file_path)`

**Purpose:**  
Reads LXC VMIDs from a text file (e.g., `lxc.csv`), assuming one numeric ID per line.

**Details:**

- Opens the file and reads only numeric lines.
- Returns a set of unique VMIDs.

**Returns:**  
A `set[str]` of container VMIDs.

---

### `list_lxc(proxmox, node_name, lxclist_path=None)`

**Purpose:**  
Retrieves LXC containers from the specified node, optionally filtered by IDs listed in a file.

**Details:**

- Calls `.nodes(node_name).lxc.get()` to fetch container data.
- If a `lxclist_path` is given, filters only containers whose VMIDs are listed in the file.
- Formats the name, VMID, and status for each container.

**Returns:**  
List of strings with LXC container details.

---

### `list_storage(proxmox, node_name)`

**Purpose:**  
Fetches storage information available on a specified node.

**Details:**

- Uses `.nodes(node_name).storage.get()` to get storage list.
- Formats name, type, and status of each storage unit.

**Returns:**  
List of storage descriptions as strings.

---

### `main()`

**Purpose:**  
Entry point of the script. Parses CLI arguments and triggers the appropriate logic.

**Details:**

- Uses `argparse` to define and parse command-line options.
- If `--all` is passed, activates all major options.
- Establishes a connection to Proxmox using `configure_proxmox()`.
- Based on the parsed arguments, calls other functions and prints results to the console.

**Returns:**  
None – runs the application logic and prints outputs.

## Testing

The project contains a file named `test_project.py` which can ne used to test individual functions using pytest. Pytest can be downloaded using:

```bash
pip install pytest
```

To run testing use the script below:

```bash
pytest test_project.py
```
