"""Clawd: desktop companion with Anthropic tool loop and basic MCP stdio support."""
import asyncio, json, os, threading, queue, subprocess, sys, time
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path
try:
    import anthropic
except ImportError:
    anthropic = None
APP=Path.home()/".clawd"; APP.mkdir(exist_ok=True)
CONFIG=APP/"mcp_servers.json"; HISTORY=APP/"tasks.json"
MODEL=os.getenv("ANTHROPIC_MODEL","claude-sonnet-4-5"); API_KEY=os.getenv("ANTHROPIC_API_KEY","")
DEFAULT_CONFIG={"servers":[]}
class MCPServer:
    """Experimental JSON-RPC MCP stdio client."""
    def __init__(self,name,cfg): self.name,self.cfg,self.proc,self.tools=name,cfg,None,[]
    async def start(self):
        if not self.cfg.get("command"): raise ValueError(f"{self.name}: command missing")
        self.proc=await asyncio.create_subprocess_exec(self.cfg["command"],*(self.cfg.get("args",[])),stdin=asyncio.subprocess.PIPE,stdout=asyncio.subprocess.PIPE,stderr=None,env={**os.environ,**self.cfg.get("env",{})})
        await self.rpc("initialize",{"protocolVersion":"2024-11-05","capabilities":{},"clientInfo":{"name":"Clawd","version":"0.2.0"}})
        await self.rpc("notifications/initialized",{},notify=True)
        self.tools=(await self.rpc("tools/list",{})).get("tools",[])
    async def rpc(self,method,params,notify=False):
        if not self.proc: raise RuntimeError("MCP process not running")
        payload={"jsonrpc":"2.0","method":method,"params":params}
        if notify:
            self.proc.stdin.write((json.dumps(payload)+"\\n").encode()); await self.proc.stdin.drain(); return
        payload["id"]=1; self.proc.stdin.write((json.dumps(payload)+"\\n").encode()); await self.proc.stdin.drain()
        while True:
            line=await asyncio.wait_for(self.proc.stdout.readline(),timeout=90)
            if not line: raise RuntimeError(f"MCP {self.name} exited")
            msg=json.loads(line)
            if msg.get("id")==1:
                if "error" in msg: raise RuntimeError(str(msg["error"]))
                return msg.get("result",{})
    async def stop(self):
        if self.proc:
            self.proc.terminate()
            try: await asyncio.wait_for(self.proc.wait(),3)
            except asyncio.TimeoutError: self.proc.kill()
