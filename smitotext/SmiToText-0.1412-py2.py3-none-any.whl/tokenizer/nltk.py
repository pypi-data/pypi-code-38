from jpype import unicode
from nltk.tokenize import word_tokenize
import nltk.data


from nltk.tokenize import sent_tokenize, word_tokenize

def nltkSentTokenizer(sentence, DEBUG=False):
    return sent_tokenize(sentence)


def nltkTokenizer(sentence, DEBUG=False):
    tokens = word_tokenize(sentence)
    # tokens = sent_tokenize(sentence)
    # tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
    # tokens = tokenizer.tokenize(sentence)
    nltkConvertSentence = (' '.join(str(e) for e in tokens))

    return nltkConvertSentence

def ntlkAnalize(sentence, DEBUG=False):
    tokens = word_tokenize(sentence)
    tagged = nltk.pos_tag(tokens)
    return tagged

if __name__ == '__main__':

    while True:
        try:
            inputText = input("\n\n문장을 입력하세요?: \n")
            inputText = unicode(inputText)
        except UnicodeDecodeError:
            print("다시 입력하세요\n")
            continue

        if inputText == 'exit':
            exit(1)
        print(nltkTokenizer(inputText))
        print(ntlkAnalize(inputText))

        # print(twitterStemmer(inputText))
