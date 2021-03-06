import numpy as np
import matplotlib.pyplot as plt

X = np.linspace(0,2.*np.pi, 1000)
results = np.zeros(100)

for i in range(1,101):
    Y = i * np.sin(X)
    var = np.var(Y)
    results[i-1] = np.exp(-((i*i)/(2*20.*20.)))

X2 = np.linspace(0,1000,1000)
Y2 = X2*X2
print Y2

plt.plot(results)
#plt.plot(Y2,'+')
plt.show()
