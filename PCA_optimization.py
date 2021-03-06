# -*- coding: utf-8 -*-
"""
Created on Sun May 16 16:49:13 2021

@author: radina
"""
 
# PCA 

from sklearn.decomposition import PCA 
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


import pandas as pd
import yfinance as yf
from pandas_datareader import data as wb  #module has to be installed

#data = pd.read_csv("assets_data.csv", index_col=0)
# Import historical data

symbols = [ 'AAPL','IBM', 'JPM',
           'MCD','MSFT','NKE', 'GC=F']
snpSym = ['^GSPC']

noa = len(symbols)
data = pd.DataFrame()
snp = pd.DataFrame()

for sym in symbols:
  data[sym] = wb.DataReader(sym, data_source='yahoo',
  start='2011-01-01', end='2021-01-01')['Adj Close']

for sym in snpSym:
  snp[sym] = wb.DataReader(sym, data_source='yahoo',
  start='2011-01-01', end='2021-01-01')['Adj Close']
  
data.isna().sum()
data = data.fillna(method='ffill') #fill na with last observation carried forward

#rename gold column
data = data.rename(columns={'GC=F': 'GOLD'})
#change index types to datetime
data.index=data.index.astype('datetime64[ns]')
snp.index=snp.index.astype('datetime64[ns]')

indu_ret_idx = snp.pct_change()
indu_ret_idx.columns =['snp']
indu_ret_idx = indu_ret_idx[1:] # skip the first row (NaN)

rets = np.log(data / data.shift(1))
rets_benchmark = np.log(snp / snp.shift(1))


# calculate stock covariance
stocks_ret = data.pct_change()
stocks_ret = stocks_ret[1:] # skip the first row (NaN)
stocks_cov = stocks_ret.cov()

sklearn_pca = PCA(n_components=3) 
pc = sklearn_pca.fit_transform(stocks_ret)

# plot the variance explained by pcs
fig = plt.figure(figsize=(12,6))
fig.add_subplot(1,2,1)
plt.bar(np.arange(sklearn_pca.n_components_), 100 * sklearn_pca.explained_variance_ratio_)
plt.title('Relative information content of PCA components')
plt.xlabel("PCA component number")
plt.ylabel("PCA component variance %")

# check the explained variance reatio
sklearn_pca.explained_variance_ratio_

# get the Principal components
pcs =sklearn_pca.components_

# first component
pc1 = pcs[0,:]
# normalized to 1 
pc_w = np.asmatrix(pc1/sum(pc1)).T

# apply our first componenet as weight of the stocks
pc1_ret = stocks_ret.values*pc_w

# plot the total return index of the first PC portfolio
pc_ret = pd.DataFrame(data =pc1_ret, index= stocks_ret.index)
pc_ret_idx = pc_ret+1
pc_ret_idx= pc_ret_idx.cumprod()
pc_ret_idx.columns =['pc1']


pc_ret_idx['snp'] = snp['^GSPC']
pc_ret_idx.plot(subplots=True,title ='PC portfolio vs Market',layout=[1,2],figsize=(10,5))

# plot the weights in the PC
portfolio_pca = pd.DataFrame(data = pc_w*100,index = data.columns)
portfolio_pca.columns=['weights']
portfolio_pca.plot.bar(title='PCA portfolio weights',rot =45,fontsize =8)

portfolio_pca=portfolio_pca.drop("GOLD")

fig = plt.figure(figsize =(10, 7))
plt.pie(portfolio_pca['weights'], labels = portfolio_pca.index, autopct='%1.1f%%', startangle = 90)
plt.show() 
# a function for major portfolio statistics
def statistics(weights):
 weights = np.array(weights)
 pret = np.sum(rets.mean() * weights) * 252
 pvol = np.sqrt(np.dot(weights.T, np.dot(rets.cov() * 252, weights)))
 return np.array([pret, pvol, pret / pvol])
#check statistics
portfolio_pca = pd.DataFrame(data = pc_w*100,index = data.columns)
portfolio_pca.columns=['weights']

weights_arr=portfolio_pca['weights'].to_numpy()
weights_arr=weights_arr.ravel()
weights_arr=weights_arr/100
pca_stat=statistics(weights_arr.round(3))
pca_stat
#compare to Monte Carlo portfolio
n_groups = 3
# create plot
fig, ax = plt.subplots()
index = np.arange(n_groups)
bar_width = 0.35
opacity = 0.8
# monte carlo in blue
rects1 = plt.bar(index, mc_stat, bar_width,
alpha=opacity,
color='b',
label='Frank')
#pca in green
rects2 = plt.bar(index + bar_width, pca_stat, bar_width,
alpha=opacity,
color='g',
label='Guido')

plt.title('Monte Carlo and PCA Optimization Statistics')
plt.xticks(index + bar_width, ('Expected return', 'Expected variance', 'Sharpe ratio'))
plt.tight_layout()
plt.show()

#calculate optimal portfolio returns
optPortPC_ret = (rets * weights_arr).sum(axis = 1)


import seaborn as sns
# plot optimal portfolio returns vs benchmark returns
sns.regplot(rets_benchmark.values,
optPortPC_ret.values)
plt.xlabel("Benchmark Returns")
plt.ylabel("Portfolio Returns")
plt.title("Portfolio Returns vs Benchmark Returns")
plt.show()


############ ALPHA and BETA
from scipy import stats
benchmark_ret = rets_benchmark.squeeze()
benchmark_ret=benchmark_ret[1:]
optPortPC_ret=optPortPC_ret[1:]
#benchmark_ret=snp['^GSPC'][1:]
(beta, alpha) = stats.linregress(benchmark_ret.values,
                optPortPC_ret.values)[0:2]

#print beta
print("The portfolio beta is", round(beta, 4)) 
print("The portfolio alpha is", round(alpha,5))
