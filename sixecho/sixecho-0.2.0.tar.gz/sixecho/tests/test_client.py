# coding=utf-8
from unittest import TestCase
from sixecho import Client
import sixecho
from time import sleep
class TestSixecho(TestCase):
    def test_tokenize(self):
        word = 'ในการเขียนโปรแกรมในภาษา Python โมดูล (Module) คือไฟล์ของโปรแกรมที่กำหนดตัวแปร ฟังก์ชัน หรือคลาสโดยแบ่งย่อยออกไปจากโปรแกรมหลัก และสามารถนำมาใช้งานได้โดยการนำเข้ามาในโปรแกรม (Import) กล่าวอีกนัยหนึ่ง โมดูลก็คือไลบรารี่ที่สร้างไว้และนำมาใช้งานในโปรแกรม ในบทนี้ เราจะพูดถึงความหมายของโมดูล การสร้าง และการใช้งานโมดูลในการเขียนโปรแกรม นอกจากนี้ เราจะแนะนำให้คุณรู้จักกับ Package ซึ่งเป็นแนวคิดในการจัดการกับโมดูลในรูปแบบของ Namespace'
        words = sixecho.tokenize(str=word)
        self.assertTrue(words>0)
    
    def test_printProgressBar(self):
        items = list(range(0, 57))
        l = len(items)
        sixecho.printProgressBar(0, l, prefix = 'Progress:', suffix = 'Complete', length = 50, fill = '█')
        for i,_ in enumerate(items):
            sleep(0.1)
            sixecho.printProgressBar(i + 1, l, prefix = 'Progress:', suffix = 'Complete', length = 50,fill = '█')
        self.assertTrue(True)

    def test_generate(self):
        client = Client()
        client.generate(str="สวัสดีครับ ผมชื่อ กอล์ฟ") 
        self.assertTrue(client.digest().size==128)
        
    def test_jaccard_different(self):
        client = Client()
        client.generate(str="สวัสดีครับ ผมชื่อ กอล์ฟ") 
        client2 = Client()
        client2.generate(str="วันนี้เป็นที่พฤหัสบดี")
        self.assertEqual(0.0,client.min_hash.jaccard(client2.min_hash))

    def test_jaccard_likely(self):
        client = Client()
        client.generate(str="สวัสดีครับ ผมชื่อ กอล์ฟ") 
        client2 = Client()
        client2.generate(str="ผมชื่อแบงก์ I am bank. ไปเที่ยวกันไหม")
        print(client.min_hash.jaccard(client2.min_hash))
        self.assertTrue(client.min_hash.jaccard(client2.min_hash)< 0.5)
    