
import socket
import datetime
import random

HOST = "0.0.0.0"
PORT = 5001

def timestamp():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Sin estado de "conexión", pero podemos llevar métricas opcionales
stats = {
    "messages": 0
}

def parse_message(msg):
    parts = msg.split("|")
    # Posibles formatos:
    # ID|COMANDO ...
    # ID|SEQ=n|COMANDO ...
    info = {"raw_parts": parts, "id": None, "seq": None, "command": None, "args": ""}
    if len(parts) < 2:
        return info
    info["id"] = parts[0]
    idx = 1
    # Chequear si hay SEQ=
    if parts[1].startswith("SEQ="):
        try:
            info["seq"] = int(parts[1][4:])
        except ValueError:
            pass
        idx = 2
    if idx < len(parts):
        # El resto (parts[idx]) puede tener comando y args separados por espacio
        cmd_line = parts[idx]
        sub = cmd_line.split(" ", 1)
        info["command"] = sub[0].upper()
        if len(sub) > 1:
            info["args"] = sub[1]
    return info

def build_response(info, status, payload):
    # Formato: [ACK=n|]STATUS|payload
    prefix = ""
    if info.get("seq") is not None:
        prefix = f"ACK={info['seq']}|"
    return f"{prefix}{status}|{payload}"

def main():
    print(f"[UDP SERVER] Escuchando en {HOST}:{PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((HOST, PORT))
        while True:
            data, addr = s.recvfrom(4096)
            msg = data.decode(errors="replace").strip()
            stats["messages"] += 1
            info = parse_message(msg)
            if not info["id"] or not info["command"]:
                resp = "ERR|Formato invalido"
            else:
                cmd = info["command"]
                if cmd == "TIME":
                    resp = build_response(info, "OK", timestamp())
                elif cmd == "ECHO":
                    resp = build_response(info, "OK", info["args"])
                elif cmd == "STATUS":
                    resp = build_response(info, "OK", f"messages={stats['messages']}")
                else:
                    resp = build_response(info, "ERR", "Comando desconocido")
            # (Opcional) Simular pérdida para demostrar retransmisión:
            # if random.random() < 0.1: continue
            s.sendto(resp.encode(), addr)

if __name__ == "__main__":
    main()
