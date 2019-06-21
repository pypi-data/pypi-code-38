from miniworldmaker.boards import pixel_board as pb
from miniworldmaker.boards import processing_tools as pt


class ProcessingBoard(pb.PixelBoard, pt.ProcessingTools):

    def __init__(self, columns=400, rows=300):
        super().__init__(columns=columns, rows=rows)

    def on_setup(self):
        pass





