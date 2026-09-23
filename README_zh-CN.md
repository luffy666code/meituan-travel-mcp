<p align="center">

# ✈️ 美团旅行 MCP 服务器

**为 AI Agent 打造的旅行搜索能力，基于飞猪 FlyAI —— 直接在 Claude Desktop、Cursor 及任意 MCP 兼容客户端中使用。**

用自然语言搜索酒店、机票、火车、景点。不用开浏览器标签页，直接问就行。

[![Python](https://img.shields.io/badge/python-3.10%2B-blue)](https://www.python.org/)
[![Node](https://img.shields.io/badge/node-%3E%3D18-green)](https://nodejs.org/)
[![MCP](https://img.shields.io/badge/MCP-stdio-purple)](https://modelcontextprotocol.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Version](https://img.shields.io/badge/version-1.0.0-orange)](https://github.com/luffy666code/meituan-travel-mcp)

[首页](#-美团旅行-mcp-服务器) · [快速开始](#-快速开始) · [客户端配置](#-mcp-客户端接入) · [工具列表](#-工具列表) · [使用示例](#-使用示例)

</p>

---

## 🤔 为什么需要这个项目？

过去在 AI 对话里规划行程，意味着要在 Agent 和十几个旅游网站之间反复切换——比酒店、查机票、看火车时刻、再手动把结果粘贴回来。

这个 MCP 服务器把**飞猪 FlyAI**（阿里巴巴官方旅行 AI 搜索）直接带进你的 Agent 工具箱。问一句，得答案，全程不用离开终端。

- **自然语言输入，结构化结果输出** —— 用中文或英文描述你的出行需求，服务器返回清晰可读的结果。
- **直连官方 FlyAI，不经第三方代理** —— 每次查询都调用阿里巴巴飞猪维护的官方 `@fly-ai/flyai-cli`。
- **stdio MCP 服务器，跨平台** —— 支持 Windows、Linux、macOS；兼容 Claude Desktop、Cursor 及任意 MCP 客户端。
- **默认可调试** —— 设置 `MEITUAN_TRAVEL_DEBUG=0` 可关闭日志，保持开启则可追踪每次 CLI 调用。

---

## 📋 环境要求

| 依赖 | 版本 | 说明 |
|---|---|---|
| Python | 3.10+ | 运行 MCP 服务器（`mcp` SDK + `pydantic`） |
| Node.js | ≥ 18 | 执行 FlyAI CLI（`@fly-ai/flyai-cli`） |
| npm | 随 Node 安装 | 安装 FlyAI CLI 包 |
| FLYAI_API_KEY | — | 从 [飞猪 AI 开放平台](https://flyai.open.fliggy.com/console) 获取 |

> **注意：** 本项目开源的是服务器软件本身。实际的旅行搜索能力依赖飞猪 FlyAI 服务和你自己的 API Key——仓库不包含任何凭证。

---

## 🚀 快速开始

### 第一步 —— 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 第二步 —— 安装 FlyAI CLI

> **重要：** 服务器以 `src/` 为基准定位 `node_modules`，因此**必须**在 `src` 目录下执行 `npm install`。

```bash
cd src
npm install @fly-ai/flyai-cli
cd ..
```

这会创建 `src/node_modules/@fly-ai/flyai-cli/`，`server.py` 会自动定位到它。

### 第三步 —— 设置 API Key

从 [飞猪 AI 开放平台控制台](https://flyai.open.fliggy.com/console) 获取密钥（登录后点击头像 → 控制台获取接口密钥）。

**Windows（cmd / PowerShell）：**
```cmd
set FLYAI_API_KEY=你的API密钥
```

**Linux / macOS：**
```bash
export FLYAI_API_KEY=你的API密钥
```

### 第四步 —— 验证服务器启动

```bash
python src/__main__.py
```

服务器以 stdio 模式启动，等待 MCP 客户端连接。没有输出即表示正常运行（调试日志默认输出到 stderr 和 `src/meituan-travel-debug.log`）。

如需关闭调试日志：
```bash
# Windows
set MEITUAN_TRAVEL_DEBUG=0
# Linux / macOS
export MEITUAN_TRAVEL_DEBUG=0
```

---

## 🔧 工具列表

| 工具 | 用途 | 必填参数 |
|---|---|---|
| `meituan_travel_query` | 带城市上下文的旅行搜索——酒店、景点、机票、火车及混合行程规划。将 `city` + `query` 合并为一次 FlyAI 请求。 | `city`（字符串）：当前城市或主要目的地，如 `北京`、`上海`、`东京`。<br>`query`（字符串）：完整的自然语言旅行需求，可包含日期、预算、交通、酒店、景点等约束。 |
| `flyai_ai_search` | 直接调用 FlyAI `ai-search`。适合复杂多城行程、开放式探索，或不需要特定城市锚点的场景。 | `query`（字符串）：完整的自然语言旅行需求，可包含出发地、目的地、日期、预算、同行人和偏好。 |

### 示例提问

- *"北京出发，国庆去成都 5 天，预算 5000，推荐酒店和景点"*
- *"上海到东京的机票，10 月 1 日出发，10 月 7 日返回"*
- *"杭州周末两日游，带老人小孩，不要太累"*
- *"Find me a boutique hotel in Bangkok near the river, under $150/night"*

---

## ⚙️ 工作原理

```
┌──────────────┐     stdio      ┌──────────────────────┐
│  MCP 客户端   │ ◄────────────► │  python src/__main__ │
│(Claude/Cursor)│                │      .py (FastMCP)   │
└──────┬───────┘                └──────────┬───────────┘
       │                                     │
       │  工具调用                            │  子进程
       ▼                                     ▼
┌──────────────┐     node       ┌──────────────────────┐
│  Agent 用自然 │ ─────────────► │  @fly-ai/flyai-cli   │
│   语言提问    │                │   （飞猪官方 CLI）     │
└──────────────┘                └──────────┬───────────┘
                                             │
                                             │  HTTPS
                                             ▼
                                  ┌──────────────────────┐
                                  │  飞猪 FlyAI API      │
                                  │  flyai.open.fliggy.  │
                                  │         com           │
                                  └──────────┬───────────┘
                                             │
                                             ▼  JSON
                                  ┌──────────────────────┐
                                  │  结果渲染后返回给     │
                                  │      Agent           │
                                  └──────────────────────┘
```

1. MCP 客户端以 stdio 子进程方式启动 `python src/__main__.py`。
2. `__main__.py` 完成路径引导（离线包模式或源码模式），导入 `server.main`。
3. `server.py` 创建 `FastMCP("meituan-travel")` 实例并注册两个工具。
4. 工具被调用时，服务器从 `src/node_modules/@fly-ai/flyai-cli` 解析 FlyAI CLI 入口。
5. 以 `FLYAI_API_KEY` 为环境变量，启动 `node <cli> ai-search --query "..."`。
6. CLI 返回 JSON，服务器解析、渲染后通过 MCP 返回结果。

---

## 🔌 MCP 客户端接入

### Claude Desktop

编辑 `claude_desktop_config.json`（Windows 路径：`%APPDATA%\Claude\claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["C:\\absolute\\path\\to\\meituan-travel-mcp\\src\\__main__.py"],
      "env": {
        "FLYAI_API_KEY": "你的API密钥"
      }
    }
  }
}
```

> 将 `C:\\absolute\\path\\to\\meituan-travel-mcp` 替换为你机器上本仓库的实际完整路径。JSON 中使用双反斜杠。

### Cursor

在项目根目录创建或编辑 `.cursor/mcp.json`：

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["C:\\absolute\\path\\to\\meituan-travel-mcp\\src\\__main__.py"],
      "env": {
        "FLYAI_API_KEY": "你的API密钥"
      }
    }
  }
}
```

### 通用 MCP 客户端

任意支持 stdio 服务器的 MCP 兼容客户端均可使用以下配置：

```json
{
  "mcpServers": {
    "meituan-travel": {
      "command": "python",
      "args": ["/absolute/path/to/meituan-travel-mcp/src/__main__.py"],
      "env": {
        "FLYAI_API_KEY": "你的API密钥"
      }
    }
  }
}
```

**Linux/macOS** 使用正斜杠绝对路径；**Windows** 在 JSON 中使用双反斜杠转义路径。

---

## 📝 使用示例

### 查询酒店

> *"我在杭州，想住西湖附近的精品酒店，预算 800 元以内，两晚"*

Agent 调用 `meituan_travel_query(city="杭州", query="想住西湖附近的精品酒店，预算 800 元以内，两晚")`，返回含价格和位置的酒店推荐。

### 多城市行程规划

> *"帮我规划一个成都-重庆-西安的 7 天行程，含交通和住宿建议"*

Agent 调用 `flyai_ai_search(query="成都-重庆-西安 7 天行程，含交通和住宿建议")`，返回涵盖交通方案、酒店建议和景点亮点的结构化行程。

---

## 🐛 常见问题

### `未配置 FLYAI_API_KEY。请在环境变量 FLYAI_API_KEY 中填写飞猪 AI 开放平台 API Key。`

未设置 `FLYAI_API_KEY` 环境变量。请参考上方[第三步](#第三步--设置-api-key)。Windows 下 `set` 仅对当前终端会话生效——如果从其他终端或 GUI 启动 MCP 客户端，请在系统环境变量中设置，或在客户端配置的 `env` 字段中填写。

### `未找到 Node.js；FlyAI CLI 要求 Node.js >= 18。`

`PATH` 中找不到 Node.js。请安装 [Node.js ≥ 18](https://nodejs.org/) 并确认终端中 `node --version` 可用。如果已安装但找不到，可设置 `FLYAI_NODE` 指向 Node 可执行文件的绝对路径：

```cmd
set FLYAI_NODE=C:\Program Files\nodejs\node.exe
```

### `包内缺少 @fly-ai/flyai-cli/package.json`

FlyAI CLI 未安装，或安装目录不对。请确认你是在 **`src/` 目录下**执行的 `npm install @fly-ai/flyai-cli`（见[第二步](#第二步--安装-flyai-cli)）。服务器专门查找 `src/node_modules/@fly-ai/flyai-cli/`。

### 服务器立即退出并显示 `启动失败`

从源码运行时（非离线包），`__main__.py` 不再要求 `site-packages/<platform>` 目录存在——会自动降级使用系统 Python 环境。如果仍报此错误，请确认 `pip install -r requirements.txt` 已成功完成，且 `python -c "import mcp"` 可以正常执行。

### 调试日志太吵

设置 `MEITUAN_TRAVEL_DEBUG=0` 可关闭 stderr 和日志文件的调试输出。

---

## 📄 许可证

本项目基于 [MIT 许可证](LICENSE) 开源。

---

## 🙏 致谢

- 基于官方 [Model Context Protocol Python SDK](https://github.com/modelcontextprotocol/python-sdk)（`mcp.server.fastmcp.FastMCP`）构建。
- 旅行搜索能力由 [飞猪 FlyAI](https://flyai.open.fliggy.com/) 及官方 [`@fly-ai/flyai-cli`](https://www.npmjs.com/package/@fly-ai/flyai-cli) 包提供。
- README 风格参考 [alibaba-flyai/flyai-skill](https://github.com/alibaba-flyai/flyai-skill)。
