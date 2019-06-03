import requests
import json

def Genel(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEXT):
        """
        ACCESS_TOKEN= Erişim anahtarını ifade eder turkce.ai üzerinden alınız.
        ACCESS_TOKEN_SECRET= Erişim gizli anahtarını ifade eder turkce.ai üzerinden alınız.
        TEXT= Analiz yapılacak metni giriniz. kelime üstü giriniz. JSON sonuç döner.
        """
        url = "http://localhost:5000/Api/general"

        querystring = {"AccessToken":ACCESS_TOKEN,"AccessTokenSecret":ACCESS_TOKEN_SECRET}

        payload = {"text":TEXT}
        headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'User-Agent': "PostmanRuntime/7.13.0",
        'Host': "localhost:5000",
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return json.dumps(response.json())



def Duygu(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEXT):
        """
        ACCESS_TOKEN= Erişim anahtarını ifade eder turkce.ai üzerinden alınız.
        ACCESS_TOKEN_SECRET= Erişim gizli anahtarını ifade eder turkce.ai üzerinden alınız.
        TEXT= Analiz yapılacak metni giriniz. kelime üstü giriniz. JSON sonuç döner.
                """
        url = "http://localhost:5000/Api/sentiment"

        querystring = {"AccessToken":ACCESS_TOKEN,"AccessTokenSecret":ACCESS_TOKEN_SECRET}

        payload = {"text":TEXT}
        headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'User-Agent': "PostmanRuntime/7.13.0",
        'Host': "localhost:5000",
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return json.dumps(response.json())



def RuhHali(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEXT):
        """
        ACCESS_TOKEN= Erişim anahtarını ifade eder turkce.ai üzerinden alınız.
        ACCESS_TOKEN_SECRET= Erişim gizli anahtarını ifade eder turkce.ai üzerinden alınız.
        TEXT= Analiz yapılacak metni giriniz. kelime üstü giriniz. JSON sonuç döner.
                """
        url = "http://localhost:5000/Api/emotion"

        querystring = {"AccessToken":ACCESS_TOKEN,"AccessTokenSecret":ACCESS_TOKEN_SECRET}

        payload = {"text":TEXT}
        headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'User-Agent': "PostmanRuntime/7.13.0",
        'Host': "localhost:5000",
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return json.dumps(response.json())



def Kategori(ACCESS_TOKEN, ACCESS_TOKEN_SECRET, TEXT):
        """
        ACCESS_TOKEN= Erişim anahtarını ifade eder turkce.ai üzerinden alınız.
        ACCESS_TOKEN_SECRET= Erişim gizli anahtarını ifade eder turkce.ai üzerinden alınız.
        TEXT= Analiz yapılacak metni giriniz. kelime üstü giriniz. JSON sonuç döner.
        """
        url = "http://localhost:5000/Api/categories"

        querystring = {"AccessToken":ACCESS_TOKEN,"AccessTokenSecret":ACCESS_TOKEN_SECRET}

        payload = {"text":TEXT}
        headers = {
        'Content-Type': "application/x-www-form-urlencoded",
        'User-Agent': "PostmanRuntime/7.13.0",
        'Host': "localhost:5000",
        }

        response = requests.request("POST", url, data=payload, headers=headers, params=querystring)

        return json.dumps(response.json())

