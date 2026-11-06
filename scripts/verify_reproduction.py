"""Compare artefatos com tolerância para arredondamento entre versões Python."""
import json
import math
from pathlib import Path
from eta_lab.cli import run

def compare(a,b,path="root"):
 if isinstance(a,bool) or a is None or isinstance(a,str):
  assert a==b,(path,a,b)
 elif isinstance(a,(float,int)):
  assert isinstance(b,(float,int)) and math.isclose(a,b,rel_tol=1e-10,abs_tol=1e-10),(path,a,b)
 elif isinstance(a,dict):
  assert a.keys()==b.keys(),path
  for k in a:compare(a[k],b[k],path+"."+k)
 elif isinstance(a,list):
  assert len(a)==len(b),path
  for i,(x,y) in enumerate(zip(a,b)):compare(x,y,f"{path}[{i}]")
 else:raise TypeError(path)

if __name__=="__main__":
 expected={p.name:json.loads(p.read_text(encoding="utf-8")) for p in Path("artifacts").glob("*.json") if p.name!="manifest.json"}
 assert "metrics.json" in expected,"Métricas versionadas ausentes"
 data={p.name:p.read_bytes() for p in Path("data").glob("*") if p.suffix in {".csv",".json"}}
 run(Path("."))
 for name,value in expected.items():compare(value,json.loads((Path("artifacts")/name).read_text(encoding="utf-8")),name)
 for name,value in data.items():assert value==(Path("data")/name).read_bytes(),name
 print("Dados idênticos e métricas reproduzidas (tolerância 1e-10).")
