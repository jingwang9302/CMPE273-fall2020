import zmq
import time
import sys
from itertools import cycle
from consistent_hashing import ConsistentHashing
from hrw import HWR


def create_clients(servers):
    producers = {}
    context = zmq.Context()
    for server in servers:
        print(f"Creating a server connection to {server}...")
        producer_conn = context.socket(zmq.PUSH)
        producer_conn.bind(server)
        producers[server] = producer_conn
    return producers


def generate_data_round_robin(servers):
    print("Starting...")
    producers = create_clients(servers)
    pool = cycle(producers.values())
    for num in range(10):
        data = {'key': f'key-{num}', 'value': f'value-{num}'}
        print(f"Sending data:{data}")
        next(pool).send_json(data)
        time.sleep(1)
    print("Done")


def generate_data_consistent_hashing(servers):
    print("Starting...")
    producers = create_clients(servers)
    hashing_ring = ConsistentHashing(servers)
    for num in range(10):
        data = {'key': f'key-{num}', 'value': f'value-{num}'}
        print(f"Sending data:{data}")
        producers[hashing_ring.get_node(data['key'])[0]].send_json(data)
        time.sleep(1)
    print("Done")


def generate_data_hrw_hashing(servers):
    print("Starting...")
    # TODO
    producers = create_clients(servers)
    hrw_hashing = HWR(servers, seed=31)
    for num in range(10):
        data = {'key': f'key-{num}', 'value': f'value-{num}'}
        print(f"Sending data:{data}")
        producers[hrw_hashing.find_leader_node(num)].send_json(data)
        time.sleep(1)
    print("Done")


if __name__ == "__main__":
    servers = []
    num_server = 1
    if len(sys.argv) > 1:
        num_server = int(sys.argv[1])
        print(f"num_server={num_server}")

    for each_server in range(num_server):
        server_port = "200{}".format(each_server)
        servers.append(f'tcp://127.0.0.1:{server_port}')

    print("Servers:", servers)
    generate_data_round_robin(servers)
    generate_data_consistent_hashing(servers)
    generate_data_hrw_hashing(servers)
