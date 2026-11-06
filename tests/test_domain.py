import concurrent.futures
import tempfile
import math
import unittest
from pathlib import Path
from eta_lab.data import orders
from eta_lab.eta import fit,predict,evaluate
from eta_lab.monitoring import quantile,psi

class MLTests(unittest.TestCase):
 def test_determinism(self):self.assertEqual(list(orders(40)),list(orders(40)))
 def test_recovers_linear_function(self):
  rows=list(orders(300))
  for r in rows:r['eta_minutes']=3+2*r['distance_km']+.5*r['prep_minutes']
  m=fit(rows,0)
  for r in list(orders(30,99)):self.assertAlmostEqual(predict(m,r),3+2*r['distance_km']+.5*r['prep_minutes'],places=7)
 def test_temporal_test_not_used_for_fit(self):
  rows=list(orders(300));model,_=evaluate(rows)
  for r in rows[240:]:r['eta_minutes']=9999
  changed,_=evaluate(rows);self.assertEqual(model,changed)
 def test_beats_baseline(self):
  _,r=evaluate(list(orders()));self.assertLess(r['test']['mae_minutes'],r['baseline_test']['mae_minutes'])
 def test_nan_rejected(self):
  rows=list(orders(30));m=fit(rows);rows[0]['rain']=math.nan
  with self.assertRaises(ValueError):predict(m,rows[0])
 def test_conformal_order_statistic(self):self.assertEqual(quantile(list(range(1,10)),.8),8)
 def test_drift(self):
  self.assertAlmostEqual(psi(list(range(100)),list(range(100))),0)
  self.assertGreater(psi(list(range(100)),list(range(300,400))),1)
