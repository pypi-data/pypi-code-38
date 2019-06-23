#!/usr/bin/python
import requests
from bs4 import BeautifulSoup
import os
import sys
import httplib2
import io
from urllib.parse import urlencode, quote_plus
import http.cookiejar

class NeterraProxy(object):
    def __init__(self, username, password, app_dir):
        self.username = username
        self.password = password
        self.app_dir = app_dir
        self.session = requests.Session()
        self.headers = ""
        self.expireTime = 0 

    def authenticate3(self):
        token = ""
        logged = False
        url="https://neterra.tv/sign-in"
        h = httplib2.Http(".cache")
        resp, content = h.request(url, "GET")

        print("response headers:")
        print(resp)
        print("  ")

        self.headers = {'Cookie': resp['set-cookie']}

        soup = BeautifulSoup(content, 'html.parser')
        token_element = soup.find(attrs={"name" : "_token"})
        token = token_element["value"]

        print("token:")
        print(token)  
        print("  ")   

        self.headers.update({   
            'X-CSRF-TOKEN': '{0}'.format(token),
            'Content-type': 'application/x-www-form-urlencoded'
            })

        print("session headers before post:")
        print (self.headers)
        print(" ")

        with io.open("initial_get_response.html", "w") as text_file:
            text_file.write(str(soup))
        
        payload = {'username': self.username, 'password': self.password, "_token": token}
        http = httplib2.Http(".cache")
        body = urlencode(payload, quote_via=quote_plus)
        response, content = http.request(url, 'POST', headers=self.headers, body=body)

        print(response)
        print(" ")

        soup2 = BeautifulSoup(content, 'html.parser')            
        with io.open("post_response.html", "w") as text_file:
            text_file.write(str(soup2))


    def authenticate(self):
        token = ""
        logged = False
        self.session.cookies.clear()
        url="https://neterra.tv/sign-in"
        try:
            r = self.session.get(url)
            print("response headers after get:")
            print(r.headers)
            print("  ")

            print("session cookies after get:")
            print(self.session.cookies)
            print("  ")

            print("session headers after get:")
            print(self.session.headers)
            print("  ")

            soup = BeautifulSoup(r.content, 'html.parser')
            element = soup.find(attrs={"name" : "_token"})
            token = element["value"]
            
            print("token:")
            print(token)  
            print("  ")   

            import io
            with io.open("initial_get_response.html", "w") as text_file:
                text_file.write(str(soup))

            formBody = {"username": self.username, \
                        "password": self.password, \
                        "_token": token}


            self.session.headers.update({   
            'X-CSRF-TOKEN': '{0}'.format(token)
            })

            print("session headers before post:")
            print (self.session.headers)
            print(" ")

            print("session cookies before post:")
            print(self.session.cookies)
            print("  ")

            r = self.session.post(url, data = formBody)

            print("session cookies after post:")
            print(self.session.cookies)
            print("  ")

            print("request headers:")
            print(r.request.headers)
            print(" ")

            print("response headers:")
            print (r.headers)
            print(" ")

            print("session headers after post:")
            print(self.session.headers)
            print(" ")

            soup = BeautifulSoup(r.content, 'html.parser')            
            import io
            with io.open("post_response.html", "w") as text_file:
                text_file.write(str(soup))

            mainURL = "https://www.neterra.tv" 

            print("session cookies before second get:")
            print(self.session.cookies)
            print("  ")

            r = self.session.get(mainURL)
            soup = BeautifulSoup(r.content, 'html.parser')            
            import io
            with io.open("second_get_response.html", "w") as text_file:
                text_file.write(str(soup))

            print("session cookies after second get:")
            print(self.session.cookies)
            print("  ")

            if r.text.find("\"SIGNED\":true") != -1:
                logged = True
            
            print("login: {0}".format(logged))
            print("check response content in script dir as initial_get_response.html, post_response.html and second_get_response.html")

        except:
            print("error occured:", sys.exc_info()[0])
            raise

username = "ananchev"
password = "7C8UCskhbt8Gdvd4OCKc"
app_dir = os.path.dirname(os.path.abspath(__file__))

net = NeterraProxy(username, password, app_dir)
net.authenticate()