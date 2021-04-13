from WIFIAPHandler import WIFIAPHandler
from WebServer import MakeHandlerClassFromArgv
from http.server import HTTPServer
import _thread
import os
import ssl
handler = WIFIAPHandler()
try:
    # waypointsDB.readFromFile()
    # print(len(waypointsDB.waypoints))
    print("Ready to receive ACARS Messages\n")

    httpd = HTTPServer(('',8888),MakeHandlerClassFromArgv(handler))
    # Check if we have certificates
    if os.path.exists("./certs"):
        if len(os.listdir('./certs')) != 0:
            print("Certificates found, using HTTPS")
            httpd.socket = ssl.wrap_socket (httpd.socket,
                keyfile='certs/privkey.pem',
                certfile='certs/fullchain.pem', server_side=True)
        else:
            print("No certificates, using HTTP")
    else:
        print("No certificates, using HTTP")
    httpd.serve_forever()

except KeyboardInterrupt:
    print('^C received, shutting down the web server')
