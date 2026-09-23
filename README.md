<p align="center">

# ✈️ Meituan Travel MCP Server

**Travel search for AI agents, powered by Fliggy FlyAI — right inside Claude Desktop, Cursor, and any MCP-compatible client.**

Search hotels, flights, trains, attractions with natural language. No browser tabs. Just ask.

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-%3E%3D18-green)](https://nodejs.org/)
[![MCP](https://img.shields.io/badge/MCP-stdio-purple)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/luffy666code/meituan-travel-mcp)

[Homepage](#-meituan-travel-mcp-server) · [Quick Start](#-quick-start) · [Configuration](#-mcp-client-configuration) · [Tools](#-tools) · [Examples](#-examples)

</p>

---

## 🤔 Why this project?

Planning a trip inside an AI conversation used to mean switching back and forth between your agent and a dozen travel websites — comparing hotels, checking flights, looking up train schedules, and pasting results back by hand.

This MCP server brings **Fliggy FlyAI** — Alibaba's official travel AI search — directly into your agent's toolbox. Ask a question, get an answer, without ever leaving the terminal.

- **Natural language in, structured results out** — describe your trip in plain Chinese or English; the server returns clean, readable results.
- **Direct to official FlyAI, no third-party proxy** — every query calls the official `@fly-ai/flyai-cli` maintained by Alibaba Fliggy.
- **stdio MCP server, cross-platform** — runs on Windows, Linux, and macOS; works with Claude Desktop, Cursor, and any MCP-compatible client.
- **Debuggable by default** — set `MEITUAN_TRAVEL_DEBUG=0` to silence logs, or leave it on to trace every CLI call.

---

## 📋 Requirements

| Dependency | Version | Why |
|---|---|---|
| Python | 3.10+ | Runs the MCP server (`mcp` SDK + `pydantic`) |
| Node.js | ≥ 18 | Executes the FlyAI CLI (`@fly-ai/flyai-cli`) |
| npm | bundled with Node | Installs the FlyAI CLI package |
| FLYAI_API_KEY | — | Your API key from [Fliggy FlyAI Open Platform](https://flyai.open.fliggy.com/console) |

> **Note:** This project is open-source server software. The actual travel search capability depends on the Fliggy FlyAI service and your own API key — the repository does not bundle any credentials.

---

## 🚀 Quick Start

### Step 1 — Install Python dependencies

```bash
pip install -r requirements.txt
```

### Step 2 — Install the FlyAI CLI

> **Important:** The server resolves `node_modules` relative to `src/`, so you **must** run `npm install` inside the `src` directory.

```bash
cd src
npm install @fly-ai/flyai-cli
cd ..
```

This creates `src/node_modules/@fly-ai/flyai-cli/`, which `server.py` locates automatically.

### Step 3 — Set your API key

Get your key from the [Fliggy FlyAI Open Platform console](https://flyai.open.fliggy.com/console) (log in → click avatar → obtain interface key).

**Windows (cmd / PowerShell):**
```cmd
set FLYAI_API_KEY=your_api_key_here
```

**Linux / macOS:**
```bash
export FLYAI_API_KEY=your_api_key_here
```

### Step 4 — Verify the server starts

```bash
python src/__main__.py
```

The server starts in stdio mode and waits for MCP client connections. No output means it's running correctly (debug logs go to stderr and `src/meituan-travel-debug.log` by default).

To disable debug logging:
```bash
# Windows
set MEITUAN_TRAVEL_DEBUG=0
# Linux / macOS
export MEITUAN_TRAVEL_DEBUG=0
```

---

## 🔧 Tools

| Tool | Purpose | Required Params |
|---|---|---|
| `meituan_travel_query` | Travel search with city context — hotels, attractions, flights, trains, and mixed itineraries. Combines `city` + `query` into a single FlyAI request. | `city` (string): Current city or main destination, e.g. `北京`, `上海`, `东京`.<br>`query` (string): Full natural-language travel request, may include dates, budget, transport, hotel, and attraction preferences. |
| `flyai_ai_search` | Direct FlyAI `ai-search` call. Best for complex multi-city trips, open-ended exploration, or when no specific city anchor is needed. | `query` (string): Full natural-language travel request, may include origin, destination, dates, budget, companions, and preferences. |

### Example prompts

- *"北京出发，国庆去成都 5 天，预算 5000，推荐酒店和景点"*
- *"上海到东京的机票，10 月 1 日出发，10 月 7 日返回"*
- *"杭州周末两日游，带老人小孩，不要太累"*
- *"Find me a boutique hotel in Bangkok near the river, under $150/night"*

---

## ⚙️ How It Works

```
┌──────────────┐     stdio      ┌──────────────────────┐
│  MCP Client  │ ◄────────────► │  python src/__main__ │
│ (Claude/Cursor│                │      .py (FastMCP)   │
└──────┬───────┘                └──────────┬───────────┘
       │                                     │
       │  tool call                          │  subprocess
       ▼                                     ▼
┌──────────────┐     node       ┌──────────────────────┐
│  Agent asks  │ ─────────────► │  @fly-ai/flyai-cli   │
│  in natural  │                │   (official Fliggy)   │
│   language   │                └──────────┬───────────┘
└──────────────┘                           │
                                           │  HTTPS
                                           ▼
                                  ┌──────────────────────┐
                                  │  Fliggy FlyAI API    │
                                  │  flyai.open.fliggy.  │
                                  │         com           │
                                  └──────────┬───────────┘
                                             │
                                             ▼  JSON
                                  ┌──────────────────────┐
                                  │  Results rendered to │
                                  │      the agent       │
                                  └──────────────────────┘
```

1. Your MCP client spawns `python src/__main__.py` as a stdio subprocess.
2. `__main__.py` bootstraps the path (offline bundle or source mode) and imports `server.main`.
3. `server.py` creates a `FastMCP("meituan-travel")` instance and registers two tools.
4. When a tool is called, the server resolves the FlyAI CLI entry from `src/node_modules/@fly-ai/flyai-cli`.
5. It spawns `node <cli> ai-search --query "..."` with `FLYAI_API_KEY` in the environment.
6. The CLI returns JSON; the server parses, renders, and sends the result back through MCP.

---

## 🔌 MCP Client Configuration

### Claude Desktop

Edit `claude_desktop_config.json` (on Windows: `%APPDATA%\Claude\claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["C:\\absolute\\path\\to\\meituan-travel-mcp\\src\\__main__.py"],
      "env": {
        "FLYAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

> Replace `C:\\absolute\\path\\to\\meituan-travel-mcp` with the actual full path to this repository on your machine. Use double backslashes in JSON.

### Cursor

Create or edit `.cursor/mcp.json` in your project root:

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["C:\\absolute\\path\\to\\meituan-travel-mcp\\src\\__main__.py"],
      "env": {
        "FLYAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

### Generic MCP Client

Any MCP-compatible client that supports stdio servers can use this configuration:

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["/absolute/path/to/meituan-travel-mcp/src/__main__.py"],
      "env": {
        "FLYAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

**On Linux/macOS**, use forward-slash absolute paths. **On Windows**, use double-backslash escaped paths in JSON.

---

## 📝 Examples

### Asking about hotels

> *"我在杭州，想住西湖附近的精品酒店，预算 800 元以内，两晚"*

The agent calls `meituan_travel_query(city="杭州", query="想住西湖附近的精品酒店，预算 800 元以内，两晚")` and returns hotel recommendations with prices and locations.

### Multi-city itinerary

> *"帮我规划一个成都-重庆-西安的 7 天行程，含交通和住宿建议"*

The agent calls `flyai_ai_search(query="成都-重庆-西安 7 天行程，含交通和住宿建议")` and gets a structured itinerary covering transport options, hotel suggestions, and attraction highlights.

---

## 🐛 Troubleshooting

### `未配置 FLYAI_API_KEY。请在环境变量 FLYAI_API_KEY 中填写飞猪 AI 开放平台 API Key。`

The `FLYAI_API_KEY` environment variable is not set. Follow [Step 3](#step-3--set-your-api-key) above. On Windows, remember that `set` only affects the current terminal session — if you launch your MCP client from a different terminal or GUI, set the variable system-wide or in the client's `env` config.

### `未找到 Node.js；FlyAI CLI 要求 Node.js >= 18。`

Node.js is not in your `PATH`. Install [Node.js ≥ 18](https://nodejs.org/) and ensure `node --version` works in your terminal. If Node is installed but not found, you can set `FLYAI_NODE` to the absolute path of the Node executable:

```cmd
set FLYAI_NODE=C:\Program Files\nodejs\node.exe
```

### `包内缺少 @fly-ai/flyai-cli/package.json`

The FlyAI CLI is not installed, or it was installed in the wrong directory. Make sure you ran `npm install @fly-ai/flyai-cli` **inside the `src/` directory** (see [Step 2](#step-2--install-the-flyai-cli)). The server looks for `src/node_modules/@fly-ai/flyai-cli/` specifically.

### Server exits immediately with `启动失败`

When running from source (not an offline bundle), `__main__.py` no longer requires a `site-packages/<platform>` directory — it falls back to using your system Python environment. If you still see this error, ensure `pip install -r requirements.txt` completed successfully and that `python -c "import mcp"` works.

### Debug logs are too noisy

Set `MEITUAN_TRAVEL_DEBUG=0` to disable debug output to stderr and the log file.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

## 🙏 Acknowledgements

- Built with the official [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk) (`mcp.server.fastmcp.FastMCP`).
- Travel search powered by [Fliggy FlyAI](https://flyai.open.fliggy.com/) and the official [`@fly-ai/flyai-cli`](https://www.npmjs.com/package/@fly-ai/flyai-cli) package.
- README style inspired by [alibaba-flyai/flyai-skill](https://github.com/alibaba-flyai/flyai-skill).
