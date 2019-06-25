#!/usr/bin/python3
# @Time    : 2019-06-25
# @Author  : Kevin Kong (kfx2007@163.com)

from kaola.comm.comm import Comm

PRODUCT_STATUS = {
    "待提交审核": 1,
    "审核中": 2,
    "审核未通过": 3,
    "待上架(审核已通过)": 4,
    "在售": 5,
    "下架": 6,
    "强制下架": 8,
    "待修改": 9,
}


class Product(Comm):
    """商品类"""

    def publish(self, key_list, outer_id_list=None):
        """
        商品上架
        参数:
        key_list: 需要上架的商品的key的集合
        outer_id_list: 需要上架的外部商品的id集合
        """
        data = {
            "method": "kaola.item.update.listing",
            "key_list": key_list,
            "outer_id_list": outer_id_list
        }
        return self.post(data=data)

    def unpublish(self, key_list, outer_id_list=None):
        """
        商品下架
        参数:
        key_list: 需要上架的商品的key的集合
        outer_id_list: 需要上架的外部商品的id集合
        """
        data = {
            "method": "kaola.item.update.delisting",
            "key_list": key_list,
            "outer_id_list": outer_id_list
        }
        return self.post(data=data)

    def get_product_info(self, key):
        """
        根据商品的key获取商品的详细信息
        """
        data = {
            "key": key,
            "method": "kaola.item.get"
        }
        return self.post(data=data)

    def get_products_infos(self, key_list):
        """
        批量获取商品信息
        """
        data = {
            "key_list": key_list,
            "method": "kaola.item.batch.get"
        }
        return self.post(data=data)

    def get_product_by_status(self, item_edit_status, date_type=None, start_time=None, end_time=None, page_no=1, page_size=20):
        """
        根据状态查询商品信息
        """
        data = {
            "method": "kaola.item.batch.status.get",
            "item_edit_status": item_edit_status,
            "date_type": date_type,
            "start_time": start_time,
            "end_time": end_time,
            "page_no": page_no,
            "page_size": page_size
        }
        return self.post(data=data)

    def update_qty(self, key, stock, sku_outer_id=None):
        """
        更新库存
        参数:
        key:SKU的key
        stock:库存数
        sku_outer_id: outer_sku_id
        """

        data = {
            "method": "kaola.item.sku.stock.update",
            "key": key,
            "stock": stock,
            "sku_outer_id": sku_outer_id
        }

        return self.post(data=data)

    def update_price(self, key, sale_price, sku_outer_id=None):
        """
        更新SKU的售价
        参数:
        key:SKU的key
        sale_price: 售价
        sku_outer_id: outer_sku_id
        """

        data = {
            "method": "kaola.item.sku.sale.price.update",
            "key": key,
            "sale_price": sale_price,
            "sku_outer_id": sku_outer_id
        }

        return self.post(data=data)

    def add_product(self, name, sub_title, short_title, ten_words_desc, item_NO, brand_id, original_country_code_id, category_id,
                    gross_weight, Item_outer_id,
                    description=None,
                    warehouse_id=None, tax_code=None, hs_code=None, express_fee=None, unit_code=None, property_valueId_list=None,
                    text_property_name_id=None, image_urls=None, Sku_market_prices=None, sku_sale_prices=None, sku_barcode=None,
                    sku_stock=None, sku_property_value=None, Sku_outer_id=None):
        """
        新增商品
        """
        data = {
            "method": "kaola.item.addPart",
            "name": name,
            "sub_title": sub_title,
            "short_title": short_title,
            "ten_words_desc": ten_words_desc,
            "item_NO": item_NO,
            "brand_id": brand_id,
            "original_country_code_id": original_country_code_id,
            "category_id": category_id,
            "gross_weight": gross_weight,
            "Item_outer_id": Item_outer_id,
            "description": description,
            "warehouse_id": warehouse_id,
            "tax_code": tax_code,
            "hs_code": hs_code,
            "express_fee": express_fee,
            "unit_code": unit_code,
            "property_valueId_list": property_valueId_list,
            "text_property_name_id": text_property_name_id,
            "image_urls": image_urls,
            "Sku_market_prices": Sku_market_prices,
            "sku_sale_prices": sku_sale_prices,
            "sku_barcode": sku_barcode,
            "sku_stock": sku_stock,
            "sku_property_value": sku_property_value,
            "Sku_outer_id": Sku_outer_id
        }

        return self.post(data=data)

    def udpate_product(self, key, description=None, image_urls=None):
        """
        修改商品
        """
        data = {
            "method": "kaola.item.update",
            "description": description,
            "image_urls": image_urls
        }
        return self.post(data=data)

    def upload_product_image(self, pic):
        """
        上传产品图片
        参数：
        pic: 图片二进制文件
        """
        data = {
            "method": "kaola.item.img.upload",
            "pic": pic
        }
        return self.post(data=data)

    def get_product_image(self, img_path):
        """
        商品图片查询
        """
        data = {
            "method": "kaola.item.img.get",
            "img_path": img_path
        }
        return self.post(data=data)

    def set_cart_hidden(self, key, hide_add_to_cart):
        """
        设置是否隐藏购物车
        """
        data = {
            "method": "kaola.item.hidecart.update",
            "key": key,
            "hide_add_to_cart": hide_add_to_cart
        }
        return self.post(data=data)

    def get_stock_by_keys(self, item_key_list):
        """
        批量查询商品，获取库存信息
        参数：
        item_key_list:商品的key，以逗号分隔；不能超过40个
        """

        data = {
            "method": "kaola.item.getBasicByKeys",
            "item_key_list": item_key_list
        }
        return self.post(data=data)

    def get_stock_by_status(self, start_modified=None, end_modified=None, item_edit_status=None, page_no=1, page_size=20):
        """
        根据商品状态查询商品，获取库存信息
        """

        data = {
            "method": "kaola.item.searchBasicByCondition",
            "start_modified": start_modified,
            "end_modified": end_modified,
            "item_edit_status": item_edit_status,
            "page_no": page_no,
            "page_size": page_size
        }

        return self.post(data=data)

    def get_stock_by_sku(self, sku_key_list):
        """
        根据sku获取库存信息
        """
        data = {
            "method": "kaola.sku.getBasicByKeys",
            "sku_key_list": sku_key_list
        }
        return self.post(data=data)

    def update_outerid(self, field, key, outer_id):
        """
        更新商品outerid
        参数：
        field: 1表示修改商品外键 2 表示修改商品sku 外键 sku_outer_id
        key: item key值
        outer_id: item的outerid 
        """
        data = {
            "method": "kaola.item.outerid.update",
            "field": field,
            "key": key,
            "outer_id": outer_id
        }

        return self.post(data)
