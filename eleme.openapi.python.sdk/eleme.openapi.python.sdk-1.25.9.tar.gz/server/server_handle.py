# -*- coding: utf-8 -*-

import json
import uuid
from sdk.util.callback_signature_util import CallbackValidationUtil
from sdk.oauth.oauth_client import OAuthClient
from sdk.config import Config
from sdk.protocol.rpc_client import RpcClient
from cgi import parse_qs, escape
from server.global_config import Global
demo_html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>欢迎使用智能配送助手</title>
  <script src="https://static11.elemecdn.com/eleme/napos.order.fe.melody/jssdk.js" type="text/javascript" charset="utf-8"></script>
</head>
<body>
  <div class="w1000">
    <div class="userinfo">
      <p>当前登录用户ID为<span id="userId">{{ userId }}</span></p>
      <p>当前店铺名称为<span id="shopName">{{ shopName }}</span></p>
    </div>
    <div class="icon-box">
      <img src="https://fuss10.elemecdn.com/4/e7/225b8c9ae6b02c10de010b00f9504png.png" alt="">
      </br>
      智能配送助手
    </div>
    <dl>
      <dt>【智能配送助手】由【饿了么】进行开发</dt>
      <dd>
        饿了么商家开放平台作为一个服务集成平台，致力于满足商户的多样需求，提供合作伙伴更多的平台资源，服务商户接入，提供给商户更丰富的经营能力。同时，开放平台将通过提供一系列非业务性的，例如安全保障、服务监控告警、日志分析统计等解决方案，让开发者专注于业务系统的开发，降低接入者的开发成本。
      </dd>
    </dl>
  </div>

  <style>
    dt,dd{
      margin: 0;
    }
    .w1000{
      width: 1000px;
      margin: 0 auto;
      display: none
    }
    .userinfo{
      text-align: center;
    }
    .icon-box{
      text-align: center;
    }
    .icon-box img{
      width: 200px;
      height: 200px;
    }
  </style>
</body>
<script>
  function post(url, param) {
    return new Promise(function(resolve, reject) {
      var xhr = new XMLHttpRequest()
      xhr.open('POST',url, true)
      xhr.onreadystatechange = function() {
        if (xhr.readyState === 4) {
          if (xhr.status === 200 || xhr.status === 1223) {
            // 这边双方约定返回json字符串
            var response = JSON.parse(xhr.responseText)
            if (response.error) {
              reject(response.error)
            } else {
              resolve(response.result)
            }
          }
        }
      }
      xhr.setRequestHeader('content-type', 'application/json')
      xhr.send(JSON.stringify(param))
    })
  }

  // 整理search成对象
  function formatSearch(search) {
    var result = {}
    if (search === '') {
      return result
    }
    // delte ?
    search = search.substring(1)
    // 将?key=value 拆分成 {key: value}的形式
    search.split('&').forEach(function(item) {
      var searchArray = item.split('=')
      result[searchArray[0]] = searchArray[1]
    })
    return result

  }

  function codeCallback() {
    document.querySelector('.w1000').style.display = 'block'
  }

  function showErrorMessage(mes) {
    var h1 = document.createElement('h1')
    h1.style.textAlign = 'center'
    h1.textContent = mes
    document.body.appendChild(h1)
  }

  function errorCallBack(searchParam) {
    var errorText = decodeURI(searchParam.error_description || '授权失败')
    showErrorMessage(errorText)
  }


  function normalCallBack() {
    // 必须在客户端打开
    if (!eleme.userAgent.isClient) {
      showErrorMessage('请在napos客户端打开')
    } else {
      Promise.all([
        eleme.getUserId(),
        eleme.getCurrentShopId()
      ]).then(function (result) {
        var userId = result[0]
        var shopId = result[1]
        post('/getInfo', {
          userId: userId,
          shopId: shopId
        }).then(result => {
          if (result.OAuthUrl) {
            location.href = result.OAuthUrl
          } else {
            var shopName = result.shopName
            document.querySelector('#userId').innerHTML = userId
            document.querySelector('#shopName').innerHTML = shopName
            document.querySelector('.w1000').style.display = 'block'
          }
        }).catch(e => {
           showErrorMessage(e)
        })
      })
    }
  }

  window.onload = function() {
    var content = document.querySelector('.w1000')
    var search = window.location.search
    var searchParam = formatSearch(search)
    // 假如有code，则是后端渲染
    if (searchParam.code) {
      codeCallback()
    } else if (searchParam.error) {
      errorCallBack(searchParam)
    } else {
      normalCallBack()
    }
  }
