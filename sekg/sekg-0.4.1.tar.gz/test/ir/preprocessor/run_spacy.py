from sekg.ir.preprocessor.spacy import SpacyTextPreprocessor

if __name__ == "__main__":
    preprocessor = SpacyTextPreprocessor()
    test_case_list = [
        (
            "This is a ArrayList, it contains all of the classes for creating user interfaces and for painting graphics and images."
            , ['ArrayList',
               'class',
               'user',
               'interface',
               'painting',
               'graphic',
               'image',
               'contain',
               'create']
        ),

        (
            "how to get File's MD5 checksum",
            ['File', 'md5', 'checksum']

        )

    ]

    for old_str, new_str in test_case_list:
        team = preprocessor.extract_words_for_query(old_str)
