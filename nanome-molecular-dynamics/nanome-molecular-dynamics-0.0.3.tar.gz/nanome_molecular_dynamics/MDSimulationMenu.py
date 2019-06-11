import nanome

class MDSimulationMenu():
    def __init__(self, plugin):
        self.__plugin = plugin
        self.__run_button = None
        self.__menu = None
        self.__complexes_list = None

    def open(self):
        self.__menu.enabled = True
        self.__plugin.update_menu(self.__menu)

    def change_state(self, state):
        self.__run_button.selected = state
        self.__plugin.update_content(self.__run_button)

    def change_complex_list(self, complex_list):
        def complex_pressed(button):
            complex = button.complex
            if complex == None:
                nanome.util.Logs.error("Couldn't retrieve a complex from its button")
                return

            if button.selected == False:
                button.selected = True
                self.__plugin._selected_complexes.append(complex.index)
            else:
                button.selected = False
                self.__plugin._selected_complexes.remove(complex.index)
            self.__plugin.update_content(button)

        self.__plugin._selected_complexes = []
        self.__complexes_list.items = []

        for complex in complex_list:
            clone = self.__complex_item_prefab.clone()
            btn = clone.get_children()[0].get_content()
            btn.set_all_text(complex.molecular.name)
            btn.complex = complex
            btn.register_pressed_callback(complex_pressed)
            self.__complexes_list.items.append(clone)

        self.__plugin.update_menu(self.__menu)

    def build_menu(self):
        def refresh_button_pressed_callback(button):
            self.__plugin.request_refresh()

        def run_button_pressed_callback(button):
            self.__plugin.toggle_simulation()

        # Request and set menu window
        menu = self.__plugin.menu
        menu.title = "MD Simulation"
        menu._width = 1.0
        menu._height = 1.0
        self.__menu = menu

        # Create all needed layout nodes
        menu.root.clear_children()
        content = menu.root.create_child_node()
        content.layout_orientation = nanome.ui.LayoutNode.LayoutTypes.horizontal

        ln_list = content.create_child_node()
        ln_list_title = ln_list.create_child_node()
        ln_list_list = ln_list.create_child_node()

        ln_settings = content.create_child_node()
        ln_refresh = ln_settings.create_child_node()
        ln_run = ln_settings.create_child_node()

        # Create the titles
        ln_list_title.add_new_label(text="Targets")

        # Create the lists
        self.__complexes_list = ln_list_list.add_new_list()
        self.__complexes_list.display_columns = 1
        self.__complexes_list.display_rows = 8
        self.__complexes_list.total_columns = 1

        # Place titles and lists in their columns
        ln_list_title.set_size_ratio(0.1)
        ln_list_list.set_size_ratio(0.9)
        ln_list_list.forward_dist = .03
        ln_list.set_padding(right = 0.05)

        # Create the 2 buttons
        button = ln_refresh.add_new_button(text="Refresh")
        button.register_pressed_callback(refresh_button_pressed_callback)
        
        button = ln_run.add_new_button(text="Start")
        button.text.value_selected = "Stop"
        button.text._value_selected_highlighted = "Stop"
        button.register_pressed_callback(run_button_pressed_callback)
        self.__run_button = button

        # Create a prefab that will be used to populate the lists
        self.__complex_item_prefab = nanome.ui.LayoutNode()
        self.__complex_item_prefab.layout_orientation = nanome.ui.LayoutNode.LayoutTypes.horizontal
        child = self.__complex_item_prefab.create_child_node()
        child.add_new_button()

        # Update the menu
        self.__plugin.update_menu(menu)
        self.__plugin.request_refresh()
        nanome.util.Logs.debug("Constructed plugin menu")