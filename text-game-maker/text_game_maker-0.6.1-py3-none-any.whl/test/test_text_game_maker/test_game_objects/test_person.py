from unittest import TestCase
from text_game_maker.player.player import Player
from text_game_maker.game_objects.person import Person
from text_game_maker.game_objects.items import Coins, SmallBag
from text_game_maker.game_objects.base import GameEntity

class TestObjectA(GameEntity):
    pass

class TestObjectB(GameEntity):
    pass

class TestObjectC(GameEntity):
    pass

class TestPerson(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.player = Player()

    def test_init(self):
        prefix = "0"
        name = "1"
        location="3"

        p = Person() # Verify we can create with no args

        # Verify constructor args set expected attrs
        p = Person(prefix, name)
        self.assertEqual(p.prefix, prefix)
        self.assertEqual(p.name, name)

        # Verify kwargs set attrs
        p = Person(location=location)
        self.assertEqual(p.location, location)

    def test_add_coins(self):
        initial_value = 23
        coins = Coins(value=initial_value)
        increment = 6

        p = Person()
        p.add_item(coins)
        
        self.assertIs(p.items[0], coins)

        p.add_coins()
        self.assertEqual(p.items[0].value, initial_value + 1)

        p.add_coins(increment)
        self.assertEqual(p.items[0].value, initial_value + increment + 1)

    def test_find_item_class(self):
        p = Person()
        obja = TestObjectA()
        objb = TestObjectB()
        objc = TestObjectC()
        p.add_items([obja, objb, objc])

        self.assertIs(obja, p.find_item_class(TestObjectA))
        self.assertIs(objb, p.find_item_class(TestObjectB))
        self.assertIs(objc, p.find_item_class(TestObjectC))
        self.assertIs(None, p.find_item_class(str))

    def test_add_shopping_list(self):
        p = Person()
        self.assertEqual(0, len(p.shopping_list))

        items = [("apple", 12), ("bleh", 6555677), ("car", 0)]
        p.add_shopping_list(*items)

        self.assertEqual(len(items), len(p.shopping_list))
        for name, value in items:
            self.assertTrue(name in p.shopping_list)
            self.assertEqual(value, p.shopping_list[name])
