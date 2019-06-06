from pyquery import PyQuery
from .storage_editor import storage_query

class DataGenerator:
    def __init__(self, generator, api=None):
        self.api = api
        self.generator = generator
        print generator

    def __call__(self, data):
        if "<ri:" in data or '<ac:' in data:
            self.query = storage_query
        else:
            self.query = PyQuery

        return self.generate(self.query(data)(":root"), **self.generator)

    def get_value(self, element, data, method, *args):
        selection = self.get_selection(element, data)
        return getattr(selection, method)(*args)

    def get_selection(self, element, data):
        for method in ['find', 'children', 'parents', 'closest', 'filter', 'next_all', 'prev_all', 'siblings']:
            if method in data:
                if not data[method]:
                    return getattr(element, method)()
                else:
                    return getattr(element, method)(data[method])
        if 'eq' in data:
            return element.eq(int(data['eq']))

        if 'toplevel' in data:
            for e in element.find(data['toplevel']).items():
                for item in e.parents():
                    if item is
                # only those elements, which have no data['toplevel'] parents,
                # which are under element
                if e
            for element in

        return element

    def meet_conditions(self, element, data):
        result = True
        if 'is' in data:
            result = result and element.is_(data['is'])
        if 'isnt' in data:
            result = result and element.not_(data['isnt'])
        if 'not' in data:
            result = result and element.not_(data['not'])
        if 'has' in data:
            if isinstance(data['has'], dict):
                for k,v in data['has'].items():
                    result = result and len(getattr(element, k)(v)) > 0
            else:
                result = result and len(element.parents(data['has'])) > 0

        return result

    def generate(self, element, **data):
        if 'do' in data:
            selection = self.get_selection(element, data)
            if isinstance(data['do'], list):
                for item in data['do']:
                    if self.meet_conditions(selection, item):
                        return self.generate(e, **item)
            else:
                return self.generate(selection, **data)

        if 'list' in data:
            result = []

            for e in self.get_selection(element, data):
                e = self.query(e)

                if data['list'] == 'text':
                    result.append(e.text())
                elif data['list'] == 'html':
                    result.append(e.html())
                else:
                    for item in data['list']:
                        if not self.meet_conditions(element, item): continue
                        result.append(self.generate(e, **item))
            return result

        if 'object' in data:
            result = {}
            for e in self.get_selection(element, data):
                e = self.query(e)

                for item in data['object']:
                    if not self.meet_conditions(element, item): continue
                    result[item['name']] = self.generate(e, **item)

            return result

        if 'attr' in data:
            return self.get_value(element, data, 'attr', data['attr'])

        if data.get('return'):
            return self.get_value(element, data, data['return'])

        else:
            return self.get_value(element, data, 'text')
