class Box(object):
    def __init__(self, box, mode='xyxy'):
        super(Box, self).__init__()
        self.mode = mode
        if box.__class__.__name__=='Box':
            for name,value in vars(box).items():
                setattr(self, name, value)
            return
        if mode=='xyxy':
            self.box_xyxy = list(map(int, box))
            self.box_xywh = [box[0], box[1], box[2]-box[0], box[3]-box[1]]
            self.w = box[2]-box[0]
            self.h = box[3]-box[1]
            self.xctr = int((box[2]+box[0]) / 2)
            self.yctr = int((box[3]+box[1]) / 2)
        elif mode=='xywh':
            self.box_xywh = list(map(int, box))
            self.box_xyxy = [box[0], box[1], box[2]+box[0], box[3]+box[1]]
            self.w = box[2]
            self.h = box[3]
            self.xctr = int(box[2]/2+box[0])
            self.yctr = int(box[3]/2+box[1])
        else:
            print('Not supported mode.')
            raise

    def xyxy(self):
        self.mode = 'xyxy'
        return self.box_xyxy

    def xywh(self):
        self.mode = 'xywh'
        return self.box_xywh

    def __getitem__(self, index):
        return getattr(self, 'box_{}'.format(self.mode))[index]

    def __str__(self):
        return 'Box(' + str(getattr(self, 'box_{}'.format(self.mode))) + ')'

    def add_field(self, field_name, value):
    	setattr(self, field_name, value)

    def get_field(self, field_name):
    	return getattr(self, field_name)

class BoxList(object):
    def __init__(self, boxlist, mode='xyxy'):
        if boxlist.__class__.__name__=='BoxList':
            for name,value in vars(boxlist).items():
                setattr(self, name, value)
            return
        self.boxes = [Box(b, mode) for b in boxlist]

    def __getitem__(self, index):
        return self.boxes[index]

    def __len__(self):
        return len(self.boxes)

    def __str__(self):
        info_list = [b.__str__() for b in self.boxes]
        return 'BoxList(\n' + ',\n'.join(info_list) + '\n)'

    def add_field(self, field_name, value):
        setattr(self, field_name, value)

    def get_field(self, field_name):
        return getattr(self, field_name)

if __name__=='__main__':
    a = [1,2,3,4]
    b = Box(a)
    c = Box(b)
    print(b)
    print(c)
    print(b==c)
    print(b is c)

    bl = BoxList([[1,2,3,4],[5,6,7,8]])
    bl2 = BoxList(bl)
    print(bl2)
    print(bl[0])
    x = bl[0].xyxy()
    print(bl[0][2])

    for i in bl:
        for j in i:
            print(j)

