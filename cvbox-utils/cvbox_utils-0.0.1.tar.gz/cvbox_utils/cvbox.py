
class Box(object):
    def __init__(self, box, mode='xyxy'):
        super(Box, self).__init__()
        self.mode = mode
        if mode=='xyxy':
            self.box_xyxy = list(map(int, box))
            self.box_xywh = [box[0], box[1], box[2]-box[0], box[3]-box[1]]
            self.w = box[2]-box[0]
            self.h = box[3]-box[1]
        elif mode=='xywh':
            self.box_xywh = list(map(int, box))
            self.box_xyxy = [box[0], box[1], box[2]+box[0], box[3]+box[1]]
            self.w = box[2]
            self.h = box[3]
        else:
            print('Not supported mode.')
            raise

    def xyxy(self):
        self.mode = 'xyxy'
        return self.xyxy

    def xywh(self):
        self.xywh = 'xywh'
        return self.xywh

    def __getitem__(self, index):
        assert index < 4, 'index out of range'
        return getattr(self, 'box_{}'.format(self.mode))[index]

    def add_field(self, field_name, value):
    	setattr(self, field_name, value)

    def get_field(self, field_name):
    	return getattr(self, field_name)

class BoxList(object):
    def __init__(self, boxlist, mode):
        self.boxes = [Box(b, mode) for b in boxlist]

    def __len__(self):
        return len(self.boxes)

if __name__=='__main__':
    a = [1,2,3,4]
    b = Box(a)
    print(b[2])