import http.server
import socketserver
import os

PORT = 8080

class CleanURLHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Extract path without query parameters
        clean_path = self.path.split('?')[0]
        
        # Root route
        if clean_path == '/':
            self.path = '/index.html'
        # If clean path doesn't have an extension (e.g. /work), check if .html file exists
        elif not os.path.splitext(clean_path)[1]:
            html_file = clean_path + '.html'
            if os.path.exists(self.translate_path(html_file)):
                self.path = html_file
                
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

if __name__ == "__main__":
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), CleanURLHandler) as httpd:
        print(f"Clean URL Server running at http://localhost:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
