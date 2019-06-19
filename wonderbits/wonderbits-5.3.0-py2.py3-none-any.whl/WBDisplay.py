from .wbits import Wonderbits





class Display(Wonderbits):
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_button(self, cb):
        self._register_event('display{}'.format(self.index), 'button', cb)
    
    def print(self, row, column, text, size = None):
        """
        固定位置显示

        :param row: 显示行数：1~16
        :param column: 显示列数：1~15
        :param text: 显示内容，可以是字符串，整数，小数
        :param size: 设置显示的大小，不填写此参数默认为小号字体  SIZE_SMALL为小号字体，值为2 SIZE_BIG为大号字体不支持汉字，值为4
        """

        text = str(text).replace('"', '\\"')
        text = "\"" + text + "\""
        args = []
        args.append(str(row))
        args.append(str(column))
        args.append(str(text))
        if size != None:
            args.append(str(size))
        command = "display{}.print({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_dot(self, x, y, page = None, save = None, color = None):
        """
        画点

        :param x: X轴坐标：1~120
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认画点在第1页
        :param save: 设置画点内容是否保存，不填写此参数默认为不保存  DRAW_NORMAL 为不保存画点内容，值为0 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容将不存在 2. 不能与print在同一页显示   DRAW_SAVED 为保存画点内容，值为1 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容仍会存在 2. 可与print在同一页显示，显示位置冲突时以画点内容为主 3. 使用清屏函数可以清除这样的点
        :param color: 设置显示点的颜色  有色点值为1 无色点值为0
        """

        args = []
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        if save != None:
            args.append(str(save))
        if color != None:
            args.append(str(color))
        command = "display{}.draw_dot({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_line(self, head_x, head_y, tail_x, tail_y, page = None, save = None, color = None):
        """
        画线

        :param head_x: 起始点X轴坐标：1~120
        :param head_y: 起始点Y轴坐标：1~32
        :param tail_x: 终止点X轴坐标：1~120
        :param tail_y: 终止点Y轴坐标：1~32
        :param page: 显示页数：1~8  默认画线在第1页
        :param save: 设置画点内容是否保存，不填写此参数默认为不保存  DRAW_NORMAL 为不保存画点内容，值为0 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容将不存在 2. 不能与print在同一页显示   DRAW_SAVED 为保存画点内容，值为1 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容仍会存在 2. 可与print在同一页显示，显示位置冲突时以画点内容为主 3. 使用清屏函数可以清除这样的点
        :param color: 设置显示点的颜色  有色点值为1 无色点值为0
        """

        args = []
        args.append(str(head_x))
        args.append(str(head_y))
        args.append(str(tail_x))
        args.append(str(tail_y))
        if page != None:
            args.append(str(page))
        if save != None:
            args.append(str(save))
        if color != None:
            args.append(str(color))
        command = "display{}.draw_line({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_chart(self, x, y, page = None, save = None, color = None):
        """
        根据点坐标画折线使用此函数会以上一次调用的坐标为起点，本次的坐标为终点划线如果是第一次使用则是在该坐标画一个点

        :param x: X轴坐标：1~120
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认画点在第1页
        :param save: 设置画点内容是否保存，不填写此参数默认为不保存  DRAW_NORMAL 为不保存画点内容，值为0 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容将不存在 2. 不能与print在同一页显示   DRAW_SAVED 为保存画点内容，值为1 1. 当某页显示画点内容，转到其他页码再转回曾显示画点的页码画点内容仍会存在 2. 可与print在同一页显示，显示位置冲突时以画点内容为主 3. 使用清屏函数可以清除这样的点
        :param color: 设置显示点的颜色  有色点值为1 无色点值为0
        """

        args = []
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        if save != None:
            args.append(str(save))
        if color != None:
            args.append(str(color))
        command = "display{}.draw_chart({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def turn_to_page(self, page):
        """
        转到某页

        :param page: 跳转到的页码：1~8
        """

        args = []
        args.append(str(page))
        command = "display{}.turn_to_page({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def clear_page(self, page = None):
        """
        清除某页

        :param page: 清除的页码：1~8  默认清除第1页
        """

        args = []
        if page != None:
            args.append(str(page))
        command = "display{}.clear_page({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def clear_all_pages(self, block = None):
        """
        清除全部8页屏幕的内容

        :param block: 阻塞参数：  False表示不阻塞 True表示阻塞
        """

        args = []
        if block != None:
            args.append(str(block))
        command = "display{}.clear_all_pages({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def get_button_state(self):
        """
        该函数用于获取翻页按钮状态:rtype: int
        """

        command = 'display{}.get_button_state()'.format(self.index)
        return self._get_command(command)
    
    def disable_page_turning(self):
        """
        禁止翻页按键功能在开启翻页按键功能的情况下使用该函数可以禁止翻页按键功能，禁止翻页按键功能后将不能通过翻页按键来切换不同页码的显示内容，只能使用turn_to_page函数来切换页码系统默认开启翻页按键功能

        """

        args = []
        command = "display{}.disable_page_turning({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def enable_page_turning(self):
        """
        开启翻页按键功能在禁止翻页按键功能的情况下使用该函数可以开启翻页按键功能系统默认开启翻页按键功能

        """

        args = []
        command = "display{}.enable_page_turning({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_direction_reverse(self):
        """
        设置显示方向为翻转显示方向，使用该函数后显示内容将会进行180°翻转

        """

        args = []
        command = "display{}.set_direction_reverse({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def set_direction_regular(self):
        """
        设置显示方向为系统默认显示方向

        """

        args = []
        command = "display{}.set_direction_regular({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def hide_scrollbar(self):
        """
        隐藏页码滚动指示条，使用该函数后将不会再显示内容界面看到页码滚动指示条系统默认显示页码滚动指示条

        """

        args = []
        command = "display{}.hide_scrollbar({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def show_scrollbar(self):
        """
        显示页码滚动指示条系统默认显示页码滚动指示条

        """

        args = []
        command = "display{}.show_scrollbar({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def disable_auto_refresh(self):
        """
        禁止自动刷新显示功能在禁止自动刷新显示功能后只能靠手动刷新显示界面实现更新显示内容系统默认开启自动刷新显示功能

        """

        args = []
        command = "display{}.disable_auto_refresh({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def enable_auto_refresh(self):
        """
        开启自动刷新显示功能在开启自动刷新显示功能后系统将智能识别当前显示内容是否需要更新，如果需要则会更新显示内容系统默认开启自动刷新显示功能

        """

        args = []
        command = "display{}.enable_auto_refresh({})".format(self.index, ",".join(args))
        self._set_command(command)

    
    def refresh(self):
        """
        更新显示内容在禁止自动刷新显示功能后只能靠该函数来实现手动刷新显示界面实现更新显示内容系统默认开启自动刷新显示功能

        """

        args = []
        command = "display{}.refresh({})".format(self.index, ",".join(args))
        self._set_command(command)

    