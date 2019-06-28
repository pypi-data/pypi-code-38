import matplotlib
matplotlib.use('Agg')

import matplotlib.pyplot as plt
import astropy.units as u
from nexoclom import Input, Output
from MESSENGERuvvs import MESSENGERdata

npack = 1e5
orbit = 36

inputsfile = 'Na.Gaussian.3_1.input'
inputs = Input(inputsfile)
inputs.run(npack, overwrite=False)

imformat = 'MercuryEmission.format'
image = inputs.produce_image(imformat)
image.display(savefile=inputsfile.replace('.input', '_radiance.png'),
              show=False)

colformat = 'MercuryColumn.format'
column = inputs.produce_image(colformat)
column.display(savefile=inputsfile.replace('.input', '_column.png'),
              show=False)

# (4) Make the modeled version
data = MESSENGERdata(inputs.options.atom, f'orbit={orbit}')
data.model(inputs, npack, dphi=3*u.deg)
lab = f'Model ({data.modelstrength:6.2f} $\times 10^{26} atoms/s$)'

plt.plot(data.data.utc, data.data.radiance, label='Data')
plt.plot(data.data.utc, data.data.model, label=lab)
plt.savefig(inputsfile.replace('.input', f'_orbit{orbit}_model.png'))
plt.close()


