#!/usr/bin/env python3


import os
# HTTP Server
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import unquote, parse_qs
import cgi
# Threading to Server
from socketserver import ThreadingMixIn

# SQL Alchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Local file, importing tables
from database_setup import Base, Restaurant, MenuItem

# Local file, importing HTML content
import html_data


# Create SQLite3 DB engine
engine = create_engine('sqlite:///restaurantmenu.db')
# Attach engine with Base (table) class
Base.metadata.bind = engine
# Create session and bind to DB engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


memory = []

res_path = '/restaurants'
add_res_path = '/restaurants/add'
add_res_e_path = '/restaurants/add/error'


class MessageHandler(BaseHTTPRequestHandler):
    """To handle messages from the client"""
    def do_GET(self):

        try:
            name = unquote(self.path)
            print('\nGET --> Now in Path: {}\n'.format(name))

            if name == '/':
                # send a 200 OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # Writing message
                self.wfile.write(
                    html_data.root_cnt.format(
                        res_path,
                        "\n".join(memory)
                        ).encode()
                    )
            
            elif name == res_path:
                # send a 200 OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                # SQL Query to get restaurant names
                restaurants = session.query(Restaurant).all()
                print('\nRestaurants:\n-----------')

                # Writing message
                output_text = ''
                for restaurant in restaurants:
                    output_text += html_data.btn_cnt.format(restaurant.name)
                    print(restaurant.name)
                print("")

                self.wfile.write(
                    html_data.res_cnt.format(
                        add_res_path,
                        output_text
                        ).encode()
                    )

            elif name == add_res_path:
                # send a 200 OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                self.wfile.write(
                    html_data.add_res_cnt.format("",res_path).encode())

            elif name == add_res_e_path:
                # send a 200 OK response
                self.send_response(200)
                self.send_header('Content-type', 'text/html; charset=utf-8')
                self.end_headers()

                self.wfile.write(
                    html_data.add_res_cnt.format(
                        html_data.add_res_e_cnt,
                        res_path
                        ).encode()
                    )

            #else:
                # Send a 303 back to the root page
                #self.send_response(303)  # redirect via GET
                #self.send_header('Location', '/') # redirect to root
                #self.end_headers()
        
        except IOError:
            self.send_response(404)
            self.send_header('Content-type', 'text/plain; charset=utf-8')
            self.end_headers()

            self.wfile.write("404: Not found".encode())

    def do_POST(self):
        name = unquote(self.path)
        print('\nPOST --> Now in Path: {}\n'.format(name))

        try:
            if name == '/':
                # Send a 303 back to the root page
                self.send_response(303)  # redirect via GET
                self.send_header('Location', '/')
                self.end_headers()

                # Getting message length
                length = int(self.headers.get('Content-length', 0))

                # Read and parse message
                data = self.rfile.read(length).decode()
                message = parse_qs(data)['message'][0]

                # Escape HTML tags in the message so users can't break world
                #   +dog.
                message = message.replace("<", "&lt;")

                # Store it in memory.
                if message != '':
                    memory.append(message)
                
            elif name == add_res_path or name == add_res_e_path:
                # Getting message length
                length = int(self.headers.get('Content-length', 0))

                # Read and parse message
                data = self.rfile.read(length).decode()
                res_name = parse_qs(data)['restaurant_name'][0]

                # Escape HTML tags in the message so users can't break world
                #   +dog.
                res_name = res_name.replace("<", "&lt;")
                print("\nRestaurant name entered {}".format(res_name))
                    
                # Add new restaurant
                res = Restaurant(name=res_name)
                session.add(res)
                session.commit()
                print("\n++ Restaurant \'{}\' is added\n".format(res_name))

                # Send a 303 back to the restaurants page
                self.send_response(303)  # redirect via GET
                self.send_header('Location', res_path)
                self.end_headers()
        
        except:
            print("\nError in POST!\n")
            if name == add_res_path or name == add_res_e_path:
                print(">> Restaurant name field is Empty!")

                # Send a 303 back to the add restaurant page
                self.send_response(303)  # redirect via GET
                self.send_header('Location', add_res_e_path)
                self.end_headers()
                
            else:
                print(">> Other")
            #pass


# Adding threading functionality to server
class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
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
