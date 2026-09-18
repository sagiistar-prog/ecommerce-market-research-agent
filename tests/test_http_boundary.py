import http.client
import json
from http.server import ThreadingHTTPServer
from pathlib import Path
import sys
import threading
import unittest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from app_server import AgentRequestHandler

class LocalHttpBoundary(unittest.TestCase):
    def setUp(self):
        self.server=ThreadingHTTPServer(('127.0.0.1',0),AgentRequestHandler)
        self.thread=threading.Thread(target=self.server.serve_forever,daemon=True);self.thread.start()
    def tearDown(self):
        self.server.shutdown();self.server.server_close();self.thread.join()
    def request(self,headers):
        connection=http.client.HTTPConnection('127.0.0.1',self.server.server_port,timeout=2)
        connection.request('POST','/api/generate',body=b'{}',headers=headers)
        response=connection.getresponse();status=response.status;response.read();connection.close();return status
    def test_cross_origin_and_forged_host_rejected(self):
        self.assertEqual(self.request({'Origin':'https://untrusted.example'}),403)
        self.assertEqual(self.request({'Host':'untrusted.example'}),403)
    def test_negative_and_oversized_content_length_rejected(self):
        self.assertEqual(self.request({'Content-Length':'-1'}),400)
        self.assertEqual(self.request({'Content-Length':'1000001'}),400)

    def post_json(self, payload, path='/api/generate'):
        connection = http.client.HTTPConnection('127.0.0.1', self.server.server_port, timeout=4)
        connection.request('POST', path, body=json.dumps(payload).encode(), headers={'Content-Type':'application/json'})
        response = connection.getresponse()
        result = response.status, json.loads(response.read())
        connection.close()
        return result

    def test_valid_web_result_matches_plugin_analysis(self):
        from plugin_run import run
        root = Path(__file__).resolve().parents[1]
        fixture = json.loads((root/'examples/pet-bowl-input.json').read_text(encoding='utf-8'))
        status, result = self.post_json({'brief':fixture['brief'], 'competitors':fixture['competitors_csv']})
        self.assertEqual(status, 200)
        self.assertEqual(result['analysis'], run(fixture)['result']['analysis'])

    def test_non_text_and_unknown_input_not_silently_coerced(self):
        for payload in [{'brief':{}, 'competitors':'x'}, {'brief':'x', 'competitors':[]}, {'brief':'x', 'competitors':'x', 'unexpected':True}]:
            status, result = self.post_json(payload)
            self.assertEqual(status, 400)
            self.assertIn('error', result)

    def test_hypothesis_import_and_review_export_use_real_reference_validation(self):
        from plugin_run import run
        root=Path(__file__).resolve().parents[1]
        fixture=json.loads((root/'examples/pet-bowl-input.json').read_text(encoding='utf-8'))
        analysis=run(fixture)['result']['analysis']
        decisions=json.loads((root/'examples/pet-bowl-decisions.json').read_text(encoding='utf-8'))
        body={'analysis':analysis,'decisions':decisions}
        status,result=self.post_json(body,'/api/decisions');self.assertEqual(status,200)
        body['review']=result['review'];body['review']['entries'][0].update(choice='reject',reason='Fictional review: the evidence is insufficient.')
        status,result=self.post_json(body,'/api/review');self.assertEqual(status,200)
        self.assertEqual(result['package']['summary']['choices']['reject'],1)
        body['decisions']['proposals'][0]['proposed_change']='Changed proposal'
        status,result=self.post_json(body,'/api/review');self.assertEqual(status,400)
        self.assertIn('changed',result['error'])

    def test_invalid_hypothesis_shape_returns_a_recoverable_client_error(self):
        for body in ({'analysis':None,'decisions':{}},{'analysis':{},'decisions':[]},{'analysis':{},'decisions':{},'unexpected':True}):
            status,_=self.post_json(body,'/api/decisions');self.assertEqual(status,400)
