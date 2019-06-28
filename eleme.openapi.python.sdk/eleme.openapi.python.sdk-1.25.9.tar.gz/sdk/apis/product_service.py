# -*- coding: utf-8 -*-


# 商品服务
class ProductService:

    __client = None

    def __init__(self, client):
        self.__client = client

    def upload_image(self, image):
        """
        上传图片，返回图片的hash值
        :param image:文件内容base64编码值
        """
        return self.__client.call("eleme.file.uploadImage", {"image": image})

    def upload_image_with_remote_url(self, url):
        """
        通过远程URL上传图片，返回图片的hash值
        :param url:远程Url地址
        """
        return self.__client.call("eleme.file.uploadImageWithRemoteUrl", {"url": url})

    def get_uploaded_url(self, hash):
        """
        获取上传文件的访问URL，返回文件的Url地址
        :param hash:图片hash值
        """
        return self.__client.call("eleme.file.getUploadedUrl", {"hash": hash})

    def get_image_url(self, hash):
        """
        获取上传图片的url地址(新版)
        :param hash:图片hash值
        """
        return self.__client.call("eleme.file.getImageUrl", {"hash": hash})

    def get_items_by_category_id(self, category_id):
        """
        获取一个分类下的所有商品
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.item.getItemsByCategoryId", {"categoryId": category_id})

    def get_item(self, item_id):
        """
        查询商品详情
        :param itemId:商品Id
        """
        return self.__client.call("eleme.product.item.getItem", {"itemId": item_id})

    def batch_get_items(self, item_ids):
        """
        批量查询商品详情
        :param itemIds:商品Id的列表
        """
        return self.__client.call("eleme.product.item.batchGetItems", {"itemIds": item_ids})

    def create_item(self, category_id, properties):
        """
        添加商品
        :param categoryId:商品分类Id
        :param properties:商品属性
        """
        return self.__client.call("eleme.product.item.createItem", {"categoryId": category_id, "properties": properties})

    def batch_create_items(self, category_id, items):
        """
        批量添加商品
        :param categoryId:商品分类Id
        :param items:商品属性的列表
        """
        return self.__client.call("eleme.product.item.batchCreateItems", {"categoryId": category_id, "items": items})

    def batch_create_items_ignore_error(self, category_id, items):
        """
        批量添加商品,且忽略异常,专为星巴克开发
        :param categoryId:商品分类Id
        :param items:商品属性的列表
        """
        return self.__client.call("eleme.product.item.batchCreateItemsIgnoreError", {"categoryId": category_id, "items": items})

    def update_item(self, item_id, category_id, properties):
        """
        更新商品
        :param itemId:商品Id
        :param categoryId:商品分类Id
        :param properties:商品属性
        """
        return self.__client.call("eleme.product.item.updateItem", {"itemId": item_id, "categoryId": category_id, "properties": properties})

    def batch_fill_stock(self, spec_ids):
        """
        批量置满库存
        :param specIds:商品及商品规格的列表
        """
        return self.__client.call("eleme.product.item.batchFillStock", {"specIds": spec_ids})

    def batch_clear_stock(self, spec_ids):
        """
        批量沽清库存
        :param specIds:商品及商品规格的列表
        """
        return self.__client.call("eleme.product.item.batchClearStock", {"specIds": spec_ids})

    def batch_on_shelf(self, spec_ids):
        """
        批量上架商品
        :param specIds:商品及商品规格的列表
        """
        return self.__client.call("eleme.product.item.batchOnShelf", {"specIds": spec_ids})

    def batch_list_items(self, item_ids):
        """
        批量上架商品(新版)
        :param itemIds:商品ID列表
        """
        return self.__client.call("eleme.product.item.batchListItems", {"itemIds": item_ids})

    def batch_off_shelf(self, spec_ids):
        """
        批量下架商品
        :param specIds:商品及商品规格的列表
        """
        return self.__client.call("eleme.product.item.batchOffShelf", {"specIds": spec_ids})

    def batch_delist_items(self, item_ids):
        """
        批量下架商品(新版)
        :param itemIds:商品ID列表
        """
        return self.__client.call("eleme.product.item.batchDelistItems", {"itemIds": item_ids})

    def remove_item(self, item_id):
        """
        删除商品
        :param itemId:商品Id
        """
        return self.__client.call("eleme.product.item.removeItem", {"itemId": item_id})

    def invalid_item(self, item_id):
        """
        删除商品(新版)
        :param itemId:商品Id
        """
        return self.__client.call("eleme.product.item.invalidItem", {"itemId": item_id})

    def batch_remove_items(self, item_ids):
        """
        批量删除商品
        :param itemIds:商品Id的列表
        """
        return self.__client.call("eleme.product.item.batchRemoveItems", {"itemIds": item_ids})

    def batch_update_spec_stocks(self, spec_stocks):
        """
        批量更新商品库存
        :param specStocks:商品以及规格库存列表
        """
        return self.__client.call("eleme.product.item.batchUpdateSpecStocks", {"specStocks": spec_stocks})

    def batch_update_stock(self, stock_map):
        """
        批量更新商品库存(新版)
        :param stockMap:商品规格ID和库存设值的映射
        """
        return self.__client.call("eleme.product.item.batchUpdateStock", {"stockMap": stock_map})

    def set_item_positions(self, category_id, item_ids):
        """
        设置商品排序
        :param categoryId:商品分类Id
        :param itemIds:商品Id列表
        """
        return self.__client.call("eleme.product.item.setItemPositions", {"categoryId": category_id, "itemIds": item_ids})

    def clear_and_timing_max_stock(self, clear_stocks):
        """
        批量沽清库存并在次日2:00开始置满
        :param clearStocks:店铺Id及商品Id的列表
        """
        return self.__client.call("eleme.product.item.clearAndTimingMaxStock", {"clearStocks": clear_stocks})

    def get_item_by_shop_id_and_extend_code(self, shop_id, extend_code):
        """
        根据商品扩展码获取商品
        :param shopId:店铺Id
        :param extendCode:商品扩展码
        """
        return self.__client.call("eleme.product.item.getItemByShopIdAndExtendCode", {"shopId": shop_id, "extendCode": extend_code})

    def get_items_by_shop_id_and_bar_code(self, shop_id, bar_code):
        """
        根据商品条形码获取商品
        :param shopId:店铺Id
        :param barCode:商品条形码
        """
        return self.__client.call("eleme.product.item.getItemsByShopIdAndBarCode", {"shopId": shop_id, "barCode": bar_code})

    def batch_update_prices(self, shop_id, spec_prices):
        """
        批量修改商品价格
        :param shopId:店铺Id
        :param specPrices:商品Id及其下SkuId和价格对应Map(限制最多50个)
        """
        return self.__client.call("eleme.product.item.batchUpdatePrices", {"shopId": shop_id, "specPrices": spec_prices})

    def get_item_ids_has_activity_by_shop_id(self, shop_id):
        """
        查询活动商品
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.product.item.getItemIdsHasActivityByShopId", {"shopId": shop_id})

    def get_shop_sales_items(self, shop_id):
        """
        查询店铺活动商品(新版)
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.product.item.getShopSalesItems", {"shopId": shop_id})

    def set_order_packing_fee(self, shop_id, status, packing_fee):
        """
        设置订单餐盒费
        :param shopId: 店铺ID
        :param status:是否按照订单设置餐盒费
        :param packingFee:订单餐盒费费用
        """
        return self.__client.call("eleme.product.item.setOrderPackingFee", {"shopId": shop_id, "status": status, "packingFee": packing_fee})

    def query_item_by_page(self, query_page):
        """
        分页获取店铺下的商品
        :param queryPage:分页查询参数
        """
        return self.__client.call("eleme.product.item.queryItemByPage", {"queryPage": query_page})

    def get_material_tree(self, shop_id):
        """
        获取原材料树
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.product.item.getMaterialTree", {"shopId": shop_id})

    def set_ingredient(self, shop_id, main_item_id, ingredient_group):
        """
        主料关联配料
        :param shopId:店铺ID
        :param mainItemId:主料ID（商品ID）
        :param ingredientGroup: 商品配料分组
        """
        return self.__client.call("eleme.product.item.setIngredient", {"shopId": shop_id, "mainItemId": main_item_id, "ingredientGroup": ingredient_group})

    def remove_ingredient(self, shop_id, main_item_id):
        """
        删除配料
        :param shopId:店铺ID
        :param mainItemId:主料ID（商品ID）
        """
        return self.__client.call("eleme.product.item.removeIngredient", {"shopId": shop_id, "mainItemId": main_item_id})

    def set_related_item_ids(self, shop_id, item_id, related_item_ids):
        """
        针对主菜itemId设置菜品推荐
        :param shopId:店铺ID
        :param itemId:商品ID
        :param relatedItemIds:关联的商品ID
        """
        return self.__client.call("eleme.product.item.setRelatedItemIds", {"shopId": shop_id, "itemId": item_id, "relatedItemIds": related_item_ids})

    def display_related_item_ids(self, shop_id, item_id, display):
        """
        对主菜itemId设置是否开启菜品推荐
        :param shopId:店铺ID
        :param itemId:商品ID
        :param display:是否展示
        """
        return self.__client.call("eleme.product.item.displayRelatedItemIds", {"shopId": shop_id, "itemId": item_id, "display": display})

    def get_related_item_ids(self, shop_id, item_id):
        """
        针对主菜itemId查询菜品推荐
        :param shopId:店铺ID
        :param itemId:商品ID
        """
        return self.__client.call("eleme.product.item.getRelatedItemIds", {"shopId": shop_id, "itemId": item_id})

    def create_multi_spec_item(self, category_id, properties):
        """
        添加多规格商品
        :param categoryId:商品分类Id
        :param properties:商品属性
        """
        return self.__client.call("eleme.product.item.createMultiSpecItem", {"categoryId": category_id, "properties": properties})

    def batch_create_multi_spec_item(self, category_id, items):
        """
        批量添加多规格商品
        :param categoryId:商品分类Id
        :param items:商品属性的列表
        """
        return self.__client.call("eleme.product.item.batchCreateMultiSpecItem", {"categoryId": category_id, "items": items})

    def update_multi_spec_item(self, item_id, category_id, properties):
        """
        更新多规格商品
        :param itemId:商品Id
        :param categoryId:商品分类Id
        :param properties:商品属性
        """
        return self.__client.call("eleme.product.item.updateMultiSpecItem", {"itemId": item_id, "categoryId": category_id, "properties": properties})

    def set_ingredient_group(self, item_id, group_relations):
        """
        设置配料组数据
        :param itemId:商品Id
        :param groupRelations:配料组信息
        """
        return self.__client.call("eleme.product.item.setIngredientGroup", {"itemId": item_id, "groupRelations": group_relations})

    def remove_ingredient_group(self, item_id):
        """
        删除配料组数据
        :param itemId:商品Id
        """
        return self.__client.call("eleme.product.item.removeIngredientGroup", {"itemId": item_id})

    def get_item_material_tree(self, shop_id):
        """
        获取商品原材料数据(新版)
        :param shopId:店铺ID
        """
        return self.__client.call("eleme.product.item.getItemMaterialTree", {"shopId": shop_id})

    def get_shop_categories(self, shop_id):
        """
        查询店铺商品分类
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.product.category.getShopCategories", {"shopId": shop_id})

    def get_shop_categories_with_children(self, shop_id):
        """
        查询店铺商品分类，包含二级分类
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.product.category.getShopCategoriesWithChildren", {"shopId": shop_id})

    def get_category(self, category_id):
        """
        查询商品分类详情
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.category.getCategory", {"categoryId": category_id})

    def get_category_with_children(self, category_id):
        """
        查询商品分类详情，包含二级分类
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.category.getCategoryWithChildren", {"categoryId": category_id})

    def create_category(self, shop_id, name, description):
        """
        添加商品分类
        :param shopId:店铺Id
        :param name:商品分类名称，长度需在50字以内
        :param description:商品分类描述，长度需在50字以内
        """
        return self.__client.call("eleme.product.category.createCategory", {"shopId": shop_id, "name": name, "description": description})

    def create_category_with_children(self, shop_id, name, parent_id, description):
        """
        添加商品分类，支持二级分类
        :param shopId:店铺Id
        :param name:商品分类名称，长度需在50字以内
        :param parentId:父分类ID，如果没有可以填0
        :param description:商品分类描述，长度需在50字以内
        """
        return self.__client.call("eleme.product.category.createCategoryWithChildren", {"shopId": shop_id, "name": name, "parentId": parent_id, "description": description})

    def update_category(self, category_id, name, description):
        """
        更新商品分类
        :param categoryId:商品分类Id
        :param name:商品分类名称，长度需在50字以内
        :param description:商品分类描述，长度需在50字以内
        """
        return self.__client.call("eleme.product.category.updateCategory", {"categoryId": category_id, "name": name, "description": description})

    def update_category_with_children(self, category_id, name, parent_id, description):
        """
        更新商品分类，包含二级分类
        :param categoryId:商品分类Id
        :param name:商品分类名称，长度需在50字以内
        :param parentId:父分类ID，如果没有可以填0
        :param description:商品分类描述，长度需在50字以内
        """
        return self.__client.call("eleme.product.category.updateCategoryWithChildren", {"categoryId": category_id, "name": name, "parentId": parent_id, "description": description})

    def remove_category(self, category_id):
        """
        删除商品分类
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.category.removeCategory", {"categoryId": category_id})

    def invalid_category(self, category_id):
        """
        删除商品分类(新版)
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.category.invalidCategory", {"categoryId": category_id})

    def set_category_positions(self, shop_id, category_ids):
        """
        设置分类排序
        :param shopId:饿了么店铺Id
        :param categoryIds:需要排序的分类Id
        """
        return self.__client.call("eleme.product.category.setCategoryPositions", {"shopId": shop_id, "categoryIds": category_ids})

    def set_category_sequence(self, shop_id, category_ids):
        """
        设置分类排序(新版)
        :param shopId:饿了么店铺Id
        :param categoryIds:需要排序的全部一级分类Id
        """
        return self.__client.call("eleme.product.category.setCategorySequence", {"shopId": shop_id, "categoryIds": category_ids})

    def set_category_positions_with_children(self, shop_id, category_with_children_ids):
        """
        设置二级分类排序
        :param shopId:饿了么店铺Id
        :param categoryWithChildrenIds:需要排序的父分类Id，及其下属的二级分类ID
        """
        return self.__client.call("eleme.product.category.setCategoryPositionsWithChildren", {"shopId": shop_id, "categoryWithChildrenIds": category_with_children_ids})

    def get_back_category(self, shop_id):
        """
        查询商品后台类目
        :param shopId:店铺Id
        """
        return self.__client.call("eleme.product.category.getBackCategory", {"shopId": shop_id})

    def set_category_type(self, shop_id, category_id, category_type):
        """
        设置分类类型
        :param shopId:店铺Id
        :param categoryId:商品分类Id
        :param categoryType:分类类型
        """
        return self.__client.call("eleme.product.category.setCategoryType", {"shopId": shop_id, "categoryId": category_id, "categoryType": category_type})

    def set_day_parting_stick_time(self, shop_id, category_id, day_parting_stick):
        """
        设置分组分时段置顶
        :param shopId:店铺Id
        :param categoryId:商品分类Id
        :param dayPartingStick:置顶时间设置
        """
        return self.__client.call("eleme.product.category.setDayPartingStickTime", {"shopId": shop_id, "categoryId": category_id, "dayPartingStick": day_parting_stick})

    def remove_day_parting_stick_time(self, shop_id, category_id):
        """
        删除分组的分时置顶功能
        :param shopId:店铺Id
        :param categoryId:商品分类Id
        """
        return self.__client.call("eleme.product.category.removeDayPartingStickTime", {"shopId": shop_id, "categoryId": category_id})

    def create_package(self, category_id, o_package):
        """
        添加套餐
        :param categoryId:分类Id
        :param oPackage:套餐属性
        """
        return self.__client.call("eleme.product.package.createPackage", {"categoryId": category_id, "oPackage": o_package})

    def update_package_content(self, item_id, category_id, update):
        """
        修改套餐基本信息
        :param itemId:新套餐id即OItem中的商品Id
        :param categoryId:分类Id即OCategory中的分类Id
        :param update:套餐基本信息
        """
        return self.__client.call("eleme.product.package.updatePackageContent", {"itemId": item_id, "categoryId": category_id, "update": update})

    def update_package_relation(self, item_id, packages):
        """
        修改套餐和主料的关联关系
        :param itemId:新套餐id即OItem中的商品Id
        :param packages:套餐关系
        """
        return self.__client.call("eleme.product.package.updatePackageRelation", {"itemId": item_id, "packages": packages})

    def remove_package(self, item_id):
        """
        删除套餐
        :param itemId:套餐Id
        """
        return self.__client.call("eleme.product.package.removePackage", {"itemId": item_id})

    def get_relation_by_pid(self, p_id):
        """
        查询连锁总店商品规格关联的单店商品规格信息
        :param pId:连锁总店商品规格Id
        """
        return self.__client.call("eleme.product.chain.pid.getRelationByPid", {"pId": p_id})

    def set_pid(self, p_id, spec_id):
        """
        设置连锁总店商品规格与单店商品规格关系
        :param pId:连锁总店商品规格Id
        :param specId:子店商品规格Id
        """
        return self.__client.call("eleme.product.chain.pid.setPid", {"pId": p_id, "specId": spec_id})

    def batch_set_pid(self, p_id, spec_ids):
        """
        批量设置连锁总店商品规格与单店商品规格关系
        :param pId:连锁总店商品规格Id
        :param specIds:子店商品规格Id列表
        """
        return self.__client.call("eleme.product.chain.pid.batchSetPid", {"pId": p_id, "specIds": spec_ids})

    def delete_pid_by_spec_id(self, spec_id):
        """
        解除连锁总店商品规格与单店商品规格关系
        :param specId:子店的商品规格Id
        """
        return self.__client.call("eleme.product.chain.pid.deletePidBySpecId", {"specId": spec_id})

    def batch_delete_pid_by_spec_id(self, spec_ids):
        """
        批量解除连锁总店商品规格与单店商品规格关系
        :param specIds:子店的商品规格Id列表
        """
        return self.__client.call("eleme.product.chain.pid.batchDeletePidBySpecId", {"specIds": spec_ids})

    def get_menu_with_group(self, mid):
        """
        查询连锁总店菜单及分组信息
        :param mid:菜单Id
        """
        return self.__client.call("eleme.product.chain.menu.getMenuWithGroup", {"mid": mid})

    def query_menu_by_page(self, offset, limit):
        """
        分页查询连锁总店下的菜单列表
        :param offset:分页起始
        :param limit:一页个数
        """
        return self.__client.call("eleme.product.chain.menu.queryMenuByPage", {"offset": offset, "limit": limit})

    def create_menu(self, chain_menu_base_d_t_o):
        """
        添加连锁总店菜单
        :param chainMenuBaseDTO:添加的菜单信息
        """
        return self.__client.call("eleme.product.chain.menu.createMenu", {"chainMenuBaseDTO": chain_menu_base_d_t_o})

    def update_menu(self, mid, chain_menu_base_d_t_o):
        """
        更新连锁总店菜单
        :param mid:菜单Id
        :param chainMenuBaseDTO:菜单更新信息
        """
        return self.__client.call("eleme.product.chain.menu.updateMenu", {"mid": mid, "chainMenuBaseDTO": chain_menu_base_d_t_o})

    def delete_menu(self, mid):
        """
        删除连锁总店菜单
        :param mid:菜单Id
        """
        return self.__client.call("eleme.product.chain.menu.deleteMenu", {"mid": mid})

    def get_chain_item(self, iid):
        """
        查询连锁总店商品信息
        :param iid:连锁总店商品Id
        """
        return self.__client.call("eleme.product.chain.item.getChainItem", {"iid": iid})

    def batch_get_chain_item(self, iids):
        """
        批量查询连锁总店商品信息
        :param iids:连锁总店商品Id列表
        """
        return self.__client.call("eleme.product.chain.item.batchGetChainItem", {"iids": iids})

    def create_chain_item(self, gid, chain_item_base_d_t_o):
        """
        添加连锁总店商品
        :param gid:连锁总店商品分组Id
        :param chainItemBaseDTO:商品创建信息
        """
        return self.__client.call("eleme.product.chain.item.createChainItem", {"gid": gid, "chainItemBaseDTO": chain_item_base_d_t_o})

    def batch_create_chain_item(self, gid, chain_item_base_d_t_os):
        """
        批量添加连锁总店商品
        :param gid:连锁总店商品分组Id
        :param chainItemBaseDTOs:商品创建信息列表
        """
        return self.__client.call("eleme.product.chain.item.batchCreateChainItem", {"gid": gid, "chainItemBaseDTOs": chain_item_base_d_t_os})

    def replace_chain_item(self, gid, chain_item_d_t_o):
        """
        替换连锁总店商品
        :param gid:商品分组Id
        :param chainItemDTO:商品替换信息
        """
        return self.__client.call("eleme.product.chain.item.replaceChainItem", {"gid": gid, "chainItemDTO": chain_item_d_t_o})

    def batch_replace_chain_item(self, gid, chain_item_d_t_os):
        """
        批量替换连锁总店商品
        :param gid:商品分组Id
        :param chainItemDTOs:商品替换信息列表
        """
        return self.__client.call("eleme.product.chain.item.batchReplaceChainItem", {"gid": gid, "chainItemDTOs": chain_item_d_t_os})

    def update_chain_item_without_sku(self, iid, chain_item_base_d_t_o):
        """
        更新连锁总店商品不包含规格信息
        :param iid:连锁总店商品Id
        :param chainItemBaseDTO:商品更新信息
        """
        return self.__client.call("eleme.product.chain.item.updateChainItemWithoutSku", {"iid": iid, "chainItemBaseDTO": chain_item_base_d_t_o})

    def delete_chain_item(self, iid):
        """
        删除连锁总店商品
        :param iid:连锁总店商品Id
        """
        return self.__client.call("eleme.product.chain.item.deleteChainItem", {"iid": iid})

    def get_sku(self, p_id):
        """
        查询连锁总店商品规格
        :param pId:连锁总店商品规格Id
        """
        return self.__client.call("eleme.product.chain.item.getSku", {"pId": p_id})

    def add_sku(self, iid, chain_sku_base_d_t_o):
        """
        新增连锁总店商品规格
        :param iid:连锁总店商品Id
        :param chainSkuBaseDTO:添加规格信息
        """
        return self.__client.call("eleme.product.chain.item.addSku", {"iid": iid, "chainSkuBaseDTO": chain_sku_base_d_t_o})

    def update_sku(self, p_id, chain_sku_base_d_t_o):
        """
        更新连锁总店商品规格
        :param pId:连锁总店商品规格Id
        :param chainSkuBaseDTO:规格更新信息
        """
        return self.__client.call("eleme.product.chain.item.updateSku", {"pId": p_id, "chainSkuBaseDTO": chain_sku_base_d_t_o})

    def delete_sku(self, p_id):
        """
        删除连锁总店商品规格
        :param pId:连锁总店商品规格Id
        """
        return self.__client.call("eleme.product.chain.item.deleteSku", {"pId": p_id})

    def get_group(self, gid):
        """
        查询连锁总店商品分组
        :param gid:连锁总店商品分组Id
        """
        return self.__client.call("eleme.product.chain.group.getGroup", {"gid": gid})

    def get_group_with_item(self, gid):
        """
        查询连锁总店商品分组及商品详情
        :param gid:连锁总店商品分组Id
        """
        return self.__client.call("eleme.product.chain.group.getGroupWithItem", {"gid": gid})

    def create_group(self, mid, chain_group_base_d_t_o):
        """
        添加连锁总店商品分组
        :param mid:菜单Id
        :param chainGroupBaseDTO:分组创建信息
        """
        return self.__client.call("eleme.product.chain.group.createGroup", {"mid": mid, "chainGroupBaseDTO": chain_group_base_d_t_o})

    def batch_create_group(self, mid, chain_group_base_d_t_os):
        """
        批量添加连锁总店商品分组
        :param mid:菜单Id
        :param chainGroupBaseDTOs:分组创建信息列表
        """
        return self.__client.call("eleme.product.chain.group.batchCreateGroup", {"mid": mid, "chainGroupBaseDTOs": chain_group_base_d_t_os})

    def update_group(self, gid, chain_group_base_d_t_o):
        """
        更新连锁总店商品分组
        :param gid:连锁总店商品分组Id
        :param chainGroupBaseDTO:分组更新信息
        """
        return self.__client.call("eleme.product.chain.group.updateGroup", {"gid": gid, "chainGroupBaseDTO": chain_group_base_d_t_o})

    def delete_group(self, gid):
        """
        删除连锁总店商品分组
        :param gid:连锁总店商品分组Id
        """
        return self.__client.call("eleme.product.chain.group.deleteGroup", {"gid": gid})

