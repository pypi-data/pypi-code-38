import json
import os

from news2play.web_downloader.down_index import DownIndex
from news2play.web_downloader.downloader import NewDownloader
from news2play.web_downloader.ts_tools import Tool


# def getEST():
#     ts = datetime.now()
#     est = ts.astimezone(timezone('US/Eastern'))
#     f_date = est.strftime('%Y%m%d')
#     return f_date
#
#
# def chooseFolder(base=os.path.join("..", "storage")):
#     current = getEST()
#     path = os.path.join(base, current)
#     if not os.path.exists(path):
#         os.makedirs(path)
#     return path


def main():
    path = Tool().choose_folder()
    url_list = DownIndex().get_url()
    nd = NewDownloader(path=path)
    return [nd.parse_news(i) for i in url_list]


def load_news(path):
    url_list = DownIndex().get_url()
    news_loader = NewDownloader(path=path)

    return [news_loader.parse_news(item) for item in url_list]


if __name__ == "__main__":
    ts = Tool()
    result = main()
    folder = ts.choose_folder()
    file_path = os.path.join(folder, "meta.json")
    with open(file_path, "w", encoding="utf-8")as f:
        f.write(json.dumps(result, indent=2))
