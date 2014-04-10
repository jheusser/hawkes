import pandas
import numpy as np
import datetime

from bisect import bisect_left

alpha = 0.1
beta = 1
mu = 0.5

def instant_rate(t, x):
  """Computes instantenous intensity rate at arbitrary times x given trade times t. """
  reg = 0 
  idx = bisect_left(t, x)

  for j in reversed(range(0, idx)):
      d = np.array(x - t[0:idx])
      reg += alpha * np.sum(np.exp(-beta*d))
  return mu + reg

def rate_series(t, x):
  return [instant_rate(t, each) for each in x]

all_trades = pandas.read_csv('./data/all_trades.csv', parse_dates=[0], index_col=0)
usd_trades = all_trades[all_trades['d.currency'] == 'USD']

usd_counts = pandas.DataFrame({'counts': np.ones(len(usd_trades))}, index=usd_trades.index)
residuals = pandas.read_csv('./data/residuals.csv', index_col=0)

# Index of series above. About 6.7 hours. In minutes thats 402 minutes.
# [2013-04-20 13:11:04, ..., 2013-04-20 19:57:04]
# 
empirical_1min = usd_counts.resample('1min', how='sum')

### read in fitted data from R and adjust index
fitted = pandas.read_csv('./data/fitted_intensities_actual_times_large.csv', index_col=0)
index = map(lambda x: datetime.datetime.fromtimestamp(float(x)-3600), fitted.index)
fitted.index = index

fitted_1min = fitted.resample('1min', how='sum')

pandas.DataFrame({'fitted': fitted_1min.data.values, 'empirical': empirical_1min.counts.values}).plot()


## plot settings
import matplotlib as mpl
import matplotlib.pyplot as plt
mpl.rc('font', **{'sans-serif':'Verdana','family':'sans-serif','size':8})
mpl.rcParams['xtick.direction'] = 'out'
mpl.rcParams['ytick.direction'] = 'out'
mpl.rcParams['axes.linewidth'] = 0.75

## simulated hawkes process
t =  [0.5, 1.1, 1.5, 1.8, 3.9, 7.2, 8.2, 8.8]
x = np.linspace(0, 10)

fig, ax = plt.subplots(figsize=(8,4))

ax.plot(x,rate_series(t, x))
ax.plot(t, [0.05]*len(t), '|', color='k')

ax.set_title('Simulated Arrival Intensity')
ax.set_xlabel('Time')
ax.set_ylabel('Intensity')

fig.tight_layout()

plt.draw()

## empirical trade counts
ax = empirical_1min.fillna(method='pad').plot()

ax.set_xlabel('Time')
ax.set_ylabel('Trades')
ax.set_title('Empirical trade counts')

plt.draw()


## empirical vs fitted
ax = pandas.DataFrame({'fitted': fitted_1min.data.values, 'empirical': empirical_1min.counts.values}).plot()

ax.set_ylabel('Intensity rate')
ax.set_xlabel('Time')
ax.set_title('Fitted vs Empirical Intensities')

plt.draw()
plt.show()

## QQ plot of residuals
import scipy.stats as stats
stats.probplot(residuals['residuals'].diff().dropna(), dist='expon', plot=plt, fit=True)

ax = plt.axes()
ax.set_title('Residual Interevent Times')

plt.draw()
plt.show()
