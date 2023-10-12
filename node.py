from utils import MSG, signature



class Leaf:
    def __init__(self, hs_glob, parent_, cmd):
        self.hs_glob = hs_glob
        self.parent = parent_
        self.cmd = cmd
        self.children = []

class Chain_tree:
    def __init__(self, hs_glob):
        self.hs_glob = hs_glob
        self.root = Leaf(hs_glob, None, None)

    def create_leaf(self, parent_, cmd):
        temp_leaf = Leaf(self.hs_glob, parent_, cmd)
        parent_.children.append(temp_leaf)
        return temp_leaf

class Node:
    def __init__(self, node_id, hs_glob):
        self.node_id = node_id
        self.hs_glob = hs_glob

    def vote_msg(self, type_, node, qc):
        temp_msg = MSG(type_, node, qc, hs_glob=self.hs_glob)
        temp_msg.add_signature(self.tsign(type_, node, temp_msg.view_number))
        return temp_msg

    def tsign(self, type_, node, view_number):
        # fake signature function using node id as signature
        return signature(self.node_id, type_, node, view_number)

