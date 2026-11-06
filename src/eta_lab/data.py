import csv
import json
import random
from pathlib import Path

SEED = 42

FEATURES = ["distance_km", "prep_minutes", "rain", "peak", "backlog"]

def orders(n=2400, seed=SEED):
 rng=random.Random(seed)
 for i in range(n):
  distance=round(rng.uniform(.5,12),2); prep=round(rng.uniform(7,35),2)
  rain=int(rng.random()<.25); peak=int(rng.random()<.4); backlog=rng.randint(0,8)
  # Mudança moderada no período final; prepara um teste temporal menos favorável.
  drift=1.8 if i>=int(n*.8) else 0
  eta=max(8, 4+2.4*distance+.85*prep+5*rain+4*peak+1.1*backlog+drift+rng.gauss(0,4))
  yield {"order_id":f"SYN-{i:05d}", "time_index":i, "distance_km":distance,
         "prep_minutes":prep,"rain":rain,"peak":peak,"backlog":backlog,
         "eta_minutes":round(eta,2), "synthetic":True}


def generate(base):
 base=Path(base);base.mkdir(parents=True,exist_ok=True)
 rows=list(orders())
 with (base/"orders.csv").open("w",newline="",encoding="utf-8") as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]),lineterminator="\n");w.writeheader();w.writerows(rows)
