from utils.constant_singleton import ConstantSingletonMetaclass

class Constant(metaclass=ConstantSingletonMetaclass):
    def __init__(self, val):
        self.val = val

    def __call__(self):
        return self.val

def main():
    c = Constant(4)
    print(c())

def second():
    c = Constant(10)

    print(c())

if __name__ == '__main__':
    main()
    second()