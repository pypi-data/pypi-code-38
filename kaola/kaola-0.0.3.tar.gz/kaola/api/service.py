#!/usr/bin/python3
# @Time    : 2019-06-25
# @Author  : Kevin Kong (kfx2007@163.com)

from kaola.comm.comm import Comm


class Service(Comm):
    """售后"""

    def search_refund(self, refund_status, start_time, end_time, page_no=1, page_size=20):
        """
        根据订单信息查询订单
        参数：
        refund_status: 退单状态
        start_time: 开始时间
        end_time: 结束时间
        """
        data = {
            "method": "kaola.refund.search",
            "refund_status": refund_status,
            "start_time": start_time,
            "end_time": end_time,
            "page_no": page_no,
            "page_size": page_size
        }
        return self.post(data=data)

    def get_refund(self, refund_id):
        """
        根据售后单号查询详细信息
        参数:
        refund_id:售后编号
        """
        data = {
            "refund_id": refund_id,
            "method": "kaola.refund.get"
        }
        return self.post(data=data)

    def change_refund_type(self, refund_id, refund_type, refund_only_reason=None):
        """
        修改退货退款类型
        参数：
        refund_id:售后编号
        refund_type: 售后类型 0 退货退款 1 仅退款
        refund_only_reason: 1 .签收超过7天申请无理由退货
                            2 .签收超过7天申请差价补偿
                            3 .商品有差价但还未签收
                            4 .上传商品完整图片
                            5 .商品不支持7天申请无理由退货
                            6 .海淘关税报销
        """
        data = {
            "method": "kaola.refund.changetype",
            "refund_id": refund_id,
            "refund_type": refund_type,
            "refund_only_reason": refund_only_reason
        }
        return self.post(data=data)

    def agree_refund(self, refund_id, refund_remark=None, pic=None):
        """
        同意用户申请退款
        参数：
        refund_id: 售后编号
        refund_mark: 退款备注
        pic: 图片 最多三张图片 1|2|3
        """
        data = {
            "method": "kaola.refund.agree",
            "refund_id": refund_id,
            "refund_remard": refund_remark,
            "pic": pic
        }

        return self.post(data=data)

    def refuse_refund(self, refund_id, refund_refuse_reason):
        """
        拒绝用户申请退款
        参数：
        refund_id: 售后编号
        refund_refuse_reason: 拒绝的原因
        """
        data = {
            "method": "kaola.refund.refuse",
            "refund_id": refund_id,
            "refund_refuse_reason": refund_refuse_reason
        }

        return self.post(data=data)

    def agree_refund_goods(self, refund_id):
        """
        同意用户申请退货
        参数：
        refund_id: 售后编号
        """
        data = {
            "refund_id": refund_id,
            "method": "kaola.refundgoods.agree"
        }

        return self.post(data=data)

    def refuse_refund_goods(self, refund_id, refund_refuse_reason):
        """
        拒绝用户申请退货
        参数：
        refund_id: 售后编号
        refund_refuse_reason: 拒绝原因
        """
        data = {
            "method": "kaola.refundgoods.refuse",
            "refund_id": refund_id,
            "refund_refuse_reason": refund_refuse_reason
        }
        return self.post(data=data)
