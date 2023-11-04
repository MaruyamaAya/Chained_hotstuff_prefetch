from global_variables import Global_Variables

class signature:
    def __init__(self, worker_id, type_, node, view_number):
        self.worker_id = worker_id
        self.type_ = type_
        self.node = node
        self.view_number = view_number

class combined_signature:
    def __init__(self, sig_list):
        if sig_list == [[]]:
            self.type = "FAKE"
            self.node = None
            self.view_number = 0
            self.sig = []
        else:
            self.type = sig_list[0][0].type_
            self.node = sig_list[0][0].node
            self.view_number = sig_list[0][0].view_number
            self.sig = []
            for partial_sig in sig_list:
                for sig_ in partial_sig:
                    self.sig.append(sig_.worker_id)
            self.sig = sorted(self.sig)



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
    def __init__(self, vote_list):
        self.view_number = vote_list[0].view_number
        self.node = vote_list[0].node
        self.node_id = vote_list[0].node.node_id
        self.sig = combined_signature([vote_.partial_signature for vote_ in vote_list])

def matching_msg(m:MSG, t, v):
    return m.type_ == t and m.view_number == v

def matching_qc(qc:QC, t, v):
    return qc.view_number == v and qc.node == t

