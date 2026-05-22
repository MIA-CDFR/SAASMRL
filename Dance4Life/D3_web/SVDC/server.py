
import http.server, socketserver, webbrowser, os
PORT = 8000
os.chdir(os.path.dirname(__file__))
Handler = http.server.SimpleHTTPRequestHandler
with socketserver.TCPServer(("", PORT), Handler) as httpd:
    webbrowser.open(f"http://localhost:{PORT}")
    print(f"Running on http://localhost:{PORT}")
    httpd.serve_forever()
