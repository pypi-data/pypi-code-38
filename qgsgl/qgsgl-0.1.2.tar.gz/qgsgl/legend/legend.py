

class Legend:
    def __init__(self):
        self.legend_items = []

    def add_item(self, legend_item):
        '''
        Add legend item object to Legend object
        '''
        self.legend_items.append(legend_item)

    def render(self, path, format='SVG'):
        '''
        Calls the LegendItem render method to write image to file system
        '''
        for legend_item in self.legend_items:
            legend_item.render(path, format)
