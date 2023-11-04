import multiprocessing
import threading


class Node:

    def __init__(self, id):
        self.id = id
        self.node_list = list(i for i in range(4))

    def broadcast(self, message_queues, msg):
        for q_id, queue in enumerate(message_queues):
            if q_id != self.id:
                queue.put(msg+"//")

    def send_message_to(self, dst_process_id, message_queues, msg):
        message_queues[dst_process_id].put(msg+"//")

    def reveice_message(self, message_queues):
        msg = message_queues[self.id].get()
        print(msg)

    def demo(self, message_queues):
        self.broadcast(message_queues, "broadcast msg from "+str(self.id))
        if self.id != 1:
            print('+++')
            self.send_message_to(1, message_queues, "recv msg from "+str(self.id))
        print('process'+ str(self.id), message_queues[self.id].get())
        if not message_queues[self.id].empty() and len(message_queues[self.id].get().split('//')) > 3:
            print(message_queues[self.id].get())

# # Function to send messages to other processes
# def send_message(process_id, message_queues, msg):
#     while True:
#         message = message_queues[process_id].get()
#         if message == 'quit':
#             break
#
#         # Send the message to all other processes
#         for q_id, queue in enumerate(message_queues):
#             if q_id != process_id:
#                 queue.put(f"Process {process_id} says: {message}")
#
# # Function to receive and display messages
# def receive_messages(process_id, message_queues):
#     while True:
#         for q_id, queue in enumerate(message_queues):
#             if q_id != process_id and not queue.empty():
#                 message = queue.get()
#                 print(message)

if __name__ == "__main__":
    num_processes = 2

    # Create a list of message queues, one for each process
    message_queues = [multiprocessing.Queue() for _ in range(num_processes)]

    processes = []
    n0 = Node(0)
    n1 = Node(1)
    n_list = [n0, n1]
    # Create sender and receiver processes for each process
    for i in range(num_processes):

        process = multiprocessing.Process(target=n_list[i].demo, args=(message_queues,))
        processes.append(process)

    # Start all processes
    for process in processes:
        process.start()

    # Wait for all processes to finish
    for process in processes:
        process.join()



