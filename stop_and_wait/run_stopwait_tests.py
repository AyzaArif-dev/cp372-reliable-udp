import csv
import os
import re
import shutil
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

RECEIVER_FILE = ROOT / "stop_and_wait" / "receiver_stopwait.py"
SENDER_FILE = ROOT / "stop_and_wait" / "sender_stopwait.py"

TEST_FILES_DIR = ROOT / "tests" / "test_files"
ACTIVE_TEST_FILE = ROOT / "tests" / "test.txt"

OUTPUT_CSV = ROOT / "stopwait_results.csv"

FILE_SIZES = [
    "10KB", "50KB", "100KB", "500KB",
    "1MB", 
]

LOSS_RATES = [0.0, 0.1, 0.2, 0.3]
TRIALS = 5


def update_loss_rate(loss_rate):
    text = RECEIVER_FILE.read_text()

    new_text = re.sub(
        r"LOSS_RATE\s*=\s*[0-9.]+",
        f"LOSS_RATE = {loss_rate}",
        text
    )

    RECEIVER_FILE.write_text(new_text)


def run_trial(loss_rate, file_size, trial):
    src = TEST_FILES_DIR / f"{file_size}.txt"

    if not src.exists():
        raise FileNotFoundError(f"Missing test file: {src}")

    shutil.copy(src, ACTIVE_TEST_FILE)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(ROOT)

    receiver = subprocess.Popen(
        ["python3", str(RECEIVER_FILE)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    time.sleep(0.5)

    start_time = time.time()

    sender = subprocess.run(
        ["python3", str(SENDER_FILE)],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )

    end_time = time.time()

    try:
        receiver_stdout, receiver_stderr = receiver.communicate(timeout=20)
    except subprocess.TimeoutExpired:
        receiver.kill()
        receiver_stdout, receiver_stderr = receiver.communicate()

    transfer_time = end_time - start_time
    file_bytes = ACTIVE_TEST_FILE.stat().st_size
    throughput = file_bytes / transfer_time if transfer_time > 0 else 0

    retransmissions = sender.stdout.count("Timeout")

    status = "PASS" if "File transfer complete" in sender.stdout else "CHECK"

    return {
        "protocol": "Stop-and-Wait",
        "loss_rate": loss_rate,
        "file_size": file_size,
        "trial": trial,
        "file_bytes": file_bytes,
        "transfer_time_seconds": round(transfer_time, 3),
        "throughput_bytes_per_second": round(throughput, 2),
        "retransmissions": retransmissions,
        "status": status,
        "sender_output": sender.stdout.replace("\n", " | "),
        "receiver_output": receiver_stdout.replace("\n", " | ")
    }


def main():
    results = []

    print("Starting Stop-and-Wait automated testing...")
    print("This will run 4 loss rates × 9 file sizes × 5 trials = 180 tests.")
    print("This may take a long time, especially for large files and packet loss.\n")

    for loss_rate in LOSS_RATES:
        print(f"\n========== LOSS RATE {int(loss_rate * 100)}% ==========")

        update_loss_rate(loss_rate)

        for file_size in FILE_SIZES:
            print(f"\n--- File size: {file_size} ---")

            for trial in range(1, TRIALS + 1):
                print(f"Running trial {trial}/5...")

                try:
                    result = run_trial(loss_rate, file_size, trial)
                    results.append(result)

                    print(
                        f"Time={result['transfer_time_seconds']}s, "
                        f"Throughput={result['throughput_bytes_per_second']} B/s, "
                        f"Retransmissions={result['retransmissions']}, "
                        f"Status={result['status']}"
                    )

                except Exception as e:
                    print(f"ERROR on {file_size}, loss={loss_rate}, trial={trial}: {e}")
                    results.append({
                        "protocol": "Stop-and-Wait",
                        "loss_rate": loss_rate,
                        "file_size": file_size,
                        "trial": trial,
                        "file_bytes": "",
                        "transfer_time_seconds": "",
                        "throughput_bytes_per_second": "",
                        "retransmissions": "",
                        "status": "ERROR",
                        "sender_output": "",
                        "receiver_output": str(e)
                    })

    with open(OUTPUT_CSV, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=results[0].keys())
        writer.writeheader()
        writer.writerows(results)

    print(f"\nDONE. Results saved to: {OUTPUT_CSV}")


if __name__ == "__main__":
    main()