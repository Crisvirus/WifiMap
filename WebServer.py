from http.server import BaseHTTPRequestHandler, HTTPServer
from WIFIAPHandler import WIFIAPHandler
from os import curdir, sep
import json
import cgi
import ssl
from bcrypt import hashpw, gensalt
from tinydb import TinyDB, Query
from http import cookies
import random
import math
from uuid import uuid4
from threading import Timer
import requests

def MakeHandlerClassFromArgv(WIFIAP_handler):
    user_passwd = {}
    passwdDB = TinyDB('./passwordDB/passwdDB.json')
    tokens = {}
    timers = {}
    for line in passwdDB.all():
        username = line['u']
        passwd = line['p']
        user_passwd[username] = passwd

    def delete_token(token):
        del tokens[token]
        timers[token].cancel()
        del timers[token]

    def token_is_valid(token):
        if token in tokens:
            return True
        else :
            return False

    def login(username,passwd):
        print("User = "+str(type(username))+" passwd = "+str(type(passwd))+"\n")
        if username not in user_passwd:
            print("User does not exist\n")
            return False
        else:
            hashed_passwd = user_passwd[username]
            if hashpw(passwd.encode('utf-8'),hashed_passwd.encode('utf-8')).decode('utf-8') == hashed_passwd:
                return True
            else:
                return False

    def create(username,passwd):
        if username in user_passwd:
            print("Already exists\n")
            return False
        else:
            hashed = hashpw(passwd.encode('utf-8'), gensalt())
            user_passwd[username] = hashed.decode('utf-8')
            entry = {}
            entry['u'] = str(username)
            entry['p'] = hashed.decode('utf-8')
            passwdDB.insert(entry)
            return True

    class WebServer(BaseHTTPRequestHandler):
        def _set_response(self,content):
            self.send_response(200)
            self.send_header('Content-type', content)
            self.end_headers()

        def serveWithCookie(self):
            token = ''
            if "Cookie" in self.headers:
                cookie_string = self.headers.get('Cookie')
                c = cookies.SimpleCookie()
                c.load(cookie_string)
                for key, morsel in c.items():
                    if key == 'token':
                        token = morsel.value
            else:
                print("No cookie for you\n")
            
            if token_is_valid(token):
                if '/BSSID' in self.path:
                    tokens = self.path.split('?')
                    bssid = tokens[1]
                    print(bssid)
                    html = "Not Found"
                    if bssid in WIFIAP_handler.BSSIDDict:
                        wifiap = WIFIAP_handler.BSSIDDict[bssid]
                        html = wifiap.getHTML()
                    else:
                        html = "Not Found"
                    self._set_response('text/html')
                    self.wfile.write(bytearray(html,"UTF-8"))
                    return

                if '/ESSID' in self.path:
                    tokens = self.path.split('?')
                    essid = tokens[1]
                    print(essid)
                    html = "Not Found"
                    if essid in WIFIAP_handler.ESSIDDict:
                        html = WIFIAP_handler.getListByESSID(essid)
                    else:
                        html = "[Not Found]"
                    self._set_response('application/json')
                    self.wfile.write(bytearray(html,"UTF-8"))
                    return
            
            else:
                print("Bad token\n")
                self.send_response(301)
                self.send_header('Location','/')
                self.end_headers()

        def do_GET(self):
            print(self.path)
            if self.path=="/":
                f = open(curdir + sep + "HTML/index.html")
                self._set_response('text/html')
                self.wfile.write(bytearray(f.read(),"UTF-8"))
                f.close()
                return

            if self.path=="/create.html":
                self.path="/create.html"
                mimetype='text/html'
                f = open(curdir + sep + "HTML/create.html") 
                self.send_response(200)
                self.send_header('Content-type',mimetype)
                self.end_headers()
                self.wfile.write(bytearray(f.read(),"UTF-8"))
                f.close()
                return

            self.serveWithCookie()

        def do_POST(self):
            #==========================Login===========================
            if self.path=="/login":
                print("Login\n")
                form = cgi.FieldStorage(
                    fp=self.rfile, 
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                            'CONTENT_TYPE':self.headers['Content-Type'],
                })
                username = form["uname"].value
                if login(username, form["psw"].value):
                    print("HERE")
                    f = open(curdir + sep + "HTML/search.html")
                    mimetype='text/html'
                    c = cookies.SimpleCookie()
                    rand_token = uuid4()
                    tokens[str(rand_token)] = form["uname"].value
                    c['token'] = str(rand_token)
                    c['token']['expires'] = 3*60*60
                    t = Timer(3*60*60, delete_token,args = [str(rand_token)])
                    t.start()
                    timers[str(rand_token)] = t
                    self.send_response(200)
                    self.send_header('Set-Cookie',str(c)[12:])
                    self.send_header('Content-type',mimetype)
                    self.end_headers()
                    self.wfile.write(bytearray(f.read(),"UTF-8"))
                    f.close()
                else:
                    self.send_response(301)
                    self.send_header('Location','/')
                    self.end_headers()

            if self.path=="/create":
                form = cgi.FieldStorage(
                    fp=self.rfile, 
                    headers=self.headers,
                    environ={'REQUEST_METHOD':'POST',
                            'CONTENT_TYPE':self.headers['Content-Type'],
                })
                if create(form["uname"].value, form["psw"].value):
                    self.send_response(301)
                    self.send_header('Location','/')
                    self.end_headers()
                else:
                    self.send_response(301)
                    self.send_header('Location','/')
                    self.end_headers()   
    return WebServer