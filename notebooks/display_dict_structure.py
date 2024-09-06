import json
from anytree import (Node, RenderTree)

def dict_keys_to_tree(data, parent=None):
    if isinstance(data, dict):
        for key, value in data.items():
            node = Node(key, parent=parent)
            dict_keys_to_tree(value, parent=node)
    elif isinstance(data, list):
        for i, item in enumerate(data):
            if i > 0: break # only display the first element of the list.
            list_node = Node('ITEM_0_OF_A_LIST', parent=parent)
            dict_keys_to_tree(item, parent=list_node)


def render_tree(data):           
    root_nodes = []
    for key, value in data.items():
        root_node = Node(key)
        dict_keys_to_tree(value, parent=root_node)
        root_nodes.append(root_node)

    for root_node in root_nodes:
        for pre, _, node in RenderTree(root_node):
            print(f"{pre}{node.name}")