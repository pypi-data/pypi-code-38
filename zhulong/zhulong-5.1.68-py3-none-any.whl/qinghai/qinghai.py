import json
import time

import pandas as pd
import re

from selenium import webdriver
from bs4 import BeautifulSoup
from lmf.dbv2 import db_write
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException,StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


from zhulong.util.etl import est_tbs, est_meta, est_html, est_gg


# __conp=["postgres","since2015","192.168.3.171","hunan","hengyang"]


# url="http://www.ycsggzy.cn/morelink.html?type=12&index=0"
# driver=webdriver.Chrome()
# driver.maximize_window()
# driver.get(url)

_name_='qinghai'

def f1(driver,num):

    locator = (By.XPATH, '//table[@class="ewb-info-table"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    cnum = driver.find_element_by_xpath('//table[@class="ewb-info-table"]/tbody/tr[1]/td[1]/span').text
    cnum = int(cnum[:-1]) + 1 if cnum != '1' else 1
    if cnum != num:
        val=driver.find_element_by_xpath('//table[@class="ewb-info-table"]/tbody/tr[1]/td[2]/a').get_attribute(
            "href").rsplit('/',maxsplit=1)[1]

        driver.execute_script('''
        
        function getdata(pageindex, pagesize){
        var param = {
        "token":"",//权限参数，索引中的userguid字段值，通过des加密
        "pn":0,//起始行
        "rn":"10",//记录数
        "sdt":"",//开始时间（yyyy-MM-dd HH:mm:ss），搜索日期默认为infodate
        "edt":"",//结束时间（yyyy-MM-dd HH:mm:ss）搜索日期默认为infodate
        "wd":"",//关键词（以空格分隔代表全包含）
        "inc_wd":"",//包含任意关键词
        "exc_wd":"",//不包含关键词
        "fields":"title",//全文检索范围（需要搜索的字段，以";"分隔，不传则搜索无效，返回空）
        "cnum":"",//分类号（以";"分隔，不传默认返回后台配置的所有分类下的数据）
        "sort":'{"showdate":"0"}',//排序规则（hashmap，key:字段，value：0：降序，1：升序）例：{"infodate":"0"}
        "ssort":"title",//匹配度排序（将匹配度最高的字段置顶），此字段传字段名称，如：title
        "cl":200,//返回内容长度
        "terminal":"",//终端类别（0:pc,1:移动端,2:其他）
        "condition":null,//查询条件，所有字段之间都是并且关系，例子如下
        //"condition":'[{"equal":"bid_shandong","equalList":null,"fieldName":"categorynum","notEqual":null,"notEqualList":null}]',
        "time":null,//时间范围（字段名称，开始时间，结束时间）,时间格式yyyy-MM-dd HH:mm:ss
        //"time":'[{"fieldName":"infodate","startTime":"1991-01-01","endTime":"1992-01-01"},{},{}]',
        "highlights":"title",//需要高亮的字段（以";"分隔，不传则默认将fields字段高亮）
        "statistics":null,//统计，默认按照后台索引分类统计，可以指定一个字段统计（这个字段不能有分词）
        "unionCondition":null,//查询条件（所有字段之间都是或者关系）,例子同condition
        "accuracy":"100",//查询内容精确度（0~100整数)，此参数默认为空，关键词匹配方式为and，如果传入1~100的数字，则匹配方式为or
        "noParticiple":"0",//查询关键词不要分词（设置为1则启用，否则不启用）
        "searchRange":null//范围查询，比如某个字段值为10，要查0~20之间的索引，例子如下：
        //"searchRange":''[{"fieldName":"status","start":"0","end":"10"},{},{}]'
        };
        
        var $record = $("#record"),   //数据区域
        $pager = $(".pager"), //分页  
        $cityHtmls = $("#cityHtmls");  //城市id
        var recordTmpl = $("#recordTmpl").html(),   //数据模板
        norecordTmpl = $("#norecordTmpl").html(),   //无数据
        cityTmpl = $("#cityTmpl").html();//城市模板
        var totalRecord = 0;
        var currentCateInfo = $("#hidecate").val();
        var rightCate = ['001001', '001001001', '001002', '001002001', '001004', '001004001', '001005', '001005001'];
        //切换选择分类
        var cnum = '001;002;003;004;005;006;007;008;009;010';
        //初始化加载栏目
        $.ajax({
            url:"/qhztbjson/firstcity.json",
            type:"get",
            dataType: 'json',
            async:false,
            cache:false,
            success:function(data){
                if(data && data.length>0){
                    $cityHtmls.html(Mustache.render(cityTmpl, {records:data}));
                    /* 药品采购去掉子站_continue */
                    var drugPurchasing = window.location.href.split("/")[5];
                    if(drugPurchasing == "001003"){
                        $cityHtmls.find("span").addClass("hidden");
                        $cityHtmls.find("span").eq(0).removeClass("hidden");
                        $cityHtmls.find("span").eq(1).removeClass("hidden");
                        $(".ewb-right-hd").attr("style", "min-height: 116px;");
                    }
                    /* 药品采购去掉子站_continue */
                }
            }
        });
        
        var jyXXSearch = function(pageindex, pagesize) {
            //初始化
            param.wd = '';
            var catenum= $("#hidecate").val();
            var citycode = $("#hidecode").val();
            var wd = $("#projectName").val();
            //分类号
            param.cnum = cnum;
            //关键字搜索
            if(wd.length>0){
                param.wd = wd;
            }else{
                param.wd = '';
                param.isBusiness=1;
            }
            //额外查询条件
            var conditionList = new Array();
            //判断是否加栏目条件
            if(catenum.length>0){
            var conditionCate ={};
                conditionCate["fieldName"]='categorynum';
                conditionCate["isLike"]=true;
                conditionCate["likeType"]=2;
                conditionCate["equal"]=catenum;
                conditionList.push(conditionCate);
            }
            //判断是否加入城市条件
             if(citycode.length>0){
                 var conditionCode = {};
                     conditionCode["fieldName"]='xiaqucode';
                     conditionCode["isLike"]=true;
                     conditionCode["likeType"]=2;
                     conditionCode["equal"]=citycode;
                    conditionList.push(conditionCode);
             }
            param.condition=conditionList;
            param.rn = pagesize || 10;
            param.pn = pageindex*pagesize;
            $record.html('');
            $.ajax({
                url: global.getfulltextdataurl,
                type: 'post',
                dataType: 'json',
                cache:false,
                data: JSON.stringify({"token":param.token,
                    "pn":param.pn,
                    "rn":pagesize,
                    "sdt":param.sdt,
                    "edt":param.edt,
                    "wd":encodeURIComponent(param.wd),
                    "inc_wd":encodeURIComponent(param.inc_wd),
                    "exc_wd":encodeURIComponent(param.exc_wd),
                    "fields":param.fields,
                    "cnum":param.cnum,
                    "sort":param.sort,//字段升序降序排序
                    "ssort":param.ssort,//字段匹配度排序
                    "cl":param.cl,
                    "terminal":param.terminal,
                    "condition":param.condition,
                    "time":param.time,
                    "highlights":param.highlights,
                    "statistics":param.statistics,
                    "unionCondition":param.unionCondition,
                    "accuracy":param.accuracy,
                    "noParticiple":param.noParticiple,
                    "searchRange":param.searchRange,
                    'isBusiness':param.isBusiness
                }),success: function(data) {
                    if (!data) {
                        data = {};
                    } else {
                        data = data.result;
                        for(var item in data.records){
                            if(data.records[item].showdate){
                                data.records[item].date=data.records[item].showdate.substring(0,10);
                            }
                            data.records[item].index = parseInt(param.pn)+parseInt(item)+1;
                        }
                    }
                    renderResult(data);
                    /*if(data.totalcount>500){
                        data.totalcount=490;
                    }*/
                    totalRecord = data.totalcount;
                    renderPager(pageindex, param.rn, totalRecord);
                },error: function(data) {
                    console.log(data);
                    //alert("请求失败");
                }
            });
        };
        
        /* 判断颜色_continue_custom  begin*/
        var hasChange = function(cate, infoList){
            var param = {
                "cate": cate,
                "infoList": infoList.join(","),
                "vname": siteInfo.vname
            }
            $.ajax({
                url: siteInfo.projectName + "/getGuaPaiInfoAction.action?cmd=HasChange",
                type: "get",
                data: param,
                dataType: "json",
                success: function(data){
                    var data = data.custom;
                    console.log(data);
                    for(var i = 0; i < data.length; i++){
                        if(data.charAt(i) == "1"){
                            $("#record").find("tr").eq(i).find("a").attr("style", "color: #f8a65c");
                        }else{
                            $("#record").find("tr").eq(i).find("a").attr("style", "color: #333");
                        }
                    }
                },
                error: function(msg){
                    console.log(msg);
                }
            })
        }
        /* 判断颜色_continue_custom  begin*/
        
        //渲染搜索结果
        var renderResult = function(data) {
            var infoList = new Array();
            var changeJudge = false;
            $("#stringNull").empty();
            $("#record").empty();
            if (data.records && data.records.length > 0) {
                
                /* 去除html标签_continue_custom  begin*/
                String.prototype.stripHTML = function() {
                    var reTag = /<(?:.|\s)*?>/g;
                    return this.replace(reTag,"");
                }
                for(var i = 0; i < data.records.length; i++){
                    data.records[i].titleNoHtml = data.records[i].title.stripHTML();
                    data.records[i].infoguid = data.records[i].id.split("_")[0];
                    infoList[i] =  data.records[i].id.split("_")[0];
                }
                /* 去除html标签_continue_custom  end*/
                
                $record.html(Mustache.render(recordTmpl, data));
                
                /* 判断颜色_continue_custom  begin*/
                $.each(rightCate, function(i, item){
                    if(item == currentCateInfo){
                        changeJudge = true;
                    }
                })
                if(changeJudge){
                    var cate = currentCateInfo.substring(0, 6);
                    if(cate == "001001"){
                        cate = cate + "006";
                    }else if(cate == "001002"){
                        cate = cate + "004";
                    }else if(cate == "001004" || cate == "001005"){
                        cate = cate + "003";
                    }
                    hasChange(cate, infoList);
                }
                /* 判断颜色_continue_custom  end*/
        
                if($("#hidecate").val().trim().length == 9 && $("#hidecate").val().trim().substr($("#hidecate").val().trim().length-3) == "001"){
                    $(".IsZBGG").removeClass("hidden");
                }else{
                    $(".IsZBGG").empty();
                    $(".IsZBGG").addClass("hidden");
                }
                
            } else {
                //$record.html(norecordTmpl);
                $("#stringNull").html(norecordTmpl);
            }
        };
        
        /* 50页之后的信息动态获取_continue_custom  begin*/
        var Custom_Search_InfoShow = function(pageindex, pagesize){
            var area = 0;
            $.each($(".ewb-screen-name"), function(i, item){
                if($(item).hasClass("current")){
                    area = $(item).index();
                }
            })
            $.ajax({
                url: siteInfo.projectName + "/CustomSearchInfoShow.action?cmd=Custom_Search_InfoShow",
                type: "post",
                data: {"cnum": cnum, "front": siteInfo.vname, "area": area, "categoryNum": $("#hidecate").val(), "pageIndex": (pageindex+1), "pageSize": pagesize, "xiaquCode": $("#hidecode").val(), "titleInfo": $("#projectName").val()},
                dataType: "json",
                success: function(data){
                    var data = JSON.parse(data.custom);
                    renderResult(data);
                    renderPager(pageindex, pagesize, data.totalNumBer<totalRecord?data.totalNumBer:totalRecord);
                },
                error: function(msg){
                    console.log(msg);
                }
            })
        } 
        /* 50页之后的信息动态获取_continue_custom  end*/
        
        //渲染分页
        var renderPager = function(pageindex, pagesize, total) {
            if ($pager.pagination()) {
                $pager.pagination('destroy');
            }
            if (!total) {
                return;
            }
            $pager.pagination({
                pageIndex: pageindex,
                pageSize: pagesize,
                total: total,
                showFirstLastBtn:true,
                pageBtnCount:20,
                showJump: false,
                jumpBtnText: 'Go',
                showPageSizes: false
            });
            $pager.on("pageClicked", function(event, data) {
                if(data.pageIndex > 48){
                    Custom_Search_InfoShow(data.pageIndex, data.pageSize);
                }else{
                    jyXXSearch(data.pageIndex, data.pageSize);
                }
            }).on('jumpClicked', function(event, data) {
                jyXXSearch(data.pageIndex, data.pageSize);
            }).on('pageSizeChanged', function(event, data) {
                jyXXSearch(data.pageIndex, data.pageSize);
            });
        };
            
        searchBtn = function (){
            jyXXSearch(0,10);
        }
        
        //地区筛选
        var $screenName = $(".ewb-screen-name");
        $screenName.on('click', function(event) {
            event.preventDefault();
            $screenName.removeClass('current');
            $(this).addClass('current');
            $("#hidecode").val($(this).attr('data-id'));
             cnum = $(this).attr('data-value');
            searchBtn();
        });
        var currentcode = $("#currentcode").val();
        if(currentcode != null && currentcode.length>0 && currentcode != '630000'){
            $cityHtmls.find('[data-id="' +currentcode+ '"]').click();   
        }   
        
        //初始化
        
        //searchBtn();
        if(pageindex<=48){jyXXSearch(pageindex, pagesize);}
        else
        {
        Custom_Search_InfoShow(pageindex, pagesize)  
        
        }
        
        }
        getdata(%s,10)
        
            ''' % (num - 1))

        locator = (By.XPATH, '//table[@class="ewb-info-table"]/tbody/tr[1]/td[2]/a[not(contains(@href,"%s"))]' % val)
        WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
        locator=(By.XPATH,'//table[@class="ewb-info-table"]/tbody/tr[1]/td[1]/span')
        WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element(locator,str(num-1)))


    data = []

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    div = soup.find('table', class_='ewb-info-table').find('tbody')
    lis = div.find_all('tr')

    for li in lis:
        tds = li.find_all('td')
        href = tds[1].a['href']
        name = tds[1].a['title']
        address = tds[2].get_text()
        ggstart_time = tds[3].get_text()

        if 'http' in href:
            href = href
        else:
            href = 'http://www.qhggzyjy.gov.cn' + href
            
        info={"diqu":address}
        info= json.dumps(info,ensure_ascii=False)
        tmp = [name, href, ggstart_time,info]
        data.append(tmp)

    df=pd.DataFrame(data=data)
    
    return df



