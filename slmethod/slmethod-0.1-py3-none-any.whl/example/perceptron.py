
from sklearn.datasets import make_classification
import matplotlib.pyplot as plt
import numpy as np
from slmethod.perceptron import Perceptron

# X 为样本特征，y 为样本类别输出，共 30 个样本，每个样本 2 个特
# 输出有 2 个类别，没有冗余特征，每个类别一个簇，随机状态为小武小久
X, y = make_classification(n_samples=30,
                           n_features=2,
                           n_informative=2,
                           n_redundant=0,
                           n_classes=2,
                           n_clusters_per_class=1,
                           random_state=59)
# 处理 y 值，取值为范围 {-1, 1}
y = np.array([1 if i == 1 else -1 for i in y])

# 原始感知机
origin_model = Perceptron(dual=False)
origin_model.fit(X, y)

# 对偶形式
dual_model = Perceptron(dual=True)
dual_model.fit(X, y)

plt.scatter(X[:, 0], X[:, 1], c=y, s=40, marker='o')
minX = np.min(X[:, 0])
maxX = np.max(X[:, 0])

x_points = np.array([minX, maxX])
origin_y = -(origin_model.w[0]*x_points + origin_model.b)/origin_model.w[1]
dual_y = -(dual_model.w[0]*x_points + dual_model.b)/dual_model.w[1]
plt.plot(x_points, origin_y, label='origin')
plt.plot(x_points, dual_y, label='dual')
plt.legend()
plt.show()
