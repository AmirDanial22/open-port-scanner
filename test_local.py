import socket
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

def start_test_server(port):
    """Start a simple HTTP server on given port"""
    class Handler(SimpleHTTPRequestHandler):
        def do_GET(self):
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Test Server Running")
    
    server = HTTPServer(('localhost', port), Handler)
    thread = threading.Thread(target=server.serve_forever)
    thread.daemon = True
    thread.start()
    print(f"Test server started on port {port}")
    return server

# Start test servers on different ports
if __name__ == "__main__":
    print("🚀 Setting up test environment...")
    
    # Start servers on common ports
    ports_to_open = [8080, 8081, 9999]
    servers = []
    
    for port in ports_to_open:
        try:
            server = start_test_server(port)
            servers.append(server)
        except:
            print(f"Port {port} already in use or unavailable")
    
    print("\n✅ Test environment ready!")
    print("Open ports for testing:")
    print("  - http://localhost:8080")
    print("  - http://localhost:8081")
    print("  - http://localhost:9999")
    print("\nNow run the main app: python app.py")
    print("Then scan: 127.0.0.1")
    
    # Keep running
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nShutting down test servers...")
        for server in servers:
            server.shutdown()