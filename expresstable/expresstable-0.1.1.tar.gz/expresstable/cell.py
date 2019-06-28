from termcolor import colored

class Cell:

    def __init__(self, text, **kwargs):
        '''Returns a new Cell instance

        Arguments:
            text        - Text to appear inside this Cell
            fgcolor     - Foreground color to use when printing text
            bgcolor     - Background color to use when printing text
            align       - Where to align text in the Cell
            bold        - Display text in Cell as bold
            dark        - Use a darker shade of the supplied fgcolor
        '''

        self.text = str(text)
        self.kwargs = kwargs

    def as_string(self, padding, padding_character=' '):
        '''Return Cell object as a string'''

        # Prepend 'on_' to bgcolor as it will be passed to termcolor
        if 'bgcolor' in self.kwargs and self.kwargs['bgcolor'] is not None:
            self.kwargs['bgcolor'] = f'on_{self.kwargs["bgcolor"]}'

        # Calculate padding
        padding = ' ' * (padding - len(self.text))
        pre_padding = padding[0:int(len(padding) / 2)]
        post_padding = padding[len(pre_padding):]

        # Generate attributes
        attributes = [
            attribute for attribute in ['bold', 'dark']
            if self.kwargs.get(attribute, None)
        ]

        # Generate text
        if self.kwargs.get('align', None) == 'right':
            text = f'{padding}{self.text}'

        elif self.kwargs.get('align', None) == 'center':
            text = f'{pre_padding}{self.text}{post_padding}'

        else:
            text = f'{self.text}{padding}'

        # Format text
        text = colored(
            f'{padding_character}{text}{padding_character}',
            self.kwargs.get('fgcolor', None),
            self.kwargs.get('bgcolor', None),
            attrs=attributes
        )

        return text
