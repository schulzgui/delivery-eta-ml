from .eta import predict
"""Demo somente em loopback, sem arquivos arbitrários ou chamadas externas."""
import json
from http.server import BaseHTTPRequestHandler,ThreadingHTTPServer
from urllib.parse import urlparse

HTML = """<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Delivery ETA ML</title>
<style>body{font:16px system-ui;background:#101724;color:#eef3ff;max-width:1080px;margin:40px auto;padding:20px}h1{font-size:42px}small{color:#b4c7df}.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(290px,1fr));gap:18px}section{background:#1c293c;padding:22px;border-radius:14px}input,button,textarea{box-sizing:border-box;padding:12px;margin:6px 0;width:100%;border-radius:7px;border:1px solid #7290b5}button{background:#b8f874;font-weight:bold;cursor:pointer}pre{white-space:pre-wrap;overflow-wrap:anywhere;font-size:13px}label{display:block}details{margin:24px 0}</style>
<h1>Delivery ETA ML</h1><p>Laboratório independente · <b>100% dados sintéticos</b> · sem vínculo com o iFood</p><small>ML, recuperação de informação e automação auditável. Nenhuma ação financeira é executada.</small>
<div class="grid"><section><h2>01 / Previsão de entrega</h2><form id="eta"><label>Distância (km)<input name="distance_km" type="number" value="5" min="0.5" max="12" step="0.1"></label><label>Preparo estimado (min)<input name="prep_minutes" type="number" value="20" min="7" max="35"></label><label>Chuva (0/1)<input name="rain" type="number" value="0" min="0" max="1"></label><label>Pico (0/1)<input name="peak" type="number" value="1" min="0" max="1"></label><label>Fila (0–8)<input name="backlog" type="number" value="3" min="0" max="8"></label><button>Prever</button></form><pre id="eta-out"></pre></section></div>
<details><summary>Métricas completas e hipóteses</summary><pre id="metrics"></pre></details>
<script>
for(const name of ['eta'])document.getElementById(name).onsubmit=async e=>{e.preventDefault();const out=document.getElementById(name+'-out');try{const payload=Object.fromEntries(new FormData(e.target));const r=await fetch('/api/'+name,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)});out.textContent=JSON.stringify(await r.json(),null,2)}catch(e){out.textContent='Falha de conexão'}};
fetch('/api/metrics').then(r=>r.json()).then(x=>document.getElementById('metrics').textContent=JSON.stringify(x,null,2));
</script></html>"""

def handler(base):
 class Handler(BaseHTTPRequestHandler):
  def send(self,status,payload,kind="application/json"):
   body=(json.dumps(payload,ensure_ascii=False) if kind=="application/json" else payload).encode()
   self.send_response(status);self.send_header("Content-Type",kind+"; charset=utf-8");self.send_header("Content-Length",str(len(body)));self.send_header("X-Content-Type-Options","nosniff");self.end_headers();self.wfile.write(body)
  def do_GET(self):
   path=urlparse(self.path).path
   if path=="/":self.send(200,HTML,"text/html")
   elif path=="/api/metrics":self.send(200,json.loads((base/"artifacts/metrics.json").read_text(encoding="utf-8")))
   elif path=="/health":self.send(200,{"status":"ok","synthetic":True})
   else:self.send(404,{"error":"Rota inexistente"})
  def do_POST(self):
   # JSON estrito + sem CORS; evita formulários cross-origin alterando o SQLite local.
   if self.headers.get("Content-Type","").split(";")[0]!="application/json":return self.send(415,{"error":"Use application/json"})
   origin=self.headers.get("Origin")
   if origin and origin!=f"http://127.0.0.1:{self.server.server_port}":return self.send(403,{"error":"Origem não permitida"})
   try:
    length=int(self.headers.get("Content-Length","0"))
    if not 0<length<=8192:raise ValueError("Corpo deve ter entre 1 e 8192 bytes")
    obj=json.loads(self.rfile.read(length))
    if not isinstance(obj,dict):raise ValueError("Objeto JSON obrigatório")
    path=urlparse(self.path).path
    if path=="/api/eta":
     model=json.loads((base/"artifacts/eta_model.json").read_text(encoding="utf-8"))
     for key,lo,hi in [("distance_km",.5,12),("prep_minutes",7,35),("rain",0,1),("peak",0,1),("backlog",0,8)]:
      if not lo<=float(obj[key])<=hi:raise ValueError("Entrada fora da faixa de treino")
      if key in {"rain","peak","backlog"} and float(obj[key])!=int(float(obj[key])):raise ValueError("Campo discreto inválido")
     result={"eta_minutes":predict(model,obj),"synthetic":True}
    else:return self.send(404,{"error":"Rota inexistente"})
    self.send(200,result)
   except (ValueError,KeyError,TypeError):self.send(400,{"error":"Entrada inválida ou chave já usada com outro conteúdo"})
  def log_message(self,*args):pass
 return Handler

def serve(base,port):
 if not (base/"artifacts/metrics.json").exists():raise SystemExit("Execute primeiro: python -m eta_lab.cli run")
 server=ThreadingHTTPServer(("127.0.0.1",port),handler(base))
 print(f"Demo sintética: http://127.0.0.1:{server.server_port}",flush=True)
 try:server.serve_forever()
 except KeyboardInterrupt:pass
 finally:server.server_close()
