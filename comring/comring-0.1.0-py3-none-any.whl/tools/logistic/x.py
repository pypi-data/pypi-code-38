from comring.lib import tool

class X(tool.SimpleTool):
    def main(self):
        self.write('stock.location.route', [1338], {
            'warehouse_ids': [6, False, [4, 277, 285, 286, 287, 253]]
        })

if __name__ == '__main__':
    x = X()
    x.bootstrap()
    x.connect()
    x.main()
