#!/usr/bin/env python3
"""
Simple HTTP server to test frontend pages
Run: python3 serve.py
Then open: http://localhost:8003/html/login.html
"""

import http.server
import socketserver

PORT = 8003

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def end_headers(self):
        # Add CORS headers
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
    print(f"✅ Frontend server running at http://localhost:{PORT}/")
    print(f"📂 Open: http://localhost:{PORT}/html/login.html")
    print(f"   Django backend should be at: http://localhost:8002/")
    print(f"\n   Press Ctrl+C to stop")
    httpd.serve_forever()
