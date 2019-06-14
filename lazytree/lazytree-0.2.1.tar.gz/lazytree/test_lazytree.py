import funcy as fn

from lazytree import LazyTree


def split(itvl):
    lo, hi = itvl
    mid = lo + (hi - lo)/2
    return (lo, mid), (mid, hi)


def test_children():
    tree = LazyTree(root=(0, 1), child_map=split)
    assert [c.view() for c in tree.children] == [(0, 0.5), (0.5, 1)]
    tree2 = tree.children[0]
    assert [c.view() for c in tree2.children] == [(0, 0.25), (0.25, .5)]


def test_map():
    tree = LazyTree(root=(0, 1), child_map=split, view=sum)
    tree2 = LazyTree(root=(0, 1), child_map=split).map(sum)
    assert tree.view() == tree2.view()

    for c1, c2 in zip(tree.children, tree2.children):
        assert c1.view() == c2.view()

    assert tree.with_identity_view().view() == (0, 1)


def assert_contracting(elems):
    max_size = 1
    for size in fn.take(7, elems):
        assert 0 <= size <= max_size
        max_size = size

    assert max_size < 0.5


def test_bfs():
    tree = LazyTree(root=(0, 1), child_map=split, view=lambda x: x[1] - x[0])
    assert_contracting(tree.bfs())


def test_cost_guided_traversal():
    tree = LazyTree(root=(0, 1), child_map=split, view=lambda x: x[1] - x[0])
    assert_contracting(tree.cost_guided_traversal(lambda x: -x))

    sizes1 = fn.take(5, tree.cost_guided_traversal(lambda x: x))
    sizes2 = fn.take(5, tree.bfs())
    assert sizes1 == sizes2


def test_prune_and_leaves():
    tree = LazyTree(root=(0, 1), child_map=split, view=lambda x: x[1] - x[0])
    tree2 = tree.prune(isleaf=lambda x: x <= 0.2)

    assert [c.view() for c in tree.children] == \
        [c.view() for c in tree2.children]

    assert all(c >= 0.1 for c in tree2.leaves())
    assert len(list(tree2.leaves())) == 8
