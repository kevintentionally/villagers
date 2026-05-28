const http = require("http");
const fs = require("fs");
const path = require("path");
const os = require("os");

const PORT = 3000;
const DATA_FILE = path.join(__dirname, "memories.json");

if (!fs.existsSync(DATA_FILE)) {
  fs.writeFileSync(DATA_FILE, JSON.stringify([]));
}

function getMemories() {
  return JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
}

function saveMemory(text, author) {
  const memories = getMemories();
  const memory = {
    id: Date.now(),
    text: text.trim().slice(0, 300),
    author: author ? author.trim().slice(0, 40) : "Anonymous",
    createdAt: new Date().toISOString(),
  };
  memories.push(memory);
  fs.writeFileSync(DATA_FILE, JSON.stringify(memories, null, 2));
  return memory;
}

function getLocalIP() {
  const interfaces = os.networkInterfaces();
  for (const name of Object.keys(interfaces)) {
    for (const iface of interfaces[name]) {
      if (iface.family === "IPv4" && !iface.internal) {
        return iface.address;
      }
    }
  }
  return "localhost";
}

const server = http.createServer((req, res) => {
  const url = new URL(req.url, `http://${req.headers.host}`);

  if (req.method === "GET" && url.pathname === "/") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(fs.readFileSync(path.join(__dirname, "submit.html")));
    return;
  }

  if (req.method === "GET" && url.pathname === "/wall") {
    res.writeHead(200, { "Content-Type": "text/html" });
    res.end(fs.readFileSync(path.join(__dirname, "wall.html")));
    return;
  }

  if (req.method === "GET" && url.pathname === "/api/memories") {
    res.writeHead(200, { "Content-Type": "application/json" });
    res.end(JSON.stringify(getMemories()));
    return;
  }

  if (req.method === "POST" && url.pathname === "/api/memories") {
    let body = "";
    req.on("data", (chunk) => (body += chunk));
    req.on("end", () => {
      try {
        const { text, author } = JSON.parse(body);
        if (!text || !text.trim()) {
          res.writeHead(400, { "Content-Type": "application/json" });
          res.end(JSON.stringify({ error: "Memory text is required" }));
          return;
        }
        const memory = saveMemory(text, author);
        res.writeHead(201, { "Content-Type": "application/json" });
        res.end(JSON.stringify(memory));
      } catch {
        res.writeHead(400, { "Content-Type": "application/json" });
        res.end(JSON.stringify({ error: "Invalid JSON" }));
      }
    });
    return;
  }

  res.writeHead(404);
  res.end("Not found");
});

server.listen(PORT, "0.0.0.0", () => {
  const ip = getLocalIP();
  console.log(`\n🏡 Villagers Memory Wall is running!\n`);
  console.log(`  Wall (show on big screen): http://${ip}:${PORT}/wall`);
  console.log(`  Submit (share with group): http://${ip}:${PORT}/\n`);
});
