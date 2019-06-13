from pprint import pprint

from pyshipping.package import Package
from pyshipping.binpack_simple import binpack


class BinPack:
    def __init__(self):
        self.bins = []
        self.bin_lookup = {}
        self.packages = []
        self.oversize = []
        self.min_bin_size = -1
        self.options = []

    def add_bin(self, id, price, height, width, depth):
        # add bin
        pkg = Package((height, width, depth))
        self.bins.append({
            'id': id,
            'price': price,
            'pkg': pkg,
        })

        # sort bins, cheapest first
        self.bins = sorted(self.bins, key=lambda x: (x['price']))

        # update bin lookup
        for i, b in enumerate(self.bins):
            self.bin_lookup[b['id']] = i

    def add_package(self, meta, height, width, depth):
        pkg = Package((height, width, depth))

        # set smallest container size
        oversize = True
        for i, b in enumerate(self.bins):
            good, bad = binpack([pkg], b['pkg'])
            if len(good) == 1:
                oversize = False
                if i > self.min_bin_size:
                    self.min_bin_size = i
                break

        # add to appropriate list
        if oversize:
            self.oversize.append({
                'meta': meta,
                'pkg': pkg
            })
        else:
            self.packages.append({
                'meta': meta,
                'min_bin_size': i,
                'pkg': pkg,
            })

        # sort packages, largest volume first
        self.packages = sorted(
            self.packages,
            key=lambda x: x['pkg'].volume,
            reverse=True
        )

    def calculate(self, bin_sizes):
        containers = []

        for p in self.packages:
            containers.append({
                'contents': {
                    'meta': [],
                    'packages': [],
                },
                'id': self.bins[bin_sizes[-1]]['id'],
            })

        # loop through packages
        for p in self.packages:
            for c in containers:
                good, bad = binpack(
                    c['contents']['packages'] + [p['pkg']],
                    self.bins[self.bin_lookup[c['id']]]['pkg']
                )
                if len(good) == 1:
                    c['contents']['packages'] += [p['pkg']]
                    c['contents']['meta'] += [p['meta']]
                    break

        # remove empty bins
        for i in reversed(range(len(containers))):
            if len(containers[i]['contents']['packages']) == 0:
                containers.pop()

        # attempt to reduce the size of the bins
        for c in containers:
            for b in self.bins:
                good, bad = binpack(c['contents']['packages'], b['pkg'])
                if len(good) == 1 and len(bad) == 0:
                    c['id'] = b['id']
                    break

        return containers

    def go(self):
        tmp = []
        results = []

        # calculate bin size combinations
        bin_sizes = list(range(self.min_bin_size, len(self.bins)))
        while len(bin_sizes) > 0:
            tmp.append(self.calculate(bin_sizes))
            bin_sizes.pop()

        # calculate prices
        for t in tmp:
            total_price = 0
            for c in t:
                c['price'] = self.bins[self.bin_lookup[c['id']]]['price']
                total_price += c['price']

            results.append({
                'price': total_price,
                'number_of_packages': len(t),
                'packages': t
            })

        # remove duplicate options
        duplicates = []
        for r in results:
            s = '%s:%s' % (r['number_of_packages'], r['price'])
            if s not in duplicates:
                duplicates.append(s)
            else:
                r['duplicate'] = True
        results = [r for r in results if 'duplicate' not in r]

        # sort prices, cheapest first
        results = sorted(
            results,
            key=lambda x: (x['price'], x['number_of_packages']),
        )

        return {
            'results': results,
            'oversize': [o['meta'] for o in self.oversize]
        }

    def debug(self):
        pprint({
            'min_bin_size': self.min_bin_size,
            'bins': self.bins,
            'packages': self.packages,
            'oversize': self.oversize,
            'bin_lookup': self.bin_lookup
        })

"""
bp = BinPack()

bp.add_bin('S', 35, 140, 200, 60)
bp.add_bin('M', 65, 170, 250, 90)
bp.add_bin('L', 75, 200, 300, 110)

bp.add_package('A', 125, 180, 11)
bp.add_package('B', 125, 180, 12)
bp.add_package('C', 148, 209, 36)
bp.add_package('D', 208, 280, 12)

# bp.debug()
pprint(bp.go())
"""