def f2(driver):


    locator = (By.XPATH, '//table[@class="ewb-info-table"]/tbody/tr[1]/td[2]/a')
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(locator))
    url=driver.current_url
    try:
        page = driver.find_element_by_link_text('尾页').get_attribute('data-page-index')
        total = int(page)+1
        total=total
    except:
        if '001003' in url:
            total=driver.find_element_by_xpath('//div[@class="pager"]/ul/li[last()]').text
            total=int(total)
            total = total
        else:
            raise TimeoutError
    driver.quit()
    return total

def f3(driver, url):

    driver.get(url)

    try:
        locator = (By.XPATH, '//div[@class="ewb-info-content"] | //div[@class="xiangxiyekuang"]')
        WebDriverWait(driver, 10).until(EC.presence_of_all_elements_located(locator))
    except:
        if '404' in driver.title:
            return 404
        else:
            raise TimeoutError

    before = len(driver.page_source)
    time.sleep(0.1)
    after = len(driver.page_source)
    i = 0
    while before != after:
        before = len(driver.page_source)
        time.sleep(0.1)
        after = len(driver.page_source)
        i += 1
        if i > 5: break

    page = driver.page_source

    soup = BeautifulSoup(page, 'html.parser')
    div = soup.find('div', class_="ewb-ca-detail")
    if div == None:
        div = soup.find('div',class_='ewb-ca-detail clearfix')

    div.find('div',class_="xiangxidate").extract()

    return div

data=[

    #包含:变更,招标
    ["gcjs_zhaobiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001001/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_zgys_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001002/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_gqita_da_bian_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001003/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_zhongbiaohx_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001005/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    # ###包含:中标,流标
    ["gcjs_zhongbiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001006/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["gcjs_liubiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001001/001001007/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    # #
    ["zfcg_zhaobiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001002/001002001/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_gqita_da_bian_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001002/001002002/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_zhongbiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001002/001002004/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["zfcg_liubiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001002/001002005/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],

    ["yiliao_zhaobiao_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001003/001003001/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["yiliao_zgysjg_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001003/001003002/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],
    ["yiliao_gqita_gg","http://www.qhggzyjy.gov.cn/ggzy/jyxx/001003/001003003/secondPage.html",[ "name", "href", "ggstart_time","info"],f1,f2],


]

def work(conp,**args):
    est_meta(conp,data=data,diqu="青海省青海",**args)
    est_html(conp,f=f3,**args)


if __name__=='__main__':


    conp=["postgres","since2015","192.168.3.171","qinghai","qinghai"]

    work(conp=conp,num=20)
