import CLI

class App(CLI.CLI):
    """
    Insert Usage information
    and help here
    """
    def __init__(self):
        super().__init__('app.json','add','remove','list')

    def add(self,args):
        name = args[0]
        balance = args[1]
        self.state[name] = balance

    def remove(self,args):
        name = args[0]
        del self.state[name]

    def list(self,*args):
        for i in self.state.keys():
            print("Name: {}\nBalance: {}".format(i,self.state[i]))

if __name__ == '__main__':
    app = App()
    app.run()
