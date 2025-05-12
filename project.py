from proxmoxer import ProxmoxAPI
from dotenv import load_dotenv
import os
import argparse


def configure_proxmox():
    """
    Configure Proxmox API connection.
    """
    load_dotenv()

    host = os.getenv("HOST")
    user = os.getenv("USER")
    token_name = os.getenv("TOKEN_NAME")
    token_value = os.getenv("TOKEN_VALUE")

    if not all([host, user, token_name, token_value]):
        raise ValueError("Missing required environment variables for Proxmox connection. Set HOST, USER, TOKEN_NAME, and TOKEN_VALUE in .env file.")

    proxmox = ProxmoxAPI(
        host=host,
        user=user,
        token_name=token_name,
        token_value=token_value,
        verify_ssl=False
    )
    return proxmox


def list_nodes(proxmox):
    try:
        nodes = proxmox.nodes.get()
        return [f"Node: {node['node']} - Status: {node['status']}" for node in nodes]
    except Exception as e:
        return [f"Error retrieving nodes: {e}"]


def load_container_ids(file_path):
    try:
        with open(file_path, "r") as f:
            return {line.strip() for line in f if line.strip().isdigit()}
    except Exception as e:
        print(f"Error loading container IDs from {file_path}: {e}")
        return set()


def list_lxc(proxmox, node_name, lxclist_path=None):
    try:
        containers = proxmox.nodes(node_name).lxc.get()
    except Exception as e:
        return [f"Error retrieving LXCs from node '{node_name}': {e}"]

    filtered_containers = []
    if lxclist_path is None:
        for ct in containers:
            lxcid = ct['vmid']
            name = ct.get('name', f'ct{lxcid}')
            status = ct['status']
            filtered_containers.append(f" - {name} (VMID: {lxcid}) - status: {status}")
    else:
        lxclist = load_container_ids(lxclist_path)
        for ct in containers:
            lxcid = ct['vmid']
            name = ct.get('name', f'ct{lxcid}')
            status = ct['status']
            if str(lxcid) in lxclist:
                filtered_containers.append(f" - {name} (VMID: {lxcid}) - status: {status}")
    return filtered_containers


def list_storage(proxmox, node_name):
    try:
        storages = proxmox.nodes(node_name).storage.get()
        return [f" - {storage['storage']} (Type: {storage.get('type', 'unknown')}) - status: {storage.get('status', 'N/A')}" for storage in storages]
    except Exception as e:
        return [f"Error retrieving storage from node '{node_name}': {e}"]


def main():
    parser = argparse.ArgumentParser(description="Proxmox Monitoring Script")
    parser.add_argument('--nodes', action="store_true", help='List all nodes')
    parser.add_argument('--lxc', action="store_true", help='List all LXCs')
    parser.add_argument('--storage', action="store_true", help='List all storage')
    parser.add_argument('--node', type=str, help='Specify a node name')
    parser.add_argument('--lxc-list', action="store_true", help='List data about LXCs in lxc.csv')
    parser.add_argument('--all', action="store_true", help='List nodes, LXCs, and storage info for all nodes')
    args = parser.parse_args()

    if args.all:
        args.nodes = args.lxc = args.storage = True

    try:
        proxmox = configure_proxmox()
    except Exception as e:
        print(f"Failed to connect to Proxmox API: {e}")
        return

    if not any(vars(args).values()):
        print("No arguments provided. Use --help for usage information.")
        return

    if args.nodes:
        print("\n====================")
        print("Nodes in the Proxmox cluster:")
        print("====================")
        for node in list_nodes(proxmox):
            print(node)

    if args.lxc:
        if args.node:
            print(f"\n====================\nLXCs on node {args.node}:\n====================")
            for lxc in list_lxc(proxmox, args.node):
                print(lxc)
        else:
            print("\n====================\nLXCs on all nodes:\n====================")
            try:
                nodes = proxmox.nodes.get()
                for node in nodes:
                    node_name = node['node']
                    print(f"\n-- LXCs on {node_name} --")
                    for lxc in list_lxc(proxmox, node_name):
                        print(lxc)
            except Exception as e:
                print(f"Error retrieving nodes for LXC listing: {e}")

    if args.lxc_list:
        print("\n====================")
        print("Filtered LXC list from lxc.csv:")
        print("====================")
        if args.node:
            print(f"\n-- LXCs on {args.node} --")
            for lxc in list_lxc(proxmox, args.node, lxclist_path="lxc.csv"):
                print(lxc)
        else:
            try:
                nodes = proxmox.nodes.get()
                for node in nodes:
                    node_name = node['node']
                    print(f"\n-- LXCs on {node_name} --")
                    for lxc in list_lxc(proxmox, node_name, lxclist_path="lxc.csv"):
                        print(lxc)
            except Exception as e:
                print(f"Error retrieving nodes for filtered LXC listing: {e}")

    if args.storage:
        if args.node:
            print(f"\n====================\nStorage on node {args.node}:\n====================")
            for storage in list_storage(proxmox, args.node):
                print(storage)
        else:
            print("\n====================\nStorage on all nodes:\n====================")
            try:
                nodes = proxmox.nodes.get()
                for node in nodes:
                    node_name = node['node']
                    print(f"\n-- Storage on {node_name} --")
                    for storage in list_storage(proxmox, node_name):
                        print(storage)
            except Exception as e:
                print(f"Error retrieving nodes for storage listing: {e}")


if __name__ == "__main__":
    main()
