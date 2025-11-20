import socket
import sys

HOST = "127.0.0.1"
PORT = 5000

def main():
    user = sys.argv[1] if len(sys.argv) > 1 else None
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect((HOST, PORT))
        print(s.recv(4096).decode(), end="")
        if user:
            s.sendall(f"LOGIN {user}\n".encode())
            print(s.recv(4096).decode(), end="")
        try:
            while True:
                line = input("> ")
                if not line:
                    continue
                s.sendall((line.strip() + "\n").encode())
                resp = s.recv(4096)
                if not resp:
                    print("Conexión cerrada.")
                    break
                print(resp.decode(), end="")
                if line.upper().startswith("QUIT"):
                    break
        except KeyboardInterrupt:
            print("\n[INTERRUPT]")
            s.sendall(b"QUIT\n")

if __name__ == "__main__":
    main()