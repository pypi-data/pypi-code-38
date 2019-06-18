import nanome
from nanome.util import Logs

import os
import tempfile
import traceback
import subprocess
from sys import platform

class PPTReader(object):

    def __init__(self, plugin, close = lambda : None):
        self.__plugin = plugin
        self.close = close
        self.update_content = plugin.update_content
        self.update_menu = plugin.update_menu
        self._images_nb = 0
        self._base_name = ""
        self._build_menu()
        self.__reset_state()

    def set_ppt(self, ppt):
        self.__reset_state()
        self._ppt_file = ppt
        self._request_pending = True
        name = self._ppt_file.name
        self._base_name = tempfile.NamedTemporaryFile().name
        if platform == "win32" and (name.endswith(".pptx") or name.endswith(".ppt") or name.endswith(".odp")):
            self._tmp_dir = tempfile.TemporaryDirectory()
            self._step = 1
        else:
            self._step = 2

    def open_menu(self):
        self.__plugin.select_menu(self.__menu)

    def is_open(self):
        return self.__plugin.menu == self.__menu

    def __del__(self):
        try:
            os.remove(self._tmp_dir)
        except:
            pass
        if self._base_name != "":
            for i in range(self._images_nb):
                try:
                    os.remove(self._base_name + '-pptreader-' + str(i) + '.jpg')
                except:
                    pass

    def __reset_state(self):
        self.__del__()
        self._tmp_dir = None
        self._request_pending = False
        self._running = False
        self._current_image = 0
        self._images_nb = 0
        self._base_name = ""
        self._image.file_path = os.path.join(os.path.dirname(__file__), 'placeholder.png')

    def _build_menu(self):
        def left(btn):
            self._display_image(self._current_image - 1)

        def right(btn):
            self._display_image(self._current_image + 1)

        menu = nanome.ui.Menu.io.from_json(os.path.join(os.path.dirname(__file__), 'ppt_reader.json'))
        self.__menu = menu

        root = menu.root
        #dont need browser_panel for this plugin
        _browser_panel = root.find_node("browser_panel", True)
        _browser_panel.enabled = False
        _pres_panel = root.find_node("pres_panel", True)
        _pres_panel.enabled = True

        self._left_arrow = root.find_node("left_arrow", True).get_content()
        self._left_arrow.unusable = True
        self._left_arrow.register_pressed_callback(left)

        self._right_arrow = root.find_node("right_arrow", True).get_content()
        self._right_arrow.unusable = True
        self._right_arrow.register_pressed_callback(right)

        self._image = root.find_node("image", True).create_child_node().add_new_image()
        self._image.file_path = os.path.join(os.path.dirname(__file__), 'placeholder.png')
        self._image.scaling_option = nanome.util.enums.ScalingOptions.fit

        root.find_node("close", True).get_content().register_pressed_callback(self.close)

        # Create a prefab that will be used to populate the list
        self._item_prefab = nanome.ui.LayoutNode()
        child = self._item_prefab.create_child_node()
        child.name = "button_node"
        child.add_new_button()

        self.update_menu(menu)

    def _display_image(self, idx):
        if idx <= 0:
            idx = 0
            if self._left_arrow.unusable == False:
                self._left_arrow.unusable = True
                self.update_content(self._left_arrow)
        elif self._left_arrow.unusable == True:
                self._left_arrow.unusable = False
                self.update_content(self._left_arrow)

        if idx >= self._images_nb - 1:
            idx = self._images_nb - 1
            if self._right_arrow.unusable == False:
                self._right_arrow.unusable = True
                self.update_content(self._right_arrow)
        elif self._right_arrow.unusable == True:
                self._right_arrow.unusable = False
                self.update_content(self._right_arrow)

        self._current_image = idx

        self._image.file_path = self._base_name + '-pptreader-' + str(idx) + '.jpg'
        self.update_content(self._image)

    ### Conversion Process ###

    def update(self):
        if self._request_pending == False:
            return

        if self._running == False:
            self._start_conversion()
        elif self._check_conversion():
            self._conversion_finished()

    def _start_conversion(self):
        if platform == "linux" or platform == "linux2":
            args = ['convert', '-density', '288', self._ppt_file.name, self._base_name + '-pptreader-%d.jpg']
        elif platform == "darwin":
            Logs.error("Plugin not compatible with Mac OS yet")
        elif platform == "win32":
            if self._step == 1:
                args = ['simpress.exe', '--headless', '--invisible', '--convert-to', 'pdf', '--outdir', self._tmp_dir.name, self._ppt_file.name]
            else:
                if self._tmp_dir != None:
                    input = os.path.join(self._tmp_dir.name, '*.pdf')
                else:
                    input = self._ppt_file.name
                args = ['magick', '-density', '288', input, self._base_name + '-pptreader-%d.jpg']

        Logs.debug("Starting conversion with args:", args)
        try:
            self._process = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except:
            nanome.util.Logs.error("Couldn't convert:", traceback.format_exc())
            self._request_pending = False
            self._running = False
            self.close()
        self._running = True

    def _check_conversion(self):
        return self._process.poll() != None
                        
    def _conversion_finished(self):
        if platform == "win32" and self._step == 1:
            self._running = False
            self._step = 2
            return

        self._request_pending = False
        self._running = False
        try:
            (results, errors) = self._process.communicate()
            if len(errors) == 0:
                for result in results:
                    for line in result.split('\n'):
                        nanome.util.Logs.debug(line)
            else:
                for line in errors.splitlines():
                    nanome.util.Logs.error(line.decode("utf-8"))

                self.close()
                return
        except:
            pass

        i = 0
        is_file = True
        while is_file:
            is_file = os.path.isfile(self._base_name + '-pptreader-' + str(i) + '.jpg')
            i += 1
        i -= 1

        if i < 0:
            nanome.util.Logs.error("No file generated by conversion")
            self.close()
            return

        self._images_nb = i
        self._current_image = 0
        self._display_image(0)