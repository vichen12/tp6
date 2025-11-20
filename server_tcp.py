
import socket
import threading
import datetime

HOST = "0.0.0.0"
PORT = 5000

lock = threading.Lock()
connected_users = {}      # socket -> username
connection_counter = 0    # histórico total

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def broadcast_system(msg):
    with lock:
        for s in list(connected_users.keys()):
            try:
                s.sendall(f"SYSTEM {msg}\n".encode())
            except Exception:
                pass

def handle_client(conn, addr):
    global connection_counter
    username = None
    try:
        conn.sendall(b"Welcome. Please LOGIN <user> or continue as anonymous.\n")
        while True:
            data = conn.recv(4096)
            if not data:
                break
            lines = data.decode(errors="replace").splitlines()
            for line in lines:
                if not line.strip():
                    continue
                parts = line.strip().split(" ", 1)
                cmd = parts[0].upper()
                arg = parts[1] if len(parts) > 1 else ""
                if cmd == "LOGIN":
                    if not arg:
                        conn.sendall(b"ERR Missing username\n")
                        continue
                    with lock:
                        username = arg
                        connected_users[conn] = username
                        connection_counter += 1  # count only first LOGIN
                    conn.sendall(f"OK Logged in as {username}\n".encode())
                    broadcast_system(f"{username} se ha conectado.")
                elif cmd == "TIME":
                    conn.sendall(f"OK {timestamp()}\n".encode())
                elif cmd == "COUNT":
                    with lock:
                        conn.sendall(f"OK {connection_counter}\n".encode())
                elif cmd == "USERS":
                    with lock:
                        users = ", ".join(connected_users.values())
                    conn.sendall(f"OK {users or 'none'}\n".encode())
                elif cmd == "ECHO":
                    conn.sendall(f"OK {arg}\n".encode())
                elif cmd == "STATUS":
                    with lock:
                        conn.sendall(f"OK users={len(connected_users)} total_conn={connection_counter}\n".encode())
                elif cmd == "URGENT":
                    # Simulación de servicio "urgente"
                    conn.sendall(f"URGENT-ACK {arg}\n".encode())
                elif cmd == "QUIT":
                    conn.sendall(b"BYE\n")
                    return
                else:
                    conn.sendall(b"ERR Unknown command\n")
    except Exception as e:
        try:
            conn.sendall(f"ERR {e}\n".encode())
        except Exception:
            pass
    finally:
        with lock:
            if conn in connected_users:
                left_user = connected_users.pop(conn)
                broadcast_system(f"{left_user} se ha desconectado.")
        conn.close()

def main():
    print(f"[TCP SERVER] Escuchando en {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((HOST, PORT))
        s.listen(10)
        while True:
            conn, addr = s.accept()
            t = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
            t.start()

if __name__ == "__main__":
    main()
