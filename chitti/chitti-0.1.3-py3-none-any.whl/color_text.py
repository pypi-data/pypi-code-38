from termcolor import colored

def color_words_in_text(text, words, color='green', text_color='white'):
    color = 'on_' + color

    for word in text.split():
        if word in words:
            word = colored(word, text_color, color)
        print(word, end=' ')