from utils import MSG, signature, QC
import threading
import time


class Leaf:
    def __init__(self, hs_glob, parent_, cmd, node_id):
        self.hs_glob = hs_glob
        self.parent = parent_
        self.cmd = cmd
        self.children = []
        self.justify = None
        self.node_id = node_id




class Chain_tree:
    def __init__(self, hs_glob):
        self.hs_glob = hs_glob
        self.root = Leaf(hs_glob, None, None, 0)
        self.leaf_dict = {0: self.root}

    def create_leaf(self, parent_, cmd, qc):
        self.hs_glob.highest_node_id += 1
        temp_leaf = Leaf(self.hs_glob, parent_, cmd, self.hs_glob.highest_node_id)
        temp_leaf.justify = qc
        parent_.children.append(temp_leaf)
        self.leaf_dict[temp_leaf.node_id] = temp_leaf
        return temp_leaf

    def update_leaf(self, leaf_, high_qc):
        parent_id = high_qc.node.node_id
        parent_ = self.leaf_dict[parent_id]
        temp_leaf = Leaf(self.hs_glob, parent_, leaf_.cmd, leaf_.node_id)
        temp_leaf.justify = high_qc
        parent_.children.append(temp_leaf)

    def extend_from(self, node1, node2):
        # check is node 2 is an ancestor of node 1
        if node1 == node2:
            return True
        if node1.parent is None:
            return False
        return self.extend_from(node1.parent, node2)

    def travel_tree(self, node, worker_id):
        if node is None:
            return
        print("node id: ", node.node_id, " cmd: ", node.cmd, " parent id: ", node.parent.node_id if node.parent is not None else None, " worker id: ", worker_id)
        for child in node.children:
            self.travel_tree(child, worker_id)





class Worker:
    def __init__(self, worker_id, hs_glob, message_queues, is_b_worker):
        self.worker_id = worker_id
        self.hs_glob = hs_glob
        self.locked_qc = None
        self.generic_qc = None
        self.chain_tree = Chain_tree(hs_glob)
        self.last_view_msg = []
        self.message_queues = message_queues
        self.is_b_node = is_b_worker
        self. prefetch = True

    def vote_msg(self, type_, node, qc):
        temp_msg = MSG(type_, node, qc, hs_glob=self.hs_glob)
        temp_msg.add_signature(self.tsign(type_, node, temp_msg.view_number))
        return temp_msg

    def tsign(self, type_, node, view_number):
        # fake signature function using node id as signature
        return signature(self.worker_id, type_, node, view_number)

    def safe_node(self, node, qc):
        return self.chain_tree.extend_from(node, self.locked_qc.node) or qc.view_number > self.locked_qc.view_number

    def dummy_send(self, msg, target):
        self.message_queues[target].put(msg)

    def dummy_broadcast(self, msg):
        for i in range(len(self.message_queues)):
            self.message_queues[i].put(msg)

    def dummy_recv(self):
        msg = self.message_queues[self.worker_id].get()
        # check if the msg's view is up to date
        while msg.view_number < self.hs_glob.current_view_number:
            msg = self.message_queues[self.worker_id].get()
        return msg

    def dummy_exec(self, cmd):
        print("worker {} executing command: ".format(self.worker_id), cmd)
        if not self.prefetch:
            self.load_from_disk()

    def protocol_process(self):
        if self.hs_glob.current_leader == self.worker_id:
            self.leader_process()
        self.replica_process()

        if self.hs_glob.next_leader == self.worker_id:
            self.next_leader_process()
        print("worker {} finished processing".format(self.worker_id))
        self.chain_tree.travel_tree(self.chain_tree.root, self.worker_id)

    def leader_process(self):
        print("leader {} is processing".format(self.worker_id))
        if self.hs_glob.current_view_number == 0:
            fake_msg = MSG("FAKE",self.chain_tree.root, None, self.hs_glob)
            self.generic_qc = QC([fake_msg])
        else:
            high_qc = max(self.last_view_msg, key=lambda x: x.justify.view_number).justify
            if high_qc.view_number > self.generic_qc.view_number:
                self.generic_qc = high_qc
        cur_proposal = self.chain_tree.create_leaf(self.generic_qc.node, self.hs_glob.get_cmd(), self.generic_qc)
        self.dummy_broadcast(MSG("GENERIC", cur_proposal, None, self.hs_glob))
        print("leader {} broadcasted GENERIC msg".format(self.worker_id))

    def replica_process(self):
        print("replica {} is processing".format(self.worker_id))
        msg = self.dummy_recv() # TODO add matchingmsg
        b_star = msg.node
        high_qc = msg.node.justify
        if self.worker_id != self.hs_glob.current_leader:
            self.chain_tree.update_leaf(b_star, high_qc)
        b2 = self.chain_tree.leaf_dict[b_star.justify.node_id]
        b1 = self.chain_tree.leaf_dict[b2.justify.node_id] if b2.justify is not None else None
        b = self.chain_tree.leaf_dict[b1.justify.node_id] if b1 is not None and b1.justify is not None else None
        if self.hs_glob.current_view_number == 0 or self.safe_node(b_star, b_star.justify): # updated for the first round
            self.dummy_send(self.vote_msg("GENERIC", b_star, None), self.hs_glob.next_leader)
        if b_star.parent == b2:
            self.generic_qc = b_star.justify
        if b_star.parent == b2 and b2.parent == b1:
            self.locked_qc = b2.justify
        if b_star.parent == b2 and b2.parent == b1 and b1.parent == b:
            self.dummy_exec(b_star.cmd)
        print("replica {} finished processing".format(self.worker_id))

    def next_leader_process(self):
        print("next leader {} is processing".format(self.worker_id))
        while self.message_queues[self.worker_id].qsize() < self.hs_glob.num_node - self.hs_glob.num_B_node:
            time.sleep(0.5)
        self.last_view_msg = [self.dummy_recv() for i in range(self.hs_glob.num_node - self.hs_glob.num_B_node)]
        print("last view msg", self.last_view_msg)
        self.generic_qc = QC(self.last_view_msg)
        self.hs_glob.move_to_next_view()
        if self.prefetch:
            t = threading.Thread(target=self.load_from_disk, args=())
            t.start()
        print("next leader {} finished processing".format(self.worker_id))

    def dummy_next_view(self):
        pass

    def view_process(self):
        for i in range(len(self.hs_glob.cmd_list)):
            self.protocol_process()

    def load_from_disk(self):
        time.sleep(self.hs_glob.file_loading_time)


