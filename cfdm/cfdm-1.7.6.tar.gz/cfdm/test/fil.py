import cfdm, re; q, t = cfdm.read('/home/david/cfdm/docs/_downloads/file.nc')

c = t.cell_methods
x = c.filter_by_type('domain_axis')
xi1 = x.inverse_filter()
xi2 = xi1.inverse_filter()

print c
print x
print xi1
print xi2
print xi2.inverse_filter()
