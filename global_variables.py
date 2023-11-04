import random


class Global_Variables:
    def __init__(self, num_node, num_B_node, cmd_list, B_node_idlist, leader_list):
        self.current_view_number = 0
        self.current_leader = leader_list[0]
        self.next_leader = leader_list[1]
        self.num_node = num_node
        self.num_B_node = num_B_node
        self.B_node_idlist = B_node_idlist
        self.highest_node_id = 0
        self.cmd_list = cmd_list
        self.leader_list = leader_list
        self.file_loading_time = 5

    def get_cmd(self):
        cur_cmd = self.cmd_list[self.current_view_number]
        return cur_cmd
    def move_to_next_view(self):
        self.current_view_number += 1
        self.current_leader = self.leader_list[self.current_view_number]
        self.next_leader = self.leader_list[self.current_view_number + 1]


