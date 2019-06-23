from bs4 import BeautifulSoup, NavigableString
from swissarmykit.utils.fileutils import FileUtils

class BItem:

    def __init__(self, item: BeautifulSoup = None, html='', html_path='', is_debug=False, type=''):
        self.item = item
        self.is_debug = is_debug
        self.type = type
        if html:
            self.item =  BeautifulSoup(html, 'html.parser')

        if html_path:
            h = FileUtils.load_html_file(html_path)
            self.item = BeautifulSoup(h, 'html.parser')

    def parent(self, level=1):
        item = self.item
        if self.is_not_null():
            # Ignore 1 level text node.
            for i in range(level + 1):
                item = item.parent
        return BItem(item=item, is_debug=self.is_debug)


    def find_by_text(self, text=''):
        item = self.item
        if self.is_not_null():
            item = self.item.find(text=text)
        return BItem(item=item, is_debug=self.is_debug)

    def next_sibling(self):
        item = self.item
        if self.is_not_null():
            item = self.item.nextSibling
            if isinstance(item, NavigableString):
                item = BeautifulSoup(item,  'html.parser')
        return BItem(item=item, is_debug=self.is_debug)

    def img_src(self):
        return self.attr('src')

    def href(self):
        return self.attr('href')

    def has_attr(self, key):
        if self.item and self.item.has_attr(key):
            return True
        return False

    def attr(self, attr=''):
        value = ''
        if self.item and self.item.has_attr(attr):
            value = self.item[attr]
        else:
            if self.is_debug:
                print('WARN: BItem is None, cant get text')
        return value

    def set_type(self, tag):
        self.type = tag

    def html(self):
        value = ''
        if self.item:
                value = str(self.item)
        else:
            # print('WARN: BItem is None, cant get text')
            pass
        return value

    def text(self, new_line=False, recursive=True, replace_white_space=False):
        value = ''
        if self.item:
            if new_line:
                value = self.item.get_text(separator='\n').strip()
            elif not recursive:
                text = self.item.find(text=True, recursive=recursive)
                value = text.strip() if text else ''
            elif replace_white_space:
                val = [i.strip() for i in self.item.text.split('\n')]
                value = ' '.join(val).strip()
            else:
                value = self.item.text.strip()
        else:
            # print('WARN: BItem is None, cant get text')
            pass
        return value

    def find_last(self, *args, **kwargs):
        lst = self.find_all(*args, **kwargs)
        return lst[-1] if len(lst) else []

    def find(self, selector='div.name', recursive=True, decompose=False): # type: (str, bool, bool) -> BItem
        ''' This function will not return None, use bitem.is_not_null() to check it. '''
        if ' ' in selector:
            return self.find_complex(selector, recursive=recursive)

        data = self.parse_selector_simple(selector)
        attrs = {data.get('attr_key'): data.get('attr_value')} if data.get('attr_key') else {}
        item = self.item
        tag = ''
        if item:
            item = self.item.find(data.get('tag'), attrs=attrs, recursive=recursive)

            if decompose:
                items = self.item.find_all(tag, attrs=attrs, recursive=recursive)
                for _item in items:
                    _item.decompose()

                item = self.item

        return BItem(item=item, is_debug=self.is_debug, type=tag)

    def is_not_null(self):
        return self.item != None

    def is_null(self):
        return self.item == None

    def find_all(self, selector='div.name', recursive=True):  # type: (str, bool) -> [BItem]
        lst = []
        if ' ' in selector:
            return self.find_all_complex(selector, recursive=recursive)

        data = self.parse_selector_simple(selector)
        if self.is_not_null():
            tag = data.get('tag')

            if data.get('attr_key'):
                items = self.item.find_all(tag, attrs={data.get('attr_key'): data.get('attr_value')}, recursive=recursive)
            else:
                items = self.item.find_all(tag, recursive=recursive)
            for item in items:
                lst.append(BItem(item=item, is_debug=self.is_debug, type=tag))
        return lst

    def find_by_texts(self, selector,  text):
        lst = []

        if '.' in selector or '#' in selector or '[' in selector:
            raise Exception('This method use for single item only!!')

        if self.is_not_null():
            for item_ in self.item.find_all(selector, string=text):
                lst.append(BItem(item=item_, type=selector))

        return lst


    def find_complex(self, selector='div', recursive=True):
        if ' ' in selector:
            selectors = selector.split(' ')
            bitem = self.find(selectors[0], recursive=recursive)
            if bitem.is_not_null():
                for selector_ in selectors[1:]:
                    bitem = bitem.find(selector_, recursive=recursive)
            return bitem
        return None

    def find_all_complex(self, selector='div', recursive=True):
        selectors = selector.split(' ')
        b_item = None
        for selector_ in selectors[:-1]:
            if not b_item:
                b_item = self.find(selector_, recursive=recursive)
            else:
                b_item = b_item.find(selector_, recursive=recursive)
        return b_item.find_all(selectors[-1], recursive=recursive)


    def parse_selector_simple(self, selector='div'):
        ''' https://www.w3schools.com/cssref/css_selectors.asp '''
        data = {}

        if '#' in selector:
            tag_name, id_name = selector.split('#')

            data['tag'] = tag_name if tag_name else 'div'
            data['attr_key'] = 'id'
            data['attr_value'] = id_name
            return data


        if '.' in selector:
            tag_name, class_name = selector.split('.')

            data['tag'] = tag_name if tag_name else 'div'
            data['attr_key'] = 'class'
            data['attr_value'] = class_name
            return data

        if '[' in selector:
            tag_name, class_name = selector.split('[')
            key, value = class_name.strip(']').split('=')

            data['tag'] = tag_name if tag_name else 'div'
            data['attr_key'] = key
            data['attr_value'] = value.strip('"').strip("'")
            return data

        data['tag'] = selector
        data['attr_key'] = ''
        data['attr_value'] = ''
        return data

    def get_html_src(self):
        return str(self.item)

    def inner_html(self):
        return str(self.item)

    def replace(self, text, new):
        return BItem(html=str(self.item).replace(text, new))

    def remove_element(self, selector='div.name', recursive=True): # type: (str, bool) -> BItem
        return self.find(selector=selector, recursive=recursive, decompose=True)

    def add_element(self, tag='div', text='', position=0, **kwargs):
        new_tag = self.item.new_tag(tag, id='file_history', **kwargs)
        new_tag.string = text
        self.item.insert(position, new_tag)
        return BItem(item=self.item, is_debug=self.is_debug)

    def to_html_desktop(self):
        FileUtils.output_html_to_desktop(str(self.item))
        return True

    def __str__(self):
        re = 'INFO: '
        if self.type == 'a':
            re += 'Link: "%s",  %s' % (self.href(), self.text())
        if self.type == 'div':
            re += 'Div: %s' % self.text()
        if self.type == 'img':
            re += 'Img: "%s"' % self.img_src()

        re += '\n' + str(self.item) + '\n'
        return re

if __name__ == '__main__':
    bsoup = BItem()
    print(bsoup.parse_selector_simple('div.test'))