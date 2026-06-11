###
### bench_client.py
###

import socket
import time
import statistics
import threading

SERVER_IP = '127.0.0.1'
SERVER_PORT = 5000
NUM_COMMANDS = 1000

def run_m1_sequential(client_id=1, silent=False):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    
    # Consume the welcome message
    buffer = b""
    while b"\n" not in buffer:
        buffer += sock.recv(1024)

    rtts = []
    
    for _ in range(NUM_COMMANDS):
        start_time = time.perf_counter()
        sock.sendall(b"ADD 1 2\n")
        
        # Read until we hit the newline for this specific response
        resp_buffer = b""
        while b"\n" not in resp_buffer:
            resp_buffer += sock.recv(1024)
            
        rtt = (time.perf_counter() - start_time) * 1000 # Convert to milliseconds
        rtts.append(rtt)
        
    sock.sendall(b"QUIT\n")
    sock.close()
    
    mean_rtt = statistics.mean(rtts)
    median_rtt = statistics.median(rtts)
    
    if not silent:
        print(f"--- M1: Sequential RTT (Client {client_id}) ---")
        print(f"Mean RTT:   {mean_rtt:.4f} ms")
        print(f"Median RTT: {median_rtt:.4f} ms")
        
    return mean_rtt

def run_m2_pipelined():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((SERVER_IP, SERVER_PORT))
    
    # Consume welcome message
    buf = b""
    while b"\n" not in buf:
        buf += sock.recv(1024)

    # Build the massive payload of 1,000 commands
    payload = b"ADD 1 2\n" * NUM_COMMANDS
    
    start_time = time.perf_counter()
    sock.sendall(payload)
    
    # Read from the socket until we have 1,000 newline characters
    response_count = 0
    buffer = ""
    
    while response_count < NUM_COMMANDS:
        data = sock.recv(4096).decode('ascii')
        buffer += data
        response_count += data.count('\n')
        
    elapsed_time = time.perf_counter() - start_time
    ops_per_sec = NUM_COMMANDS / elapsed_time
    
    sock.sendall(b"QUIT\n")
    sock.close()
    
    print(f"\nM2: Pipelined Throughput")
    print(f"Total Elapsed Time: {elapsed_time:.4f} seconds")
    print(f"Throughput: {ops_per_sec:.2f} operations/sec")

def run_m3_concurrent(num_clients):
    print(f"\nM3: Concurrent Clients ({num_clients} instances)")
    threads = []
    results = []

    def worker(client_id):
        mean_rtt = run_m1_sequential(client_id, silent=True)
        results.append(mean_rtt)

    # Spawn threads
    for i in range(num_clients):
        t = threading.Thread(target=worker, args=(i+1,))
        threads.append(t)
        t.start()

    # Wait for all threads to finish
    for t in threads:
        t.join()

    overall_mean = statistics.mean(results)
    print(f"Overall Mean RTT across {num_clients} concurrent clients: {overall_mean:.4f} ms")

if __name__ == "__main__":
    # Run M1 three times to observe variation
    for i in range(3):
        print(f"\n[ M1 Run {i+1} ]")
        run_m1_sequential()
        
    # Run M2
    run_m2_pipelined()
    
    # Run M3 for 5, 10, and 20 clients
    run_m3_concurrent(5)
    run_m3_concurrent(10)
    run_m3_concurrent(20)