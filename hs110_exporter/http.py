import urlparse
import socket
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ForkingMixIn

from prometheus_client import CONTENT_TYPE_LATEST


from collector import collect_hs110

# Check if hostname is valid
def validHostname(hostname):
	try:
		socket.gethostbyname(hostname)
	except socket.error:
		return 0
	return 1

class ForkingHTTPServer(ForkingMixIn, HTTPServer):
  pass

class Hs110ExporterHandler(BaseHTTPRequestHandler):
  def __init__(self, *args, **kwargs):
    BaseHTTPRequestHandler.__init__(self, *args, **kwargs)

  def do_GET(self):
    url = urlparse.urlparse(self.path)
    if url.path == '/metrics':
      params = urlparse.parse_qs(url.query)
      if 'target' not in params:
        self.send_response(400)
        self.end_headers()
        self.wfile.write("Missing 'target' from parameters")
        return
      if not validHostname(params['target'][0]):
        self.send_response(400)
        self.end_headers()
        self.wfile.write("Invalid hostname")
        return

      output = collect_hs110(params['target'][0])
      
      self.send_response(200)
      self.send_header('Content-Type', CONTENT_TYPE_LATEST)
      self.end_headers()
      self.wfile.write(output)
    elif url.path == '/':
      self.send_response(200)
      self.end_headers()
      self.wfile.write("""<html>
      <head><title>HS110 Exporter</title></head>
      <body>
      <h1>HS110 Exporter</h1>
      <p>Visit <code>/metrics?target=1.2.3.4</code> to use.</p>
      </body>
      </html>""")
    else:
      self.send_response(404)
      self.end_headers()

def start_http_server( port):
  handler = lambda *args, **kwargs: Hs110ExporterHandler( *args, **kwargs)
  server = ForkingHTTPServer(('', port), handler)
  server.serve_forever()

