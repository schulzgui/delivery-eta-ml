"""Regressão ridge em Python puro; estatísticas ajustadas apenas no treino."""
import math
from .data import FEATURES

def solve(a,b):
 m=[list(row)+[v] for row,v in zip(a,b)]; n=len(b)
 for j in range(n):
  pivot=max(range(j,n),key=lambda i:abs(m[i][j]));m[j],m[pivot]=m[pivot],m[j]
  if abs(m[j][j])<1e-12: raise ValueError("Matriz singular")
  scale=m[j][j];m[j]=[v/scale for v in m[j]]
  for i in range(n):
   if i!=j:
    factor=m[i][j];m[i]=[x-factor*y for x,y in zip(m[i],m[j])]
 return [r[-1] for r in m]

def fit(rows,alpha=1):
 means=[sum(float(r[k]) for r in rows)/len(rows) for k in FEATURES]
 scales=[max(1e-8,math.sqrt(sum((float(r[k])-mu)**2 for r in rows)/len(rows))) for k,mu in zip(FEATURES,means)]
 x=[[1]+[(float(r[k])-mu)/sd for k,mu,sd in zip(FEATURES,means,scales)] for r in rows]
 n=len(FEATURES)+1
 a=[[sum(v[i]*v[j] for v in x)+(alpha if i==j and i>0 else 0) for j in range(n)] for i in range(n)]
 b=[sum(v[i]*float(r["eta_minutes"]) for v,r in zip(x,rows)) for i in range(n)]
 return {"features":FEATURES,"means":means,"scales":scales,"weights":solve(a,b),"alpha":alpha}

def predict(model,row):
 values=[]
 for k,mu,sd in zip(model["features"],model["means"],model["scales"]):
  v=float(row[k])
  if not math.isfinite(v): raise ValueError("Entrada deve ser finita")
  values.append((v-mu)/sd)
 return max(0,sum(a*b for a,b in zip(model["weights"],[1]+values)))

def metrics(rows,preds):
 errors=[abs(float(r["eta_minutes"])-p) for r,p in zip(rows,preds)]
 return {"n":len(errors),"mae_minutes":sum(errors)/len(errors),"rmse_minutes":math.sqrt(sum(e*e for e in errors)/len(errors)),"p90_absolute_error_minutes":sorted(errors)[math.ceil(.9*len(errors))-1]}

def evaluate(rows):
 train=rows[:int(len(rows)*.6)];valid=rows[int(len(rows)*.6):int(len(rows)*.8)];test=rows[int(len(rows)*.8):]
 candidates=[]
 for alpha in [0.01,1,10,100]:
  model=fit(train,alpha); candidates.append((metrics(valid,[predict(model,r) for r in valid])["mae_minutes"],alpha))
 _,alpha=min(candidates)
 model=fit(train+valid,alpha)
 baseline=sum(float(r["eta_minutes"]) for r in train+valid)/len(train+valid)
 report={"split":"temporal 60/20/20; refit em 80% após seleção", "selected_alpha":alpha,
 "validation_mae_by_alpha":{str(a):m for m,a in candidates},
 "test":metrics(test,[predict(model,r) for r in test]),"baseline_test":metrics(test,[baseline]*len(test)),
 "slices":{}}
 for field in ["rain","peak"]:
  for value in [0,1]:
   subset=[r for r in test if int(r[field])==value]
   report["slices"][f"{field}={value}"]=metrics(subset,[predict(model,r) for r in subset])
 return model,report
