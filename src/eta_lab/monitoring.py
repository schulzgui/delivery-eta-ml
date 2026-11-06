"""Intervalos conformais e PSI sem dependências externas."""
import math
from .eta import fit,predict,metrics
from .data import FEATURES

def quantile(values,coverage=.9):
 if not values or not 0<coverage<1:raise ValueError("Calibração e cobertura inválidas")
 return sorted(values)[min(len(values)-1,math.ceil((len(values)+1)*coverage)-1)]

def psi(reference,current):
 ordered=sorted(reference)
 edges=sorted(set(ordered[min(len(ordered)-1,int(len(ordered)*i/10))] for i in range(1,10)))
 def bins(values):
  counts=[.5]*(len(edges)+1)
  for v in values:counts[sum(v>e for e in edges)]+=1
  return [c/sum(counts) for c in counts]
 p,q=bins(reference),bins(current)
 return sum((a-b)*math.log(a/b) for a,b in zip(p,q))

def assess(rows,alpha):
 # Modelo próprio: 60% treino, 20% calibração, 20% teste. Sem refit após calibração.
 train=rows[:int(.6*len(rows))];cal=rows[int(.6*len(rows)):int(.8*len(rows))];test=rows[int(.8*len(rows)):]
 # Alpha fixo evita reutilizar calibração para seleção de hiperparâmetros.
 model=fit(train,alpha)
 radius=quantile([abs(float(r["eta_minutes"])-predict(model,r)) for r in cal])
 preds=[predict(model,r) for r in test]
 return {"model":model,"nominal_coverage":.9,"radius_minutes":radius,
 "test_coverage":sum(abs(float(r["eta_minutes"])-p)<=radius for r,p in zip(test,preds))/len(test),
 "mean_interval_width_minutes":2*radius,"test":metrics(test,preds),
 "feature_psi":{k:psi([float(r[k]) for r in train],[float(r[k]) for r in test]) for k in FEATURES},
 "caveat":"Cobertura nominal exige permutabilidade; mudança temporal viola essa hipótese. PSI não detecta sozinho mudança em P(y|x)."}
