"""HALO-XR · server lokal (python serve.py [port]).
Memaksa MIME type yang benar: di Windows, registry sering memetakan .js ke text/plain sehingga modul ES gagal dimuat."""
import http.server, sys, os

class Handler(http.server.SimpleHTTPRequestHandler):
    extensions_map = {**http.server.SimpleHTTPRequestHandler.extensions_map,
        ".js": "text/javascript", ".mjs": "text/javascript", ".json": "application/json", ".webmanifest": "application/manifest+json",
        ".glb": "model/gltf-binary", ".webp": "image/webp", ".svg": "image/svg+xml", ".wasm": "application/wasm", ".css": "text/css"}

if __name__ == "__main__":
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"HALO-XR: http://localhost:{port}  (Ctrl+C untuk berhenti)")
    http.server.ThreadingHTTPServer(("", port), Handler).serve_forever()
