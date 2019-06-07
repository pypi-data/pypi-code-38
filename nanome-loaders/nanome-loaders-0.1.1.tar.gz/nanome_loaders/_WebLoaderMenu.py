import nanome

class _WebLoaderMenu():
    def __init__(self, plugin):
        self.__plugin = plugin
        self.__selected_file = None

    def build_menu(self, url_text):
        # Called when load button is clicked
        def load_button_pressed_callback(button):
            if self.__selected_file != None:
                self.__plugin.load_molecule(self.__selected_file.text.value_idle)

        # Request and set menu window
        menu = self.__plugin.menu
        menu.title = "Web Files"
        self.__menu = menu

        # Create all needed layout nodes
        menu.root.clear_children()
        content = menu.root.create_child_node()
        ln_url_text = content.create_child_node()
        ln_url_text.set_size_ratio(0.10)
        ln_list = content.create_child_node()
        ln_list.set_size_ratio(0.75)
        ln_list.set_padding(top=0.016, down=0.016)
        ln_button = content.create_child_node()
        ln_button.set_size_ratio(0.15)

        # Create the URL text
        url_text = ln_url_text.add_new_label(text="Add files by visiting \"" + url_text + "\" in your browser")

        # Create the list
        self._file_list = ln_list.add_new_list()
        self._file_list.display_columns = 1
        self._file_list.display_rows = 7
        self._file_list.total_columns = 1

        # Create the load button
        load_btn = ln_button.add_new_button(text="Load")
        load_btn.register_pressed_callback(load_button_pressed_callback)

        # Create a prefab that will be used to populate the list
        self._item_prefab = nanome.ui.LayoutNode()
        self._item_prefab.layout_orientation = nanome.ui.LayoutNode.LayoutTypes.horizontal
        child = self._item_prefab.create_child_node()
        child.name = "button_node"
        child.add_new_button()

        # Update menu
        self.__plugin.update_menu(self.__menu)

    def open_menu(self):
        self.__menu.enabled = True
        self.__plugin.update_menu(self.__menu)

    def update_list(self, file_list):
        # Called when a button is clicked in the list
        def btn_pressed(button):
            last_selected = self.__selected_file
            if last_selected == button:
                return

            if last_selected != None:
                last_selected.selected = False
                self.__plugin.update_content(last_selected)

            button.selected = True
            self.__selected_file = button
            self.__plugin.update_content(button)
        
        list_items = self._file_list.items

        for i in range(len(list_items) - 1, -1, -1):
            try:
                idx = file_list.index(list_items[i].get_children()[0].get_content().text.value_idle)
                del file_list[idx]
            except ValueError:
                if list_items[i].get_children()[0].get_content().selected:
                    self.__selected_file = None
                del list_items[i]

        for file in file_list:
            clone = self._item_prefab.clone()
            ln_btn = clone.get_children()[0]
            btn = ln_btn.get_content()
            btn.set_all_text(file)
            btn.register_pressed_callback(btn_pressed)
            list_items.append(clone)

        self.__plugin.update_content(self._file_list)