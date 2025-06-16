import http.server
import cgi
import tempfile
import os
from typing import List
from arxml_merger import parse_arxml, merge_trees, parse_rules

HTML_FORM = b"""<html><body><h1>ARXML Merger</h1>
<form method='post' enctype='multipart/form-data'>
<input type='file' name='files' multiple><br>
<select name='strategy'>
<option value='conservative'>conservative</option>
<option value='latest-wins'>latest-wins</option>
<option value='interactive'>interactive</option>
<option value='rule-based'>rule-based</option>
</select>
<input type='submit' value='Merge'>
</form></body></html>"""

class Handler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.end_headers()
        self.wfile.write(HTML_FORM)

    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.get("Content-Type"))
        if ctype != 'multipart/form-data':
            self.send_error(400, "Invalid form")
            return
        form = cgi.FieldStorage(fp=self.rfile, headers=self.headers,
                                environ={'REQUEST_METHOD':'POST'}, keep_blank_values=True)
        files = form['files']
        if not isinstance(files, list):
            files = [files]
        strategy = form.getvalue('strategy', 'conservative')
        temp_paths: List[str] = []
        for item in files:
            if not item.filename:
                continue
            with tempfile.NamedTemporaryFile(delete=False, suffix='.arxml') as tmp:
                tmp.write(item.file.read())
                temp_paths.append(tmp.name)
        trees = []
        for path in temp_paths:
            t = parse_arxml(path)
            if t is not None:
                trees.append(t)
        for path in temp_paths:
            os.unlink(path)
        if not trees:
            self.send_error(400, "No valid files uploaded")
            return
        merged = merge_trees(trees, strategy, parse_rules(None))
        out = tempfile.NamedTemporaryFile(delete=False, suffix='.arxml')
        merged.write(out.name, encoding='utf-8', xml_declaration=True)
        out.seek(0)
        data = out.read()
        out.close()
        os.unlink(out.name)
        self.send_response(200)
        self.send_header('Content-Type', 'application/xml')
        self.send_header('Content-Disposition', 'attachment; filename="merged.arxml"')
        self.send_header('Content-Length', str(len(data)))
        self.end_headers()
        self.wfile.write(data)

def run(server_class=http.server.HTTPServer, handler_class=Handler, port=8000):
    server_address = ('', port)
    with server_class(server_address, handler_class) as httpd:
        print(f'Serving on http://localhost:{port}')
        httpd.serve_forever()

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Start simple ARXML merge web server')
    parser.add_argument('--port', type=int, default=8000, help='Port to listen on')
    args = parser.parse_args()
    run(port=args.port)
