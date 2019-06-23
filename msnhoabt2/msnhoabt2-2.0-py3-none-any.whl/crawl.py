import scrapy
from scrapy.crawler import CrawlerProcess
import textwrap
import os
import json
import media_helper as mediah
import draw_helper as draw
import shutil
import uuid


class MSNSpider(scrapy.Spider):
    name = "MSNSpider"
    parent_path="/var/msn"
    bg_sound_path="/var/msn/bg/01.wav"
    outro_path="/var/msn/bg/s45iJEcUZKI.avi"
    output="/var/msn/tmp/x1.avi"
    max_text_read=190
    wrap_text_len=70
    tl="vi"
    def parse(self, response):
        tmp_path = os.path.join(self.parent_path, "tmp")
        font_file = os.path.join(self.parent_path, "fonts/Arial-Unicode-Bold.ttf")
        self.max_text_read=int(self.max_text_read)
        self.wrap_text_len=int(self.wrap_text_len)
        if not os.path.exists(tmp_path):
            os.mkdir(tmp_path)
        arr_imageT = response.xpath('//div[@id="maincontent"]//span/img/@data-src').extract()
        arr_image = []
        for imageT in arr_imageT:
            imgObj = json.loads(imageT)
            arr_image.append(mediah.makefullhd("http:"+imgObj['default']['src'],tmp_path))

        arr_text = response.xpath('//div[@id="maincontent"]//p[not (descendant::img or descendant::a)]').extract()
        draw.nomalize_text(arr_text,self.max_text_read)
        draw.balance_image(arr_image, arr_text)
        i=0
        arr_vid=[]
        while(i<len(arr_image)):
            img_source=arr_image[i]
            text_input=arr_text[i]
            if text_input==None or text_input =="":
                soundI = mediah.make_sound_null(6,tmp_path)
            else:
                img_source = draw.content(arr_image[i], text_input,font_file,tmp_path,self.wrap_text_len)
                textTran=";;".join(textwrap.wrap(text_input.replace("\"","\\\""),self.max_text_read))
                soundI = os.popen("php trans.php --tmp=\""+tmp_path+"\" --text=\"" + textTran + "\" --tl="+self.tl).read()
                soundI=mediah.speedup_sound(soundI,tmp_path)
                duration = mediah.duration(soundI)
                if (duration < 1):
                    soundI = mediah.make_sound_null(6,tmp_path)
            arr_vid.append(mediah.makevid(img_source,soundI,tmp_path))
            i+=1
        for img in arr_image:
            try:
                os.remove(img)
            except:
                pass
        if self.outro_path !="None":
            new_outro_path=tmp_path+"/"+uuid.uuid4().hex +".avi"
            shutil.copyfile(self.outro_path, new_outro_path)
            arr_vid.append(new_outro_path)
        mediah.mergvid(arr_vid,tmp_path,self.output)
        #mediah.mix_sound_bg(merged_vid,self.bg_sound_path,tmp_path,self.output)

def run(tl,parent_path,outro_path,start_urls,output,max_text_read,wrap_text_len,log_enabled=False):
    process = CrawlerProcess({
        'USER_AGENT': 'Googlebot-News',
        'LOG_ENABLED':log_enabled
    })
    #process.crawl(MSNSpider,bg_sound_path="D:/Developer/Python/reup/msn/bg/01.wav",parent_path="D:/Developer/Python/reup/msn", start_urls=["https://www.msn.com/vi-vn/entertainment/news/v%C3%AC-sao-ng%E1%BB%8Dc-trinh-kh%C3%B4ng-%C4%91%C3%B3ng-phim-v%E1%BA%ABn-c%C3%B3-m%E1%BA%B7t-g%C3%A2y-b%C3%A3o-th%E1%BA%A3m-%C4%91%E1%BB%8F-lhp-cannes/ar-AABD8AV"])
    process.crawl(MSNSpider,outro_path=outro_path,parent_path=parent_path,start_urls=start_urls,output=output,tl=tl,max_text_read=max_text_read,wrap_text_len=wrap_text_len)
    process.start()