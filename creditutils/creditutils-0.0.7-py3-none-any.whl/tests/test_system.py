# -*- coding:UTF-8 -*-


'''
Created on 2013年12月4日

@author: work_cfh
'''
import unittest
import creditutils.system_util as mysystem
import win32con
import win32api


class Test(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testSystemWide(self):
        self.assertTrue(mysystem.is_64_windows())


class TestRegedit(unittest.TestCase):

    def setUp(self):
        self.itemTest = 'SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\JustForTest'
        self.edit = mysystem.Regedit(self.itemTest)
        self.edit.Create()

    def tearDown(self):
        self.edit.Delete()

    def testIsExists(self):
        edit = mysystem.Regedit(self.itemTest)
        self.assertTrue(edit.IsExists())

        itemPath = self.itemTest + '\\TestIsExists'
        edit = mysystem.Regedit(itemPath)
        self.assertFalse(edit.IsExists())

        self.assertTrue(edit.IsExists(self.itemTest))
        itemPath = self.itemTest + '\\TestIsExistsAnother'
        self.assertFalse(edit.IsExists(itemPath))

    def testSetItemValue(self):
        itemName = 'what'
        itemType = win32con.REG_SZ
        itemValue = 'nothing'
        self.edit.SetItemValue(itemName, itemValue, itemType)

        itemInfo = self.edit.GetItemInfo(itemName)
        self.assertEqual(itemValue, itemInfo[0])
        self.assertEqual(itemType, itemInfo[1])

        self.assertEqual(itemValue, self.edit.GetItemValue(itemName))
        self.assertEqual(itemType, self.edit.GetItemType(itemName))

    def testSetItemsValue(self):
        itemsInfo = {}

        itemName_01 = 'what'
        itemValue_01 = 'how are you'
        itemType_01 = win32con.REG_SZ
        itemInfo_01 = (itemValue_01, itemType_01)
        itemsInfo[itemName_01] = itemInfo_01

        itemName_02 = 'second'
        itemValue_02 = 15
        itemType_02 = win32con.REG_DWORD
        itemInfo_02 = (itemValue_02, itemType_02)
        itemsInfo[itemName_02] = itemInfo_02

        itemName_03 = 'third'
        itemValue_03 = 'nothing'
        itemType_03 = win32con.REG_SZ
        itemInfo_03 = (itemValue_03, itemType_03)
        itemsInfo[itemName_03] = itemInfo_03

        itemsName = [itemName_01, itemName_02, itemName_03]

        self.edit.SetItemsValue(itemsInfo)

        itemsInfoGet = self.edit.GetItemsInfo(itemsName)
        self.assertEquals(itemInfo_01, itemsInfoGet[itemName_01])
        self.assertEquals(itemInfo_02, itemsInfoGet[itemName_02])
        self.assertEquals(itemInfo_03, itemsInfoGet[itemName_03])

        itemsValueGet = self.edit.GetItemsValue(itemsName)
        self.assertEqual(itemValue_01, itemsValueGet[itemName_01])
        self.assertEqual(itemValue_02, itemsValueGet[itemName_02])
        self.assertEqual(itemValue_03, itemsValueGet[itemName_03])

        itemsTypeGet = self.edit.GetItemsType(itemsName)
        self.assertEqual(itemType_01, itemsTypeGet[itemName_01])
        self.assertEqual(itemType_02, itemsTypeGet[itemName_02])
        self.assertEqual(itemType_03, itemsTypeGet[itemName_03])

    def testRegDeleteTree(self):
        grandsonItem = 'SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\JustForTest\\first\\second\\third'
        subItem = 'SYSTEM\\CurrentControlSet\\Services\\EventLog\\Application\\JustForTest'
        itemName = 'first'
        grandsonEdit = mysystem.Regedit(grandsonItem)
        self.assertFalse(grandsonEdit.IsExists())
        grandsonEdit.Create()
        grandsonEdit.SetItemValue('what', 'are you')

        handle = win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, subItem, 0, win32con.KEY_ALL_ACCESS)
        mysystem.RegDeleteTree(handle, itemName)
        handle.Close()

        srcEdit = mysystem.Regedit(subItem)
        dstItem = subItem + '\\' + itemName
        dstEdit = mysystem.Regedit(dstItem)
        self.assertTrue(srcEdit.IsExists())
        self.assertFalse(dstEdit.IsExists())


def test_SystemWide():
    print(mysystem.is_64_windows())
    print(mysystem.getProgramFiles32())
    print(mysystem.getProgramFiles64())


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
#     test_SystemWide()
