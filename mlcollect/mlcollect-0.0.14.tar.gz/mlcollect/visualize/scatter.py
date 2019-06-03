import matplotlib.pyplot as plt
from sklearn.manifold import TSNE

def point_scatter(colors, X, Y, c):
    tsne = TSNE(n_components=2, random_state=0)
    X = tsne.fit_transform(X)
    plt.figure(figsize=(6, 5))
    plt.scatter(X, Y, c=c)
    plt.legend()
    plt.show()
