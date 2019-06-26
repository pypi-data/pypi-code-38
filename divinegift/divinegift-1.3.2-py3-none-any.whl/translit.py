from transliterate import translit, get_available_language_codes
from transliterate.discover import autodiscover
from transliterate.base import TranslitLanguagePack, registry

#autodiscover()


class ExtendedRussianLangPack(TranslitLanguagePack):
    language_code = 'ru_ext'
    language_name = 'Russian extended'
    mapping = (
        'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ',
        'абцдефгхийклмнопкрстуввкызАБЦДЕФГХИЙКЛМНОПКРСТУВВКЫЗ',
    )
    pre_processor_mapping = {
        'shch': 'щ',
        'ya': 'я',
        'ia': 'я',
        'yu': 'ю',
        'iu': 'ю',
        'ch': 'ч',
        'sh': 'ш',
        'y': 'ы',
        'x': 'кс',
        'zh': 'ж',
        'ts': 'ц',
        'kh': 'х',
        'SHCH': 'Щ',
        'YA': 'Я',
        'IA': 'Я',
        'YU': 'Ю',
        'IU': 'Ю',
        'CH': 'Ч',
        'SH': 'Ш',
        'Y': 'Ы',
        'X': 'КС',
        'ZH': 'Ж',
        'TS': 'Ц',
        'KH': 'Х',
    }
    reversed_specific_pre_processor_mapping = {
        'в': 'v',
        'ё': 'e',
        'ж': 'zh',
        'й': 'i',
        'к': 'k',
        'х': 'kh',
        'ц': 'ts',
        'ч': 'ch',
        'ш': 'sh',
        'щ': 'shch',
        'ъ': "'",
        'ы': 'y',
        'ь': "'",
        'э': 'e',
        'ю': 'iu',
        'я': 'ia',
        'В': 'V',
        'Ё': 'E',
        'Ж': 'ZH',
        'Й': 'I',
        'К': 'K',
        'Х': 'KH',
        'Ц': 'TS',
        'Ч': 'CH',
        'Ш': 'SH',
        'Щ': 'SHCH',
        'Ъ': "'",
        'Ы': 'Y',
        'Ь': "'",
        'Э': 'E',
        'Ю': 'IU',
        'Я': 'IA',
    }


registry.register(ExtendedRussianLangPack, force=True)