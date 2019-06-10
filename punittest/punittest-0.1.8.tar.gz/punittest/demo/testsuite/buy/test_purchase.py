#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from punittest import PUnittest, logger


class TestPurchase(PUnittest):
    """测试游戏内购买功能"""

    def setUp(self):
        super(TestPurchase, self).setUp()
        logger.info("登录角色")
        logger.info("修改角色货币")

    def tearDown(self):
        logger.info("角色登出")
        super(TestPurchase, self).tearDown()

    @PUnittest.tag("Smoke", "Regression")
    def test_purchase_weapon(self):
        """测试购买武器成功"""
        logger.info("调用购买接口，获取购买结果")
        result = "某款武器"
        self.assertEqual(result, "某款武器")

    @PUnittest.tag("Smoke", "Regression")
    def test_purchase_armor(self):
        """测试购买防具成功"""
        logger.info("调用购买接口，获取购买结果")
        result = "某款防具"
        self.assertTrue(result, "某款饰品")

    @PUnittest.tag()
    def test_purchase_accessories(self):
        """测试购买饰品成功"""
        logger.info("将角色货币归0")
        logger.info("调用购买接口，获取购买结果")
        result = "角色货币不足"
        self.assertTrue(result, "某款饰品")