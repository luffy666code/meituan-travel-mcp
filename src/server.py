
from __future__ import annotations
import json, os, shutil, subprocess, sys
from pathlib import Path
from typing import Annotated, Any
from mcp.server.fastmcp import FastMCP
from pydantic import Field

mcp = FastMCP("meituan-travel")
ROOT = Path(__file__).resolve().parent
FLYAI_PACKAGE = ROOT / "node_modules" / "@fly-ai" / "flyai-cli"


def _resolve_cli_entry() -> Path:
    """Resolve npm bin dynamically instead of assuming dist/index.js."""
    pkg = FLYAI_PACKAGE / "package.json"
    if not pkg.is_file():
        raise RuntimeError(f"包内缺少 @fly-ai/flyai-cli/package.json: {pkg}")
    try:
        meta = json.loads(pkg.read_text(encoding="utf-8"))
    except Exception as exc:
        raise RuntimeError(f"无法读取 FlyAI package.json: {exc}") from exc

    bin_value = meta.get("bin")
    rel = None
    if isinstance(bin_value, str):
        rel = bin_value
    elif isinstance(bin_value, dict):
        rel = (
            bin_value.get("flyai")
            or bin_value.get("flyai-cli")
            or bin_value.get("flyai-bundle")
        )
        if not rel and bin_value:
            rel = next(iter(bin_value.values()))

    candidates = []
    if rel:
        candidates.append(FLYAI_PACKAGE / str(rel))
    candidates += [
        FLYAI_PACKAGE / "dist" / "flyai-bundle.cjs",
        FLYAI_PACKAGE / "dist" / "index.js",
        FLYAI_PACKAGE / "index.js",
        FLYAI_PACKAGE / "bin" / "flyai.js",
        FLYAI_PACKAGE / "bin" / "flyai.cjs",
    ]

    seen = set()
    for candidate in candidates:
        candidate = candidate.resolve()
        key = str(candidate)
        if key in seen:
            continue
        seen.add(key)
        if candidate.is_file():
            _debug(f"resolved_cli_entry={str(candidate)!r} package_bin={bin_value!r}")
            return candidate

    raise RuntimeError(
        "已安装 @fly-ai/flyai-cli，但找不到可执行入口。"
        f" package.json bin={bin_value!r}; package={FLYAI_PACKAGE}"
    )
LOG = ROOT/"meituan-travel-debug.log"
DEBUG = os.getenv("MEITUAN_TRAVEL_DEBUG","1").strip().lower() not in {"0","false","no","off"}

def _debug(msg:str):
    if not DEBUG: return
    line=f"[meituan-travel-debug] {msg}"
    try: print(line,file=sys.stderr,flush=True)
    except Exception: pass
    try:
        with LOG.open("a",encoding="utf-8") as f: f.write(line+"\n")
    except Exception: pass

def _node():
    override=os.getenv("FLYAI_NODE","").strip()
    if override:
        if Path(override).is_file(): return override
        raise RuntimeError(f"FLYAI_NODE 不存在: {override}")
    n=shutil.which("node") or shutil.which("node.exe")
    if not n:
        raise RuntimeError("未找到 Node.js；FlyAI CLI 要求 Node.js >= 18。")
    return n

def _key():
    k=os.getenv("FLYAI_API_KEY","").strip()
    if not k:
        raise RuntimeError("未配置 FLYAI_API_KEY。请在环境变量 FLYAI_API_KEY 中填写飞猪 AI 开放平台 API Key。")
    return k

def _run(args:list[str], timeout:int=120)->Any:
    cli = _resolve_cli_entry()
    node=_node(); _key()
    env=os.environ.copy()
    _debug(
        f"exec node={node!r} cli={str(cli)!r} args={args!r} "
        f"FLYAI_API_KEY={'SET' if env.get('FLYAI_API_KEY') else 'EMPTY'}"
    )
    p=subprocess.run([node,str(cli),*args],cwd=str(ROOT),env=env,capture_output=True,
                     text=True,encoding="utf-8",errors="replace",timeout=timeout,shell=False)
    out=(p.stdout or "").strip(); err=(p.stderr or "").strip()
    _debug(f"result returncode={p.returncode} stdout_len={len(out)} stderr_len={len(err)} stderr={err[:500]!r}")
    if p.returncode!=0:
        raise RuntimeError("FlyAI CLI 调用失败: "+(err or out or f"exit {p.returncode}")[:1000])
    if not out:
        raise RuntimeError("FlyAI CLI 未返回结果")
    for c in [out]+list(reversed([x.strip() for x in out.splitlines() if x.strip()])):
        try: return json.loads(c)
        except json.JSONDecodeError: pass
    return {"status":0,"message":"success","data":out}

def _render(x:Any)->str:
    if isinstance(x,dict):
        if x.get("error"):
            e=x["error"]
            if isinstance(e,dict): e=e.get("message") or e.get("msg") or str(e)
            return "查询失败: "+str(e)
        if "status" in x:
            try: ok=int(x["status"])==0
            except Exception: ok=str(x["status"]).lower() in {"ok","success"}
            if not ok: return "查询失败: "+str(x.get("message") or x.get("systemMessage") or x["status"])
        if x.get("ok") is False:
            return "查询失败: "+str(x.get("message") or x.get("msg") or "FlyAI 返回 ok=false")
        data=next((x[k] for k in ("data","result","content","text","answer") if k in x and x[k] not in (None,"",[],{})), x)
    else:
        data=x
    if data in (None,"",[],{}): return "暂无相关结果，建议调整查询条件后重试。"
    body=data.strip() if isinstance(data,str) else json.dumps(data,ensure_ascii=False,indent=2)
    return body+"\n\n数据来源：飞猪 FlyAI"

@mcp.tool(
    title="美团旅行综合查询",
    description="直接调用飞猪官方 FlyAI，不经过第三方作者代理。支持酒店、景点、航班、火车和混合旅行规划。"
)
def meituan_travel_query(
    city: Annotated[str, Field(description="当前城市或主要目的地。类型：string。例如：北京、上海、杭州、东京。")],
    query: Annotated[str, Field(description="完整自然语言旅行需求。类型：string。可包含日期、预算、交通、酒店、景点等约束。")]
)->str:
    city=(city or "").strip()
    query=(query or "").strip()
    if not query: return "查询失败: query 不能为空。"
    q=f"当前城市/主要地点：{city}。旅行需求：{query}" if city and city not in query else query
    _debug(f"tool=meituan_travel_query city={city!r} query={query!r}")
    try: return _render(_run(["ai-search","--query",q]))
    except Exception as e: return "查询失败: "+str(e)

@mcp.tool(
    title="飞猪 AI 综合旅行搜索",
    description="直接调用飞猪官方 FlyAI ai-search，适合酒店、景点、航班、火车和复杂混合旅行需求。"
)
def flyai_ai_search(
    query: Annotated[str, Field(description="完整自然语言旅行需求。类型：string。可包含出发地、目的地、日期、预算、同行人和偏好。")]
)->str:
    query=(query or "").strip()
    if not query: return "查询失败: query 不能为空。"
    try: return _render(_run(["ai-search","--query",query]))
    except Exception as e: return "查询失败: "+str(e)

def main():
    _debug(
        f"startup FLYAI_API_KEY={'SET' if os.getenv('FLYAI_API_KEY') else 'EMPTY'} "
        f"package={str(FLYAI_PACKAGE)!r}"
    )
    mcp.run()

if __name__=="__main__":
    main()
