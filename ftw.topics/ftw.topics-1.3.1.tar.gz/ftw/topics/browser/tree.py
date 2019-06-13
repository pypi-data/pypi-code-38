from Products.CMFCore.utils import getToolByName
from Products.Five.browser import BrowserView
from ftw.topics.interfaces import ITopic


def get_brain_data(brain):
    return {'title': brain.Title,
            'path': brain.getPath(),
            'url': brain.getURL(),
            'children': []}


def get_parent_path(path):
    return '/'.join(path.rstrip('/').split('/')[:-1])


def make_treeish(data):
    path2node = dict(map(lambda item: (item['path'], item), data))

    tree = []
    for node in data:
        parent_path = get_parent_path(node['path'])
        if parent_path in path2node:
            path2node[parent_path]['children'].append(node)
        else:
            tree.append(node)

    return tree


class TreeView(BrowserView):

    def get_tree(self):
        brains = self._get_brains()
        data = map(get_brain_data, brains)
        data = sorted(data, key=lambda item: item.get('title'))
        data = make_treeish(data)
        return data

    def _get_brains(self):
        query = {'object_provides': ITopic.__identifier__,
                 'path': {'query': '/'.join(self.context.getPhysicalPath()),
                          'depth': 2}}

        catalog = getToolByName(self.context, 'portal_catalog')
        return catalog(query)
