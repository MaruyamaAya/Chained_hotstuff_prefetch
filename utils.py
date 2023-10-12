from global_variables import Global_Variables

class signature:
    def __init__(self, node_id, type_, node, view_number):
        self.node_id = node_id
        self.type = type_
        self.node = node
        self.view_number = view_number

class combined_signature:
    def __init__(self, sig_list: list[signature]):
        self.type = sig_list[0].type
        self.node = sig_list[0].node
        self.view_number = sig_list[0].view_number
        self.sig = sorted([sig.node_id for sig in sig_list])



class MSG:
    def __init__(self, type_, node, qc, hs_glob: Global_Variables):
        self.type_ = type_
        self.node = node
        self.view_number = hs_glob.current_view_number
        self.justify = qc
        self.partial_signature = []

    def add_signature(self, signature):
        self.partial_signature.append(signature)


class QC:
    def __init__(self, vote_list: list(MSG)):
        self.view_number = vote_list[0].view_number
        self.node = vote_list[0].node
        self.sig = combined_signature(vote_list)

def matching_msg(m:MSG, t, v):
    return m.type_ == t and m.view_number == v

def matching_qc(qc:QC, t, v):
    return qc.view_number == v and qc.node == t

