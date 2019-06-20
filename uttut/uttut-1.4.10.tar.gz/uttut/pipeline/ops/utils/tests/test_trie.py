from ..trie import Trie


def test_exist():
    word = 'abc'
    trie = Trie()
    trie.insert(word)
    assert word in trie
    assert 'ab' not in trie
    assert 'zxy' not in trie


def test_match_prefix():
    trie = Trie()
    trie.insert('珍奶')
    trie.insert('珍奶去冰')

    assert '珍奶去冰' == trie.match_prefix('珍奶去冰')
    assert '珍奶' == trie.match_prefix('珍奶去冰', shortest=True)
    assert '珍奶去冰' == trie.match_prefix('珍奶去冰謝謝')
    assert trie.match_prefix('我想要珍奶去冰') is None
