import sys
from unittest.mock import patch, MagicMock
from project import configure_proxmox, list_nodes, list_lxc, list_storage, load_container_ids, main

@patch.dict("os.environ", {
    "HOST": "fakehost",
    "USER": "root@pam",
    "TOKEN_NAME": "apitoken",
    "TOKEN_VALUE": "secret"
})

@patch("project.ProxmoxAPI")
def test_configure_proxmox(mock_api):
    proxmox = configure_proxmox()
    mock_api.assert_called_once()
    assert proxmox == mock_api.return_value

def test_load_container_ids(tmp_path):
    file = tmp_path / "lxc.csv"
    file.write_text("100\nabc\n101\n\n102\n")
    ids = load_container_ids(str(file))
    assert ids == {"100", "101", "102"}

@patch("project.ProxmoxAPI")
def test_list_nodes(mock_api):
    mock_api.nodes.get.return_value = [
        {"node": "node1", "status": "online"},
        {"node": "node2", "status": "offline"}
    ]
    result = list_nodes(mock_api)
    assert "Node: node1 - Status: online" in result
    assert "Node: node2 - Status: offline" in result

@patch("project.ProxmoxAPI")
def test_list_lxc_no_filter(mock_api):
    mock_api.nodes().lxc.get.return_value = [
        {"vmid": 100, "name": "web", "status": "running"},
        {"vmid": 101, "status": "stopped"}
    ]
    result = list_lxc(mock_api, "node1")
    assert any("web (VMID: 100)" in r for r in result)
    assert any("ct101 (VMID: 101)" in r for r in result)

@patch("project.ProxmoxAPI")
def test_list_storage(mock_api):
    mock_api.nodes().storage.get.return_value = [
        {"storage": "local", "type": "dir", "status": "available"},
        {"storage": "backup", "type": "nfs"}
    ]
    result = list_storage(mock_api, "node1")
    assert "local" in result[0]
    assert "backup" in result[1]

@patch("project.configure_proxmox")
@patch("project.list_nodes")
def test_main_nodes_output(mock_list_nodes, mock_configure_proxmox, capsys):
    mock_list_nodes.return_value = [
        "Node: node1 - Status: online",
        "Node: node2 - Status: offline"
    ]
    mock_configure_proxmox.return_value = MagicMock()

    testargs = ["prog", "--nodes"]
    with patch.object(sys, 'argv', testargs):
        main()

    captured = capsys.readouterr()
    assert "Nodes in the Proxmox cluster:" in captured.out
    assert "Node: node1 - Status: online" in captured.out

@patch("project.configure_proxmox")
@patch("project.list_nodes")
def test_main_nodes_output(mock_list_nodes, mock_configure_proxmox, capsys):
    mock_list_nodes.return_value = [
        "Node: node1 - Status: online",
        "Node: node2 - Status: offline"
    ]
    mock_configure_proxmox.return_value = MagicMock()
    testargs = ["prog", "--nodes"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert "Nodes in the Proxmox cluster:" in captured.out
    assert "Node: node1 - Status: online" in captured.out

@patch("project.configure_proxmox")
@patch("project.list_lxc")
def test_main_lxc_on_node(mock_list_lxc, mock_configure_proxmox, capsys):
    mock_list_lxc.return_value = [" - web (VMID: 100) - status: running"]
    mock_configure_proxmox.return_value = MagicMock()
    testargs = ["prog", "--lxc", "--node", "node1"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert "LXCs on node node1" in captured.out
    assert " - web (VMID: 100) - status: running" in captured.out

@patch("project.configure_proxmox")
@patch("project.list_lxc")
def test_main_lxc_list(mock_list_lxc, mock_configure_proxmox, capsys):
    mock_list_lxc.return_value = [" - web (VMID: 100) - status: running"]
    mock_configure_proxmox.return_value.nodes.get.return_value = [{"node": "node1"}]
    testargs = ["prog", "--lxc-list"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert "Filtered LXC list from lxc.csv:" in captured.out
    assert " - web (VMID: 100) - status: running" in captured.out

@patch("project.configure_proxmox")
@patch("project.list_storage")
def test_main_storage_on_node(mock_list_storage, mock_configure_proxmox, capsys):
    mock_list_storage.return_value = [" - local (Type: dir) - status: available"]
    mock_configure_proxmox.return_value = MagicMock()
    testargs = ["prog", "--storage", "--node", "node1"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert "Storage on node node1:" in captured.out
    assert " - local (Type: dir) - status: available" in captured.out

@patch("project.configure_proxmox")
@patch("project.list_nodes")
@patch("project.list_lxc")
@patch("project.list_storage")
def test_main_all(mock_list_storage, mock_list_lxc, mock_list_nodes, mock_configure_proxmox, capsys):
    mock_list_nodes.return_value = ["Node: node1 - Status: online"]
    mock_list_lxc.return_value = [" - web (VMID: 100) - status: running"]
    mock_list_storage.return_value = [" - local (Type: dir) - status: available"]
    mock_configure_proxmox.return_value.nodes.get.return_value = [{"node": "node1"}]
    testargs = ["prog", "--all"]
    with patch.object(sys, 'argv', testargs):
        main()
    captured = capsys.readouterr()
    assert "Nodes in the Proxmox cluster:" in captured.out
    assert "-- LXCs on node1 --" in captured.out
    assert "-- Storage on node1 --" in captured.out