class App:
    def __init__(self,root):
        self.root=root; root.title("Clawd · your AI companion"); root.geometry("520x650"); root.minsize(480,600); root.configure(bg="#201927")
        self.busy=False; self.events=queue.Queue(); self.history=self.load_history(); self.ui(); self.poll()
    def ui(self):
        top=tk.Frame(self.root,bg="#201927"); top.pack(fill="x",padx=18,pady=12)
        tk.Label(top,text="✿",font=("Segoe UI Emoji",42),bg="#201927",fg="#ffb879").pack(side="left",padx=(4,18))
        tk.Label(top,text="Clawd",font=("Segoe UI",22,"bold"),bg="#201927",fg="#ffe5ce").pack(side="left")
        tk.Label(top,text="MCP DESKTOP COMPANION",font=("Segoe UI",8),bg="#201927",fg="#a99bb7").pack(side="left",padx=12,pady=15)
        self.bubble=tk.Label(self.root,text="Hej! Co dziś robimy?",font=("Segoe UI",12),wraplength=440,justify="left",bg="#382b45",fg="#f6edf9",padx=18,pady=15); self.bubble.pack(fill="x",padx=18,pady=(4,14))
        usage=tk.Frame(self.root,bg="#30263b",highlightthickness=1,highlightbackground="#4a3b56"); usage.pack(fill="x",padx=18)
        tk.Label(usage,text="LIMITY CLAUDE",font=("Segoe UI",9,"bold"),bg="#30263b",fg="#d8c9e5").pack(anchor="w",padx=12,pady=(10,2))
        tk.Label(usage,text="5h: niepołączony   ·   weekly: niepołączony",font=("Segoe UI",10),bg="#30263b",fg="#bcaec9").pack(anchor="w",padx=12,pady=(0,10))
        tk.Label(self.root,text="ZADANIE",font=("Segoe UI",9,"bold"),bg="#201927",fg="#bcaec9").pack(anchor="w",padx=20,pady=(18,5))
        self.input=tk.Text(self.root,height=5,wrap="word",font=("Segoe UI",11),bg="#30263b",fg="white",insertbackground="white",relief="flat",padx=12,pady=10); self.input.pack(fill="x",padx=18); self.input.bind("<Control-Return>",lambda e:self.submit())
        row=tk.Frame(self.root,bg="#201927"); row.pack(fill="x",padx=18,pady=10)
        self.send=tk.Button(row,text="▶ Start task",command=self.submit,bg="#ffb879",fg="#281c30",font=("Segoe UI",10,"bold"),relief="flat",padx=15,pady=8); self.send.pack(side="left")
        ttk.Button(row,text="MCP settings",command=self.settings).pack(side="left",padx=8); ttk.Button(row,text="History",command=self.show_history).pack(side="left")
        tk.Label(self.root,text="TASK LOG",font=("Segoe UI",9,"bold"),bg="#201927",fg="#bcaec9").pack(anchor="w",padx=20,pady=(8,4))
        self.log=tk.Text(self.root,height=8,wrap="word",state="disabled",font=("Consolas",9),bg="#18131f",fg="#c6b9d0",relief="flat",padx=10,pady=8); self.log.pack(fill="both",expand=True,padx=18,pady=(0,14))
        tk.Label(self.root,text="Ctrl+Enter to send · MCP subprocesses run locally · Review server commands carefully",bg="#201927",fg="#897b95",font=("Segoe UI",8)).pack(pady=(0,10))
    def write_log(self,text):
        self.log.config(state="normal"); self.log.insert("end",text+"\\n"); self.log.see("end"); self.log.config(state="disabled")
    def load_history(self):
        try: return json.loads(HISTORY.read_text(encoding="utf-8"))
        except Exception: return []
    def save_history(self,item):
        self.history.insert(0,item); self.history=self.history[:50]; HISTORY.write_text(json.dumps(self.history,indent=2,ensure_ascii=False),encoding="utf-8")
    def submit(self):
        task=self.input.get("1.0","end").strip()
        if not task or self.busy:return
        if not API_KEY: messagebox.showerror("API key missing","Set ANTHROPIC_API_KEY and restart Clawd."); return
        if anthropic is None: messagebox.showerror("Dependency missing","Install requirements first."); return
        self.busy=True; self.send.config(state="disabled",text="Working…"); self.bubble.config(text="Pracuję nad tym… ✨"); self.input.delete("1.0","end"); self.write_log("Started: "+task); threading.Thread(target=self.worker,args=(task,),daemon=True).start()
    def worker(self,task):
        try: self.events.put(("done",asyncio.run(self.agent(task)),task))
        except Exception as e: self.events.put(("error",str(e),task))
    async def agent(self,task):
        client=anthropic.AsyncAnthropic(api_key=API_KEY); servers=[]; toolmap={}; tools=[]
        try:
            cfg=json.loads(CONFIG.read_text(encoding="utf-8")) if CONFIG.exists() else DEFAULT_CONFIG
            for entry in cfg.get("servers",[]):
                if not entry.get("enabled",True):continue
                server=MCPServer(entry.get("name","server"),entry); await server.start(); servers.append(server)
                for t in server.tools:
                    tool_name=f'{server.name}__{t["name"]}'; toolmap[tool_name]=(server,t["name"]); tools.append({"name":tool_name,"description":f'MCP {server.name}: {t.get("description", "")}',"input_schema":t.get("inputSchema",{"type":"object","properties":{}})})
            messages=[{"role":"user","content":task}]; output=[]
            for _ in range(10):
                args={"model":MODEL,"max_tokens":1800,"messages":messages}
                if tools:args["tools"]=tools
                response=await client.messages.create(**args); messages.append({"role":"assistant","content":[b.model_dump() for b in response.content]})
                calls=[b for b in response.content if b.type=="tool_use"]
                for block in response.content:
                    if block.type=="text":output.append(block.text)
                if not calls:break
                results=[]
                for block in calls:
                    srv,name=toolmap[block.name]; self.events.put(("log",f"Tool call: {srv.name}/{name}",task))
                    try: result=await srv.rpc("tools/call",{"name":name,"arguments":block.input})
                    except Exception as err: result={"error":str(err)}
                    results.append({"type":"tool_result","tool_use_id":block.id,"content":json.dumps(result,ensure_ascii=False)[:12000]})
                messages.append({"role":"user","content":results})
            return "\\n\\n".join(output) or "Done."
        finally:
            for server in servers:await server.stop()
    def poll(self):
        try:
            while True:
                kind,text,task=self.events.get_nowait()
                if kind=="log":self.write_log(text);continue
                self.busy=False; self.send.config(state="normal",text="▶ Start task"); self.bubble.config(text=("Finished! ✨\\n" if kind=="done" else "Something went wrong ✦\\n")+text[:1000]); self.write_log(("Completed" if kind=="done" else "Error")+": "+text[:1000]); self.save_history({"task":task,"result":text,"status":kind,"time":time.strftime("%Y-%m-%d %H:%M:%S")})
        except queue.Empty:pass
        self.root.after(150,self.poll)
    def settings(self):
        win=tk.Toplevel(self.root); win.title("MCP config help"); win.geometry("570x300")
        helptext='Config file: ~/.clawd/mcp_servers.json\\nExample format:\\n{ "servers": [{"name":"sample","command":"npx","args":["-y","YOUR-MCP-SERVER"],"env":{},"enabled":true}] }\\n\\nServer commands execute locally. Clawd currently does not ask for per-tool approval. Configure trusted servers only and use limited permissions.'
        tk.Label(win,text=helptext,justify="left",font=("Consolas",10),wraplength=530).pack(anchor="w",padx=14,pady=14)
        if not CONFIG.exists():CONFIG.write_text(json.dumps(DEFAULT_CONFIG,indent=2),encoding="utf-8")
        ttk.Button(win,text="Open config folder",command=self.open_folder).pack(anchor="w",padx=14)
    def open_folder(self):
        if sys.platform=="win32":os.startfile(str(APP))
        elif sys.platform=="darwin":subprocess.Popen(["open",str(APP)])
        else:subprocess.Popen(["xdg-open",str(APP)])
    def show_history(self):
        win=tk.Toplevel(self.root); win.title("Task history"); win.geometry("550x420"); box=tk.Text(win,wrap="word"); box.pack(fill="both",expand=True)
        for item in self.history:box.insert("end",f'{item.get("time")} · {item.get("status")}\\n{item.get("task")}\\n{item.get("result", "")[:500]}\\n\\n---\\n\\n')
        box.config(state="disabled")
if __name__=="__main__":
    root=tk.Tk(); App(root); root.mainloop()
