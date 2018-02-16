#!/usr/bin/env python3

import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, parse_qs
from socketserver import ThreadingMixIn


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    pass

memory = []

form = '''<!DOCTYPE html>
  <title>Message Board</title>
  <form method="POST">
    <textarea name="message"></textarea>
    <br>
    <button type="submit">Post it!</button>
  </form>
  <pre>
{}
  </pre>
'''

class MessageHandler(BaseHTTPRequestHandler):
    """To handle messages from the client"""
    def do_GET(self):

        try:
            name = unquote(self.path[1:])
            print('Unquoted Path: {}'.format(name))
            if name == '':

                # send a 200 OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # Writing message
                mesg = form.format("\n".join(memory))
                self.wfile.write(mesg.encode())
            
            elif name == 'restaurants':
                restaurants = session.query(Restaurant).all()
        
        except IOError:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()

            self.wfile.write("404: Not found".encode())

    def do_POST(self):
        try:
            # Send a 303 back to the root page
            self.send_response(303)  # redirect via GET
            self.send_header('Location', '/')
            self.end_headers()

            # Getting message length
            length = int(self.headers.get('Content-length', 0))

            # Read and parse message
            data = self.rfile.read(length).decode()
            message = parse_qs(data)['message'][0]

            # Escape HTML tags in the message so users can't break world+dog.
            message = message.replace("<", "&lt;")

            # Store it in memory.
            if message != '':
                memory.append(message)
        
        except:
            pass


# This starts the server
if __name__ == '__main__':
    try:
        port = int(os.environ.get('PORT', 8000))
        server_address = ('', port)
        server = ThreadedHTTPServer(server_address, MessageHandler)
        print("\nServer is up and running on port {} >>>>>>>>>>\n".format(port))
        server.serve_forever()
        print('abc!!!')

    except KeyboardInterrupt:
        print("\n^^ Keyboard exception received, stopping server...\n")
        server.socket.close()
