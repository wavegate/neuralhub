import numpy as np
import matplotlib.pyplot as plt
N = np.random.randint(1,10)
x = np.random.rand(N)
y = np.random.rand(N)

colors = 'k'
area = 20

plt.scatter(x, y, s=area, c=colors)
plt.axis([0, 1, 0, 1])

plt.show()
