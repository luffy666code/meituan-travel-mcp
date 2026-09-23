
from __future__ import annotations
import os, platform, site, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
SP=ROOT/"site-packages"
_HANDLES=[]

def target():
    m=(platform.machine() or "").lower()
    if sys.platform=="win32": return SP/"window-x64"
    if sys.platform.startswith("linux"):
        if m in ("x86_64","amd64"): return SP/"linux_x86_64"
        if m in ("aarch64","arm64"): return SP/"linux_aarch64"
    raise RuntimeError(f"不支持平台: {sys.platform}/{m}")

def add(p):
    s=str(p)
    if p.exists():
        while s in sys.path: sys.path.remove(s)
        sys.path.insert(0,s)

def pywin(t):
    if sys.platform!="win32": return
    for x in ("win32","win32/lib","Pythonwin"): add(t/x)
    for d in (t/"pywin32_system32",t/"win32",t):
        if d.is_dir() and hasattr(os,"add_dll_directory"):
            try: _HANDLES.append(os.add_dll_directory(str(d)))
            except OSError: pass
    import pywintypes, pythoncom  # noqa

def main():
    try:
        t=target()
        if t.is_dir():
            # 离线打包场景：注入随包依赖目录
            site.addsitedir(str(t)); add(t); pywin(t); add(ROOT)
        else:
            # 源码运行场景：依赖由 pip 环境提供，仅确保 src 目录可导入
            add(ROOT)
        from server import main as run
    except Exception as e:
        print(f"[meituan-travel] 启动失败: {e}",file=sys.stderr,flush=True)
        raise SystemExit(2)
    run()

if __name__=="__main__": main()
