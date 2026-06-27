Project Overview:

This project implements and evaluates two reliable application-layer transport 
protocols: Stop-and-Wait and Go-Back-N that operate on top of  
unreliable UDP sockets in Python. 

Project Structure

## Project Structure

```text
cp372-reliable-udp/
├── go_back_n/
│   ├── __init__.py
│   ├── __main__.py
│   ├── create_test_files.py
│   ├── receiver_gbn.py
│   ├── run_gbn_tests.py
│   └── sender_gbn.py
├── shared/
│   ├── __init__.py
│   └── packet.py
├── stop_and_wait/
│   ├── __init__.py
│   ├── receiver_stopwait.py
│   ├── run_stopwait_tests.py
│   └── sender_stopwait.py
├── tests/
│   ├── test_files/
│   └── test.txt
├── .gitignore
├── gbn_results.csv
├── LICENSE
├── README.md
├── received.txt
└── Testing         
```

How to Run the Experiments

1. STOP-AND-WAIT RUNS:
   Open Terminal 1 (Receiver):

   $ python3 -m stop_and_wait.receiver_stopwait
   
   Open Terminal 2 (Sender):

    $ python3 -m stop_and_wait.sender_stopwait tests/test_10k.txt

3. GO-BACK-N RUNS:
   Open Terminal 1 (Receiver):

   $ python3 -m go_back_n.receiver_gbn
   
   Open Terminal 2 (Sender):

    $ python3 -m go_back_n.sender_gbn

Configuring Packet Loss

To change network loss simulation parameters (0%, 10%, 20%, 30%), open the 
respective receiver script (`receiver_stopwait.py` or `receiver_gbn.py`) and 
modify the global variable:
LOSS_RATE = 0.3  # Represents a 30% simulated loss threshold

Known Bugs & Limitation
- The automated benchmarking script for Go-Back-N contains a logging metric error 
  that records 0 retransmissions to the final summary data arrays despite 
  timeouts triggering correctly during manual execution loops.
- GBN evaluations utilize simulated generated string message payloads in memory 
  rather than conducting direct binary system disk writes.
