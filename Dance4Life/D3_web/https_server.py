from http.server import HTTPServer, SimpleHTTPRequestHandler
import ssl

server = HTTPServer(
    ("0.0.0.0", 8000),
    SimpleHTTPRequestHandler
)

context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)

context.load_cert_chain(
    certfile="cert.pem",
    keyfile="key.pem"
)

server.socket = context.wrap_socket(
    server.socket,
    server_side=True
)

print("HTTPS server running on https://0.0.0.0:8000")

server.serve_forever()