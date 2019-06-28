import json

from tokenizer_tools.conllz.reader import read_conllx
from tokenizer_tools.converter.conllz_to_offset import conllx_to_offset


def conllx_to_rasa(conllx_file, output_rasa):
    rasa_data = {
        "rasa_nlu_data": {
            "common_examples": [],
            "regex_features": [],
            "lookup_tables": [],
            "entity_synonyms": []
        },
    }

    rasa = rasa_data['rasa_nlu_data']['common_examples']

    with open(conllx_file) as fd:
        conllx_list = read_conllx(fd)

    for conllx in conllx_list:
        offset_data, is_failed = conllx_to_offset(conllx)
        text_str = ''.join(offset_data.text)

        offset_data.span_set.fill_text(text_str)

        data_item = {
            "text": text_str,
            "intent": offset_data.label,
            "entities": [
                {"start": i.start, "end": i.end, "value": i.value, "entity": i.entity}
                for i in offset_data.span_set
            ]
        }

        rasa.append(data_item)

    with open(output_rasa, 'w') as fd:
        json.dump(rasa_data, fd, ensure_ascii=False)


if __name__ == "__main__":
    conllx_to_rasa("/Users/howl/PyCharmProjects/seq2label/data/train.conllx", "/Users/howl/PyCharmProjects/seq2label/data/train.json")
