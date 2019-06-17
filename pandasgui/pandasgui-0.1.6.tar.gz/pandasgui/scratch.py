from pandasgui import show
import pandas as pd

tel = list('ABC')
step = list('DEFGH')
df = pd.DataFrame(data=pd.np.random.randn(15, 5),
                 index=pd.MultiIndex.from_product([tel, step], names=['tel', 'step']),
                 columns=list('IJKLM'))
show(df)