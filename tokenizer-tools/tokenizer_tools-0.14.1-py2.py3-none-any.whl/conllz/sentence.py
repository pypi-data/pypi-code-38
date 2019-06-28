import uuid


class Sentence(object):
    def __init__(self, word_lines=None, attribute_lines=None, attribute_names=None, id=None):
        self.word_lines = word_lines if word_lines else []
        self.attribute_lines = attribute_lines if attribute_lines else []
        self.attribute_names = attribute_names if attribute_names else []
        self.id = id if id is not None else str(uuid.uuid4())

    def get_attribute(self, key):
        if isinstance(key, int):
            return self.get_attribute_by_index(key)
        return self.get_attribute_by_name(key)

    def get_attribute_by_name(self, name):
        attribute_index = self.attribute_names.index(name)
        return self.attribute_lines[attribute_index]

    def get_attribute_by_index(self, index):
        return self.attribute_lines[index]

    def read_as_row(self):
        for i in zip(self.word_lines, *self.attribute_lines):
            yield i

    def write_as_row(self, data):
        if self.attribute_lines:
            if len(self.attribute_lines) != len(data) - 1:
                raise ValueError('data not match attribute lines')

        self.word_lines.append(data[0])

        if not self.attribute_lines:
            self.attribute_lines = [[i] for i in data[1:]]
        else:
            for index, attribute_line in enumerate(self.attribute_lines):
                attribute_line.append(data[index+1])

    def read_as_row_dict(self):
        for i in self.read_as_row():
            word = i[0]
            attributes = i[1:]
            attribute_dict = dict(zip(attributes, self.attribute_names))

            yield word, attribute_dict

    def __eq__(self, other):
        return self.id == other.id and self.word_lines == other.word_lines and self.attribute_lines == other.attribute_lines


class SentenceX(Sentence):
    def __init__(self, *args, **kwargs):
        super(SentenceX, self).__init__(*args, **kwargs)

        self.meta = {}
