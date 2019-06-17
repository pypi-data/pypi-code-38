# coding=utf-8

import config
from ..extra_passport import system_name
from ..http_handler import wallet_handler as w, contract_handler as c, entrance_handler

base = '{}/{}/{}'.format(config.VER, config.PLATFORM, system_name)
base_chain = '{}/(?P<catalog>chain|catalog)/(?P<cid>\w+)'.format(base)
base_coin = '{}/(?P<cname>coin|contract)/(?P<contract_id>\w+)'.format(base)
routes = [
    # 查询组织拥有哪些资源的许可证/通行证，许可范围有多大
    (rf"/{base}/entrance/employ/passports", entrance_handler.EmployPassportsHandler),

    # 查询我的钱包账户列表
    (rf"/{base}/mine", w.MyWalletsHandler),

    # ******************************************************
    # 以下catalog/([a-f0-9]*)的含义是指在哪个区块链下，如eth，btc，eos等等，参数为注册时生成的类型ID
    # ******************************************************

    # *************************
    # 合约相关(注意：主币也是一种合约！)

    # 查询已注册合约列表
    (rf"/{base_chain}/(?P<cname>coin|contract)/list", c.QueryContractsHandler),

    # 向平台注册/注销合约（仅管理员可以使用）
    (rf"/{base_chain}/(?P<cname>coin|contract)/(?P<contract_id>\w*)", c.ContractHandler),

    # 获取交易详情(根据tx_hash，适合链上所有交易)
    (rf"/{base_chain}/txhash/(?P<tx_hash>[a-fA-F0-9x]*)", w.TxInfoByHashHandler),

    # 获取交易详情(根据tx_id，适合在本系统提交的交易)
    (rf"/{base}/txid/(?P<tx_id>[a-f0-9]*)", w.TxInfoByIdHandler),

    # 查询钱包交易列表
    (rf"/{base_chain}/address/(?P<address>[a-fA-F0-9x]*)/tx/list", w.TxListHandler),

    # *************************
    # 常用接口

    # 创建/删除新钱包账户，含合约钱包，只是对应的contract_id不同
    (rf"/{base_coin}/wallet/(?P<wallet_id>[a-f0-9]*)", w.WalletHandler),

    # 查询余额(根据钱包地址)
    (rf"/{base_coin}/address/(?P<address>[a-fA-F0-9x]*)/balance", w.BalanceHandler),

    # 校验钱包密码
    (rf"/{base_coin}/address/(?P<address>[a-fA-F0-9x]*)/verify", w.VerifyHandler),

    # 交易矿工费预估
    (rf"/{base_coin}/address/(?P<from_address>[a-fA-F0-9x]*)/transfer/estimate", w.TransferEstimateHandler),

    # 执行转账交易
    (rf"/{base_coin}/address/(?P<from_address>[a-fA-F0-9x]*)/transfer", w.TransferHandler),

    # *************************
    # 高级接口

    # 合约查看（不用签名，不用矿工费，不会写入数据）
    (rf"/{base_coin}/view", w.ViewHandler),

    # 合约交易调用（需签名，会扣矿工费，会写入/改变数据）
    (rf"/{base_coin}/address/(?P<from_address>[a-fA-F0-9x]*)/transaction", w.TransactionHandler),

]
