# tests/test_recorder.py
import os
import json
import tempfile
import threading
from selenium import webdriver
from http.server import SimpleHTTPRequestHandler, HTTPServer
import time
import pytest

from riskbench_core.recorder import record_session

@pytest.fixture(scope="module")
def demo_server(tmp_path_factory):
    # serve a simple HTML page to click on
    folder = tmp_path_factory.mktemp("demo")
    html = folder / "index.html"
    html.write_text("""
      <html><body>
        <button id="btn">Click me</button>
        <script>
          document.getElementById('btn').addEventListener('click', ()=>{console.log('clicked')});
        </script>
      </body></html>
    """, encoding="utf-8")

    os.chdir(str(folder))
    server = HTTPServer(("localhost", 8765), SimpleHTTPRequestHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    yield "http://localhost:8765/index.html"
    server.shutdown()
    thread.join()

def test_record_session(demo_server, tmp_path):
    out_file = tmp_path / "log.jsonl"
    # run headless for 5s so test completes
    record_session(start_url=demo_server, out_path=str(out_file), headless=True, timeout=5)
    lines = out_file.read_text(encoding="utf-8").strip().splitlines()
    # must have at least a navigate event and possibly more
    assert any(json.loads(l)["action"] == "navigate" for l in lines)
