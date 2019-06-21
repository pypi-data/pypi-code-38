from .wbits import Wonderbits

def _format_str_type(x):
    if isinstance(x, str):
       x = str(x).replace('"', '\\"')
       x = "\"" + x + "\""
    return x

class Display(Wonderbits):
    SIZE_SMALL = 0x02
    SIZE_BIG = 0x04
    BUTTON_NONE = 0x01
    BUTTON_L = 0x02
    BUTTON_R = 0x04
    BUTTON_M = 0x08
    def __init__(self, index = 1):
        Wonderbits.__init__(self)
        self.index = index

    
    def register_button(self, cb):
        self._register_event('display{}'.format(self.index), 'button', cb)
    
    def print(self, row, column, text, size = None):
        """
        在某个位置显示内容

        :param row: 显示行数：1~16
        :param column: 显示列数：1~15
        :param text: 显示内容，可以是字符串，整数，小数
        :param size: 设置显示的大小，默认为小号字体  SIZE_SMALL：小号字体，值为2 SIZE_BIG：大号字体（不支持汉字），值为4
        """

        text = _format_str_type(text)
        
        args = []    
        args.append(str(row))
        args.append(str(column))
        args.append(str(text))
        if size != None:
            args.append(str(size))
        command = 'display{}.print({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_dot(self, x, y, page = None):
        """
        在指定坐标画一个点在画点的页使用print函数会导致已经画过的点消失切换到不同的页码在回到画点的页码也会导致已经画过的点消失

        :param x: X轴坐标：1~119
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认第1页
        """

        
        args = []    
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_dot({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_line(self, head_x, head_y, tail_x, tail_y, page = None):
        """
        通过给定坐标画线段在画线的页使用print函数会导致已经画过的线消失切换到不同的页码在回到画线的页码也会导致已经画过的线消失

        :param head_x: 起始点X轴坐标：1~119
        :param head_y: 起始点Y轴坐标：1~32
        :param tail_x: 终止点X轴坐标：1~119
        :param tail_y: 终止点Y轴坐标：1~32
        :param page: 显示页数：1~8  默认第1页
        """

        
        args = []    
        args.append(str(head_x))
        args.append(str(head_y))
        args.append(str(tail_x))
        args.append(str(tail_y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_line({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_chart(self, x, y, page = None):
        """
        画折线图以上次传入的坐标为起点，本次坐标为终点画线段。如果是首次使用，则只画单个点

        :param x: X轴坐标：1~119
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认画点在第1页
        """

        
        args = []    
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_chart({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def turn_to_page(self, page):
        """
        转到某页

        :param page: 页码：1~8
        """

        
        args = []    
        args.append(str(page))
        command = 'display{}.turn_to_page({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def clear_page(self, page = None):
        """
        清除某页显示的内容

        :param page: 清除的页码：1~8  默认第1页
        """

        
        args = []    
        if page != None:
            args.append(str(page))
        command = 'display{}.clear_page({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def clear_all_pages(self, block = None):
        """
        清除全部8页显示的内容

        :param block: 阻塞参数：  False: 不阻塞 True: 阻塞
        """

        
        args = []    
        if block != None:
            args.append(str(block))
        command = 'display{}.clear_all_pages({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def disable_page_turning(self):
        """
        禁止翻页按键功能禁止翻页按键功能后将不能通过翻页按键来切换不同页码的显示内容系统默认开启翻页按键功能

        """

        command = 'display{}.disable_page_turning()'.format(self.index)
        self._set_command(command)

    
    def enable_page_turning(self):
        """
        开启翻页按键功能系统默认开启翻页按键功能

        """

        command = 'display{}.enable_page_turning()'.format(self.index)
        self._set_command(command)

    
    def get_button_state(self):
        """
        获取翻页按钮状态:rtype: int
        """

        command = 'display{}.get_button_state()'.format(self.index)
        return self._get_command(command)

    
    def set_direction_reverse(self):
        """
        设置显示方向为翻转显示方向，使用该函数后显示内容将会进行180°翻转

        """

        command = 'display{}.set_direction_reverse()'.format(self.index)
        self._set_command(command)

    
    def set_direction_regular(self):
        """
        设置显示方向为系统默认显示方向

        """

        command = 'display{}.set_direction_regular()'.format(self.index)
        self._set_command(command)

    
    def hide_scrollbar(self):
        """
        隐藏页码滚动指示条（屏幕右边的白色小点，用于指示当前页码）系统默认显示页码滚动指示条隐藏后每行最大显示字符数由15变为16

        """

        command = 'display{}.hide_scrollbar()'.format(self.index)
        self._set_command(command)

    
    def show_scrollbar(self):
        """
        显示页码滚动指示条系统默认显示页码滚动指示条

        """

        command = 'display{}.show_scrollbar()'.format(self.index)
        self._set_command(command)

    
    def disable_auto_refresh(self):
        """
        禁止自动刷新显示功能禁止自动刷新后，只能调用刷新函数refresh()才能改变显示内容系统默认开启自动刷新显示功能

        """

        command = 'display{}.disable_auto_refresh()'.format(self.index)
        self._set_command(command)

    
    def enable_auto_refresh(self):
        """
        开启自动刷新显示功能系统默认开启自动刷新显示功能

        """

        command = 'display{}.enable_auto_refresh()'.format(self.index)
        self._set_command(command)

    
    def refresh(self):
        """
        更新一次显示内容在禁止自动刷新显示功能后只能靠此函数来更新显示内容系统默认开启自动刷新显示功能

        """

        command = 'display{}.refresh()'.format(self.index)
        self._set_command(command)

    
    def draw_save_dot(self, x, y, page = None):
        """
        在指定坐标画一个点画点后始终存在，可以使用清屏擦除可与print在同一页显示，显示位置冲突时以画点内容为主

        :param x: X轴坐标：1~119
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认第1页
        """

        
        args = []    
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_save_dot({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_save_line(self, head_x, head_y, tail_x, tail_y, page = None):
        """
        通过给定坐标画线段画线后始终存在，可以使用清屏擦除可与print在同一页显示，显示位置冲突时以画线内容为主

        :param head_x: 起始点X轴坐标：1~119
        :param head_y: 起始点Y轴坐标：1~32
        :param tail_x: 终止点X轴坐标：1~119
        :param tail_y: 终止点Y轴坐标：1~32
        :param page: 显示页数：1~8  默认第1页
        """

        
        args = []    
        args.append(str(head_x))
        args.append(str(head_y))
        args.append(str(tail_x))
        args.append(str(tail_y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_save_line({})'.format(self.index, ",".join(args))
        self._set_command(command)

    
    def draw_save_chart(self, x, y, page = None):
        """
        画折线图以上次传入的坐标为起点，本次坐标为终点画线段。如果是首次使用，则只画单个点

        :param x: X轴坐标：1~119
        :param y: Y轴坐标：1~32
        :param page: 显示页数：1~8  默认画点在第1页
        """

        
        args = []    
        args.append(str(x))
        args.append(str(y))
        if page != None:
            args.append(str(page))
        command = 'display{}.draw_save_chart({})'.format(self.index, ",".join(args))
        self._set_command(command)

    