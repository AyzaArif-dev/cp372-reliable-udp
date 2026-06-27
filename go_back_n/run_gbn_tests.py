import csv
import os
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUTPUT_CSV = ROOT / "gbn_results.csv"

FILE_SIZES = {
    "10KB": 10 * 1024,
    "50KB": 50 * 1024,
    "100KB": 100 * 1024,
    "500KB": 500 * 1024,
    "1MB": 1024 * 1024,
}

LOSS_RATES = [0.0, 0.1, 0.2, 0.3]
TRIALS = 5
WINDOW_SIZE = 4


def run_trial(loss_rate, file_size_label, byte_count, trial):
    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    receiver_cmd = [
        "python3", "-m", "go_back_n",
        "receiver", "5001", "5000", str(WINDOW_SIZE),
        "--p", str(loss_rate)
    ]

    sender_cmd = [
        "python3", "-m", "go_back_n",
        "sender", "5000", "5001", str(WINDOW_SIZE)
    ]

    receiver = subprocess.Popen(
        receiver_cmd,
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    time.sleep(0.5)

    payload = "A" * byte_count
    sender_input = f"send {payload}\nexit\n"

    start = time.time()

    sender = subprocess.run(
        sender_cmd,
        input=sender_input,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        cwd=ROOT,
        env=env,
        timeout=300
    )

    end = time.time()

    receiver.kill()
    receiver_stdout, receiver_stderr = receiver.communicate()

    transfer_time = end - start
    throughput = byte_count / transfer_time if transfer_time > 0 else 0

    retransmissions = sender.stdout.count("timeout")

    status = "PASS" if "ACK" in sender.stdout else "CHECK"

    return {
        "protocol": "Go-Back-N",
        "loss_rate": loss_rate,
        "file_size": file_size_label,
        "trial": trial,
        "file_bytes": byte_count,
        "transfer_time_seconds": round(transfer_time, 3),
        "throughput_bytes_per_second": round(throughput, 2),
        "retransmissions": retransmissions,
        "status": status,
    }


def main():
    results = []

    print("Starting Go-Back-N automated testing...")
    print("This will run 4 loss rates × 5 file sizes × 5 trials = 100 tests.")
    print("Using message payloads to simulate file sizes.\n")

    for loss_rate in LOSS_RATES:
        print(f"\n========== LOSS RATE {int(loss_rate * 100)}% ==========")

        for file_size_label, byte_count in FILE_SIZES.items():
            print(f"\n--- File size: {file_size_label} ---")

            for trial in range(1, TRIALS + 1):
                print(f"Running trial {trial}/5...")

                try:
                    result = run_trial(loss_rate, file_size_label, byte_count, trial)
                    results.append(result)

                    print(
                        f"Time={result['transfer_time_seconds']}s, "
                        f"Throughput={result['throughput_bytes_per_second']} B/s, "
                        f"Retransmissions={result['retransmissions']}, "
                        f"Status={result['status']}"
                    )

                except Exception as e:
                    print(f"ERROR on {file_size_label}, loss={loss_rate}, trial={trial}: {e}")
                    results.append({
                        "protocol": "Go-Back-N",
                        "loss_rate": loss_rate,
                        "file_size": file_size_label,
                        "trial": trial,
                        "file_bytes": byte_count,
                        "transfer_time_seconds": "",
                        "throughput_bytes_per_second": "",
                        "retransmissions": "",
                        "status": "ERROR",
                    })

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDONE. Results saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()