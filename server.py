#!/usr/bin/env python3
import http.server
import json
import os
import socket
import time
from pathlib import Path

PORT = int(os.environ.get("PORT", 3000))
BASE = Path(__file__).parent
DATA_FILE = BASE / "memories.json"

if not DATA_FILE.exists():
    DATA_FILE.write_text("[]")


def get_memories():
    return json.loads(DATA_FILE.read_text())


def save_memory(text, author):
    memories = get_memories()
    memory = {
        "id": int(time.time() * 1000),
        "text": text.strip()[:300],
        "author": (author or "Anonymous").strip()[:40],
        "createdAt": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }
    memories.append(memory)
    DATA_FILE.write_text(json.dumps(memories, indent=2))
    return memory


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"


class Handler(http.server.BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # suppress default request logs

    def send_file(self, filepath, content_type="text/html"):
        content = Path(filepath).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def send_json(self, data, status=200):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = self.path.split("?")[0]
        if path == "/":
            self.send_file(BASE / "home.html")
        elif path == "/submit":
            self.send_file(BASE / "submit.html")
        elif path in ("/kevin", "/consulting"):
            self.send_file(BASE / "consulting.html")
        elif path == "/karina":
            self.send_file(BASE / "karina.html")
        elif path == "/deborah":
            self.send_file(BASE / "deborah.html")
        elif path == "/wall":
            self.send_file(BASE / "wall.html")
        elif path == "/api/memories":
            self.send_json(get_memories())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/api/memories":
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length)
            try:
                data = json.loads(body)
                text = data.get("text", "").strip()
                if not text:
                    self.send_json({"error": "text required"}, 400)
                    return
                memory = save_memory(text, data.get("author", ""))
                self.send_json(memory, 201)
            except Exception:
                self.send_json({"error": "invalid request"}, 400)
        else:
            self.send_response(404)
            self.end_headers()


if __name__ == "__main__":
    ip = get_local_ip()
    server = http.server.HTTPServer(("0.0.0.0", PORT), Handler)
    print(f"\n🏡 Villagers Memory Wall is running!\n")
    print(f"  Wall (show on big screen): http://{ip}:{PORT}/wall")
    print(f"  Submit (share with group): http://{ip}:{PORT}/\n")
    print("Press Ctrl+C to stop.\n")
    server.serve_forever()