</script>
</html>
"""



def application(environ, start_response):
    method = environ['REQUEST_METHOD']
    path = environ['PATH_INFO']
    if method == 'GET' and path == '/listenMessage':
        return ping(environ, start_response)
    elif method == 'POST' and path == '/listenMessage':
        return process_message(environ, start_response)
    elif method == 'GET' and path == '/callback':
        return callback(environ, start_response)
    elif method == 'POST' and path == '/getInfo':
        return get_user_info(environ, start_response)
    else:
        start_response('404 Not Found', [('Content-Type', 'text/html; charset=utf-8')])
        return [b'<h1>404 Not Found</h1>']


def ping(environ, start_response):
    Global.log.info('ping...')
    start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
    return ['{"message":"ok"}'.encode('utf-8')]


def process_message(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
    response = None
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        response = '{"message":"params error"}'
    request_body = environ['wsgi.input'].read(request_body_size)
    Global.log.info('receive eleme message :{}'.format(request_body))
    if not CallbackValidationUtil.is_valid_message(request_body):
        response = '{"message":"invalid signature"}'
    else:
        response = '{"message":"ok"}'
        try:
            eleme_message = json.loads(request_body)
            if (int(eleme_message['messageType']) == 10):
                order_id = eleme_message['order_id']
                config = Config(Global.get_env(), Global.get_app_key(), Global.get_secret(), Global.get_callback_url())
                oauth_client = OAuthClient(config)
                response = oauth_client.get_token_in_client_credentials()
                token = json.loads(response)['access_token']
                rpc_client = RpcClient(Config, token)
                rpc_client.call("eleme.order.confirmOrder", {"orderId": order_id})
        except Exception as e:
            Global.log.error('confirm order error :{}'.format(e.message))
        Global.log.info('myserver response:{}'.format(request_body))
    return [response.encode('utf-8')]


def callback(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    query_string = parse_qs(environ['QUERY_STRING'])
    if not query_string:
        return [demo_html_content.encode('utf-8')]
    auth_code = query_string.get('code', [''])[0]
    if auth_code:
        config = Config(Global.get_env(), Global.get_app_key(), Global.get_secret(), Global.get_callback_url())
        oauth_client = OAuthClient(config)
        response = oauth_client.get_token_by_auth_code(auth_code)
        #response = oauth_client.get_token_in_client_credentials()
        token = json.loads(response)['access_token']
        rpc_client = RpcClient(Config, token)
        user_info = rpc_client.call("eleme.user.getUser", {})
        user_id = user_info['userId']
        f = open("mapping.txt", "a")
        f.write(str(user_id)+":"+token+'\n')
        f.close()
        response_body = demo_html_content % (user_id, user_info['authorizedShops'][0]['id'])
        return [response_body.encode('utf-8')]
    else:
        return [demo_html_content.encode('utf-8')]


def get_user_info(environ, start_response):
    start_response('200 OK', [('Content-Type', 'application/json; charset=utf-8')])
    try:
        request_body_size = int(environ.get('CONTENT_LENGTH', 0))
    except (ValueError):
        return ['{"message":"params error"}'.encode('utf-8')]
    request_body = environ['wsgi.input'].read(request_body_size)
    print(request_body)
    result = {}
    params = json.loads(request_body)
    user_id = params['userId']
    shop_id = params['shopId']
    file = open("mapping.txt", "r")
    while 1:
        line = file.readline()
        if not line:
            config = Config(Global.get_env(), Global.get_app_key(), Global.get_secret(), Global.get_callback_url())
            oauth_client = OAuthClient(config)
            auth_url = oauth_client.get_auth_url(str(uuid.uuid4()), 'all')
            result['authUrl'] = auth_url
            return [result.encode('utf-8')]
        if user_id == line.split(':')[0]:
            token = line.split(':')[1]
            rpc_client = RpcClient(token)
            user_info = rpc_client.call("eleme.user.getUser", {})
            result['userInfo'] = user_info
            authorized_shops = user_info['authorizedShops']
            for shop in authorized_shops:
                if shop['id'] == int(shop_id):
                    shop_info = rpc_client.call("eleme.shop.getShop", {"shopId": int(shop_id)})
                    result['shopInfo'] = shop_info
                    return [result.encode('utf-8')]
    return [result.encode('utf-8')]