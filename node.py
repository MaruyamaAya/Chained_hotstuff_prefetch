from utils import MSG, signature, QC



class Leaf:
    def __init__(self, hs_glob, parent_, cmd):
        self.hs_glob = hs_glob
        self.parent = parent_
        self.cmd = cmd
        self.children = []
        self.justify = None




class Chain_tree:
    def __init__(self, hs_glob):
        self.hs_glob = hs_glob
        self.root = Leaf(hs_glob, None, None)

    def create_leaf(self, parent_, cmd, qc):
        temp_leaf = Leaf(self.hs_glob, parent_, cmd)
        temp_leaf.justify = qc
        parent_.children.append(temp_leaf)
        return temp_leaf

    def extend_from(self, node1, node2):
        # check is node 2 is an ancestor of node 1
        if node1 == node2:
            return True
        if node1.parent is None:
            return False
        return self.extend_from(node1.parent, node2)





class Node:
    def __init__(self, node_id, hs_glob):
        self.node_id = node_id
        self.hs_glob = hs_glob
        self.locked_qc = None
        self.generic_qc = None
        self.chain_tree = Chain_tree(hs_glob)
        self.last_view_msg = []

    def vote_msg(self, type_, node, qc):
        temp_msg = MSG(type_, node, qc, hs_glob=self.hs_glob)
        temp_msg.add_signature(self.tsign(type_, node, temp_msg.view_number))
        return temp_msg

    def tsign(self, type_, node, view_number):
        # fake signature function using node id as signature
        return signature(self.node_id, type_, node, view_number)

    def safe_node(self, node, qc):
        return self.chain_tree.extend_from(node, self.locked_qc.node) or qc.view_number > self.locked_qc.view_number

    def dummy_send(self, msg, target):
        pass

    def dummy_broadcast(self, msg):
        pass

    def dummy_recv(self):
        return MSG("DUMMY", None, None, self.hs_glob)

    def dummy_exec(self, cmd):
        pass

    def protocol_process(self):
        if self.hs_glob.current_leader == self.node_id:
            self.leader_process()
        self.replica_process()
        if self.hs_glob.next_leader == self.node_id:
            self.next_leader_process()

    def leader_process(self):
        high_qc = max(self.last_view_msg, key=lambda x: x.justify.view_number).justify
        if high_qc.view_number > self.generic_qc.view_number:
            self.generic_qc = high_qc
        cur_proposal = self.chain_tree.create_leaf(self.generic_qc.node, self.hs_glob.cur_cmd, self.generic_qc)
        self.dummy_broadcast(MSG("GENERIC", cur_proposal, None, self.hs_glob))

    def replica_process(self):
        msg = self.dummy_recv() # TODO add matchingmsg
        b_star = msg.node
        b2 = b_star.justify.node
        b1 = b2.justify.node
        b = b1.justify.node
        if self.safe_node(b_star, b_star.justify):
            self.dummy_send(self.vote_msg("GENERIC", b_star, None), self.hs_glob.next_leader)
        if b_star.parent == b2:
            self.generic_qc = b_star.justify
        if b_star.parent == b2 and b2.parent == b1:
            self.locked_qc = b2.justify
        if b_star.parent == b2 and b2.parent == b1 and b1.parent == b:
            self.dummy_exec(b_star.cmd)

    def next_leader_process(self):
        self.last_view_msg = self.dummy_recv()
        self.generic_qc = QC(self.last_view_msg)

    def dummy_next_view(self):
        pass