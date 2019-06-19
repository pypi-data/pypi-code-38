import nanome
from nanome.util import Logs
from nanome.api.structure import Complex

from ._WebLoaderServer import _WebLoaderServer
from . import _WebLoaderMenu
from .PPTReader import PPTReader
import os
import socket
from timeit import default_timer as timer

SERVER_PORT = 80

# Plugin instance (for Nanome)
class WebLoader(nanome.PluginInstance):
    def start(self):
        self._web_loader_menu = _WebLoaderMenu._WebLoaderMenu(self)
        self._web_loader_menu.build_menu(WebLoader.get_server_url())
        self.__refresh()
        self.__timer = timer()
        self._ppt_reader = None

    def update(self):
        if self._ppt_reader:
            self._ppt_reader.update()
        if (self._web_loader_menu.is_open()):
            if timer() - self.__timer >= 3.0:
                self.__refresh()
                self.__timer = timer()

    def select_menu(self, menu):
        self.menu = menu
        self.menu.enabled = True
        self.update_menu(self.menu)

    def __refresh(self):
        file_list = [filename for filename in os.listdir(os.path.join(os.path.dirname(__file__), '_WebLoader')) if _WebLoaderServer.file_filter(filename)]
        self._web_loader_menu.update_list(file_list)

    def on_run(self):
        self._web_loader_menu.open_menu()

    def load_molecule(self, name):
        extension = name.split(".")[-1]
        file_path = os.path.join(os.path.dirname(__file__), '_WebLoader/') + name
        if extension == "pdb":
            complex = Complex.io.from_pdb(path=file_path)
            self.add_bonds([complex], self.bonds_ready)
            return
        elif extension == "sdf":
            complex = Complex.io.from_sdf(path=file_path)
            self.bonds_ready([complex])
        elif extension == "cif":
            complex = Complex.io.from_mmcif(path=file_path)
            self.add_bonds([complex], self.bonds_ready)
            return
        elif extension == "ppt" or extension == "pptx" or extension == "pdf":
            with open(file_path) as ppt:
                self.display_ppt(ppt)
        else:
            Logs.warning("Unknown file extension for file", name)
            return

    def bonds_ready(self, complex_list):
        self.add_dssp(complex_list, self.send_complexes)

    def send_complexes(self, complex_list):
        self.add_to_workspace(complex_list)

    @staticmethod
    def get_server_url():
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('10.255.255.255', 1))
            ip = s.getsockname()[0]
        except:
            ip = '127.0.0.1'
        finally:
            s.close()

        if SERVER_PORT != 80:
            ip += ":" + str(SERVER_PORT)
        return ip

    def display_ppt(self, file):
        if (self._ppt_reader == None):
            self._ppt_reader = PPTReader(self, lambda _=None : self._web_loader_menu.open_menu())
        self._ppt_reader.set_ppt(file)
        self._ppt_reader.open_menu()

def main():
    # Plugin server (for Web)
    server = _WebLoaderServer(SERVER_PORT)
    server.start()

    # Plugin
    plugin = nanome.Plugin("Load from Web", "Gives access to a folder of molecules that can be modified by a Web UI", "Loading", False)
    plugin.set_plugin_class(WebLoader)
    plugin.run('127.0.0.1', 8888)

if __name__ == "__main__":
    main()