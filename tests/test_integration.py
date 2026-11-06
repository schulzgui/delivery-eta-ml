import json
import tempfile
import threading
import unittest
import urllib.request
import urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
from eta_lab.cli import run
from eta_lab.server import handler

class IntegrationTests(unittest.TestCase):
 def test_reproducible_pipeline_and_api(self):
  with tempfile.TemporaryDirectory() as d:
   base=Path(d);run(base);before=(base/'artifacts/metrics.json').read_bytes();run(base)
   self.assertEqual(before,(base/'artifacts/metrics.json').read_bytes())
   server=ThreadingHTTPServer(('127.0.0.1',0),handler(base));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
   url=f'http://127.0.0.1:{server.server_port}'
   try:
    with urllib.request.urlopen(url+'/health') as r:self.assertEqual(json.load(r)['status'],'ok')
    for path,payload in [('eta', {'distance_km': 5, 'prep_minutes': 20, 'rain': 0, 'peak': 1, 'backlog': 3})]:
     req=urllib.request.Request(url+'/api/'+path,json.dumps(payload).encode(),{'Content-Type':'application/json'})
     with urllib.request.urlopen(req) as r:self.assertEqual(r.status,200)
    req=urllib.request.Request(url+'/api/eta',b'{}',{'Content-Type':'application/json','Origin':'http://evil.example'})
    with self.assertRaises(urllib.error.HTTPError) as err:urllib.request.urlopen(req)
    self.assertEqual(err.exception.code,403)
    with self.assertRaises(urllib.error.HTTPError):urllib.request.urlopen(url+'/../../pyproject.toml')
   finally:server.shutdown();thread.join();server.server_close()
