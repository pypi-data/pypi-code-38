import cv2

class Pyramid:
    "A data structure which consists of levels. Each level contains an image of a different resolution than other layers."

    def __init__(self, layer_number, depth):
        self.levels = []
        self.layer_number = layer_number
        self.depth = depth

    def get_layer_number(self):
        return self.layer_number

    def get_depth(self):
        return self.depth

    def add_lower_resolution_level(self, level):
        self.levels.append(level)

    def add_higher_resolution_level(self, level):
        self.levels.insert(0, level)

    def get_level(self, level_number):
        "lowest level of the pyramid hes the highest resolution and number 0"
        return self.levels[level_number]

    def get_top_level(self):
        return self.levels[-1]

    #test this
    def sort_levels(self):
        old_levels = self.levels
        self.levels = sorted(old_levels, key = lambda x:x.array.shape[0], reverse=True) # bigger resolution lower index

    def collapse(self):
        """Collapse the pyramid - effectively flatten a fused pyramid along levels to get one all in focus image."""
        image = self.get_top_level().get_array()
        for level_number in range(len(self.levels)-2, -1, -1):
            expanded = cv2.pyrUp(image)
            level = self.get_level(level_number).get_array()
            if expanded.shape != level.shape:
                expanded = expanded[:level.shape[0], :level.shape[1]]
            image = expanded + level

        return image

    def add_bunch_of_levels(self, bunch):
        for level in bunch:
            self.levels.append(level)