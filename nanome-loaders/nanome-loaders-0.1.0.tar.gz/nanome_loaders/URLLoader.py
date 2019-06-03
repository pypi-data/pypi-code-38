import requests
import tempfile
import traceback
import os

import nanome
from nanome.util import Logs

##################
##### CONFIG #####
##################

url = "https://files.rcsb.org/download/{{NAME}}.cif" # {{NAME}} indicates where to write molecule code
type = "MMCIF" # PDB / SDF / MMCIF

##################
##################
##################

class URLLoader(nanome.PluginInstance):
    def start(self):
        def btn_click(button):
            self.load_molecule(self.__field.input_text)

        # Request and set menu window
        menu = self.menu
        menu.title = "URL Loader"
        menu._width = 0.8
        menu._height = 0.7
        menu.enabled = True

        # Create all needed layout nodes
        menu.root.clear_children()
        content = menu.root.create_child_node()
        ln_field = content.create_child_node()
        ln_field.forward_dist = .03 # TMP, should be fixed soon
        ln_field.set_padding(top=0.07, down=0.04)
        ln_button = content.create_child_node()
        ln_button.set_padding(top=0.1)

        # Create the text field
        self.__field = ln_field.add_new_text_input()
        self.__field.placeholder_text = "Molecule Code"

        # Create the load button
        btn = ln_button.add_new_button(text="Load")
        btn.register_pressed_callback(btn_click)

        # Update menu
        self.update_menu(menu)

    # When user clicks on "Run", open menu
    def on_run(self):
        self.menu.enabled = True
        self.update_menu(self.menu)

    def load_molecule(self, code):
        url_to_load = url.replace("{{NAME}}", code)
        response = requests.get(url_to_load)
        file = tempfile.NamedTemporaryFile(delete=False)
        self._name = code
        try:
            file.write(response.text.encode("utf-8"))
            file.close()
            if type == "PDB":
                complex = nanome.structure.Complex.io.from_pdb(path=file.name)
                self.add_bonds([complex], self.bonds_ready)
            elif type == "SDF":
                complex = nanome.structure.Complex.io.from_sdf(path=file.name)
                self.bonds_ready([complex])
            elif type == "MMCIF":
                complex = nanome.structure.Complex.io.from_mmcif(path=file.name)
                self.add_bonds([complex], self.bonds_ready)
            else:
                Logs.error("Unknown file type")
        except: # Making sure temp file gets deleted in case of problem
            Logs.error("Error while loading molecule:\n", traceback.format_exc())
        os.remove(file.name)

    def bonds_ready(self, complex_list):
        self.add_dssp(complex_list, self.complex_ready)

    def complex_ready(self, complex_list):
        complex_list[0].molecular.name = self._name
        self.add_to_workspace(complex_list)

def main():
    plugin = nanome.Plugin("URL Loader", "Load molecule from database", "Loading", False)
    plugin.set_plugin_class(URLLoader)
    plugin.run('127.0.0.1', 8888)

if __name__ == "__main__":
    main()