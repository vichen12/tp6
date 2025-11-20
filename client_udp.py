
import socket
import sys
import time

SERVER = "127.0.0.1"
PORT = 5001
CLIENT_ID = "c42"
TIMEOUT = 1.0
RETRIES = 3
seq = 0

def send_command(sock, cmd, reliable=False):
    global seq
    if reliable:
        seq += 1
        payload = f"{CLIENT_ID}|SEQ={seq}|{cmd}"
        for attempt in range(RETRIES):
            sock.sendto(payload.encode(), (SERVER, PORT))
            sock.settimeout(TIMEOUT)
            try:
                data, _ = sock.recvfrom(4096)
                resp = data.decode()
                if f"ACK={seq}|" in resp:
                    return resp
            except socket.timeout:
                print(f"[WARN] Timeout seq={seq} intento={attempt+1}")
        return f"ERR|No ACK tras {RETRIES} intentos"
    else:
        payload = f"{CLIENT_ID}|{cmd}"
        sock.sendto(payload.encode(), (SERVER, PORT))
        sock.settimeout(TIMEOUT)
        try:
            data, _ = sock.recvfrom(4096)
            return data.decode()
        except socket.timeout:
            return "ERR|Timeout sin fiabilidad"

def main():
    reliable = "--reliable" in sys.argv
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        print("Comandos: TIME, ECHO <txt>, STATUS, exit")
        while True:
            line = input("> ").strip()
            if line.lower() in ("exit", "quit"):
                break
            if not line:
                continue
            resp = send_command(sock, line, reliable=reliable)
            print(resp)

if __name__ == "__main__":
    main()
