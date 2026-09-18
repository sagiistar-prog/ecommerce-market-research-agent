import http.client
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
