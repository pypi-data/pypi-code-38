from kivy.app import App
from kivy.lang import Builder
from kivy.uix.label import Label

# from . wombat import Wombat
# from . wombat import Wombat as Wombat2


DATA = """
<MyLabel1>
    text: 'MyLabel1'

MyLabel1:
"""

MyLabel1 = Label


class MyLabel2(Label):
    pass


class MainApp(App):
    def build(self):
        try:
            return Builder.load_string(DATA)
        except Exception:
            print('MyLabel1 fails')
        try:
            return Builder.load_string(DATA.replace('MyLabel1', 'Wombat'))
        except Exception:
            print('Wombat fails')

        return Builder.load_string(DATA.replace('1', '2'))


if __name__ == '__main__':
    MainApp().run()
