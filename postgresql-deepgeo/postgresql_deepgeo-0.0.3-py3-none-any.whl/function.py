import shutil
import http.client as httplib
import json, os

def url_parse(url):
    domain = url.split("/")[0]
    get = url.split(domain)[-1]
    return domain, get

def get_page(protocol, domain, get):
    conn = None
    if protocol == "https":
        conn = httplib.HTTPSConnection(domain)
    elif protocol == "http":
        conn = httplib.HTTPConnection(domain)
    if conn is not None:
        conn.request("GET", get)
        page = conn.getresponse()
        return page.read()
    else:
        return None

def download_file(url, to_file):
    protocol = url.split("://")
    ext_list = ['json','h5','weights']
    file_ext = url.split(".")[-1]
    assert file_ext in ext_list, "지원하지 않은 확장명입니다."
    
    if protocol[0] in ['http','https']:
        domain, get = url_parse(protocol[1])
        page = get_page(protocol[0], domain, get)
        assert page is not None, "잘못된 URI 입니다."
        
        fail = open(to_file, "wb")
        fail.write(page)
        fail.close()
        r_url = to_file

    elif protocol[0] == 'file' :
        try:
            shutil.copy(protocol[1], to_file)
            r_url = to_file
        except Exception as e:
            print(str(e) + " Error")
            r_url = None
            assert r_url is not None, "파일을 복사할 수 없습니다."
    else:
        r_url = url
    assert r_url is not None, "잘못된 경로 입니다."

    return r_url

def json_to_string(file):
    with open(file) as json_file:
        return json.load(json_file)

def download_weights(config):
    path = config['MODEL_PATH']+config['MODEL_FILE_NAME']
    if os.path.isfile(path) is False:
        download_file(config['MODEL_URI'],path)
    return path

def delete_weights(config):
    path = config['MODEL_PATH']+config['MODEL_FILE_NAME']
    if os.path.isfile(path):
        os.remove(path)

def engine_model_update(engine, model_table, rtype=True):
    try:
        model_name_list = {}
        engine_model_list = engine.get_model_list()

        # 테이블에서 이름데이터만 추출합니다.
        for row in model_table:
            model_name_list.update({row['name']:[row['engine'],json.loads(row['config'])]})

        for key in engine_model_list:
            if not key in list(model_name_list.keys()):
                engine.delete_model(key)
                delete_weights(model_name_list[key][1])
            else:
                del model_name_list[key]

        for key in model_name_list:
            download_weights(model_name_list[key][1])
            engine.add_model(key,model_name_list[key][0], model_name_list[key][1])
    except Exception as e:
        if rtype is True:
            return False
        else:
            return e
    if rtype is True:
        return True
    else:
        return "True"

