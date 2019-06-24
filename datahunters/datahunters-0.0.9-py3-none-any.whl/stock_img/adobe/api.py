"""API class for adobe stock content.

https://www.adobe.io/apis/creativecloud/stock/docs/getting-started/01-getting-started_master.html
"""

import json
import objectpath
import requests

from datahunters.stock_img.common import StockContent, StockImageAPIBase


class AdobeStockContent(StockContent):
  """Class for adobe stock image.
  """
  category_name = ""


class AdobeStockAPI(StockImageAPIBase):
  """Class for adobe stock api.
  """
  client_id = ""
  client_secret = ""
  headers = {}
  base_url = "https://stock.adobe.io/Rest/"

  def __init__(self, client_id_):
    """Set up client keys.
    """
    self.client_id = client_id_
    self.headers = {
        "X-Product": "MySampleApp/1.0",
        "X-API-Key": self.client_id
    }

  def convert_raw_content(self, raw_content):
    """Convert raw content json to object.
    """
    cur_item = AdobeStockContent()
    cur_item.img_id = str(raw_content["id"])
    cur_item.description = raw_content["description"]
    if not cur_item.description:
      cur_item.description = ""
    cur_item.created_date = raw_content["creation_date"]
    cur_item.full_url = raw_content["comp_url"]
    cur_item.normal_url = raw_content["thumbnail_url"]
    cur_item.link = raw_content["details_url"]
    cur_item.title = raw_content["title"]
    cur_item.category_name = objectpath.Tree(raw_content).execute(
        "$.category.name")
    return cur_item

  def form_result_req_str(self, field_names):
    """Form total string for requested fields.
    """
    total_str = ""
    for field_name in field_names:
      total_str = "{}&result_columns[]={}".format(total_str, field_name)
    # always start with '&'.
    return total_str

  def get_imgs(self, start_page=-1):
    """Get images from the whole catalog.
    """
    if start_page == -1:
      start_page = 0
    return self.search_imgs("", start_page)

  def search_imgs(self, keywords, start_page=0):
    """Search adobe stock images.
    """
    items_per_page = 64
    offset = items_per_page * start_page
    total_num = -1
    req_fields = [
        "nb_results", "id", "stock_id", "title", "width", "height",
        "thumbnail_url", "category", "creation_date", "comp_url",
        "content_type", "details_url", "description"
    ]
    while True:
      try:
        # TODO(jiefeng): add detailed results via result column.
        req_url = "{}Media/1/Search/Files?locale=en_US&search_parameters[limit]=64&search_parameters[words]={}&search_parameters[offset]={}".format(
            self.base_url, keywords, offset)
        req_url += self.form_result_req_str(req_fields)
        raw_res = requests.get(req_url, headers=self.headers)
        res_json = raw_res.json()
        if total_num == -1:
          total_num = res_json["nb_results"]
        # process results.
        res_items = res_json["files"]
        for item in res_items:
          try:
            cur_content_obj = self.convert_raw_content(item)
            yield cur_content_obj
          except Exception as ex:
            print("error converting adobe item: {}. raw item: {}".format(
                ex, item))
            continue
        # ready for next page.
        offset += len(res_items)
        if offset >= total_num:
          break
      except Exception as ex:
        print("error processing get_imgs: {}".format(ex))
