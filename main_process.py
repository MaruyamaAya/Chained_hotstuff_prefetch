import multiprocessing as mp

from global_variables import *
from utils import *
from node import *



def main():
    num_node = 4
    B_node_idlist = [3]
    num_b_node = len(B_node_idlist)
    leader_list = [0, 1, 2, 2]
    hs_glob = Global_Variables(num_node, num_b_node, ["cmd1", "cmd2", "cmd3", "cmd4"], B_node_idlist, leader_list)
    # hs_glob.current_leader = leader_list[hs_glob.current_view_number]
    # if hs_glob.current_view_number + 1 < len(leader_list):
    #     hs_glob.next_leader = leader_list[hs_glob.current_view_number + 1]
    # else:
    #     hs_glob.next_leader = -1

    # Create message queue for each worker
    message_queues = [mp.Queue() for i in range(num_node)]

    # Create workers
    workers = [Worker(i, hs_glob, message_queues, i in hs_glob.B_node_idlist) for i in range(num_node)]

    # processes list
    processes = []
    for w in workers:
        process = mp.Process(target=w.view_process, args=())
        processes.append(process)

    # start processes
    for p in processes:
        p.start()

    # join processes
    for p in processes:
        p.join()

if __name__ == "__main__":
    main()