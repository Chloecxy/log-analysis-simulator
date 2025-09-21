import random
from datetime import datetime, timedelta

MONTHS = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
USERNAMES = ["admin", "root", "guest", "user", "ubuntu", "test", "test2"]
IPS = [
    # Local IPs
    "10.45.67.89", "172.20.14.5", "10.8.1.230", "172.31.200.99", "10.255.0.1", "172.19.12.42", "10.3.3.3", "172.16.250.10", "10.10.10.10", "172.29.100.100",

    # Malicious IPs
    "170.205.31.167",  # SQL injection attempt (banned 2025‑06‑04)
    "162.155.113.54",  # SQL injection attempt (banned 2025‑06‑04)
    "17.241.75.208",   # flagged/banned (2025‑06‑04)
    "37.221.66.42",    # SQL injection attempt (2025‑06‑03)
    "104.234.53.52",   # SQL injection attempt (2025‑06‑03)
    "141.98.11.222",   # SQL injection attempt (2025‑06‑03)
    "66.240.205.34",   # most detected threat last 7 days (seen 2025‑06‑03)
    "93.174.95.106",   # socks scan (2025‑06‑02)
    "71.6.146.185",    # IMAP attack (2025‑06‑02)
    "165.232.174.130",  # used in hacking/C&C (flagged by Criminal IP 2025‑04‑18)

    # public IPs
    "8.8.8.8", "1.1.1.1", "203.0.113.5"
]

def generate_single_log():
    # Random time in the last 7 days
    time_now = datetime.now()
    log_time = time_now - timedelta(seconds=random.randint(0, 604800))
    timestamp = log_time.strftime(f"%b %d %H:%M:%S")

    user = random.choice(USERNAMES)
    ip = random.choice(IPS)
    port = random.randint(1024, 65535)
    status = random.choices(["Failed", "Accepted"], weights=[0.8, 0.2])[0]

    if status == "Failed":
        return f"{timestamp} ubuntu sshd[1234]: Failed password for invalid user {user} from {ip} port {port} ssh2"
    else:
        return f"{timestamp} ubuntu sshd[1234]: Accepted password for {user} from {ip} port {port} ssh2"


def generate_log_file(log_file="sample_auth.log", count=1000):
    with open(log_file, 'w') as file:
        for _ in range(count):
            file.write(generate_single_log() + "\n")
    print(f"{count} log entries written in '{log_file}'")

generate_log_file()
