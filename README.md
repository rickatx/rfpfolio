# Welcome to rfpfolio
> Generate historical return data for portfolios, with rebalancing.


This Python package is designed to solve a simple problem: examining the historical performance of a portfolio of assets with a specified, fixed weighting for each asset, and periodic rebalancing to the specified weighting.

In other words, the goal is similar to that of https://portfoliocharts.com/

However, here you can use your own data (perhaps for alternative asset classes) and are not restricted to choices available at portfoliocharts.com.

The most common application for this Python package is to import it into a Jupyter notebook, use it to generate portfolio returns for an asset weighting of interest, and then using other Python tools for analyzing and plotting the portfolio returns.

## Install

Clone this repo to your machine. Navigate your shell to the cloned repo's root directory and run:

```
pip install .
```
or:
````
python setup.py install
```

## How to use

### Specify a source for your data

The supported format is Yahoo Finance csv, and the code currently only reads the `Date` and `Adj Close` columns.

The data root directory specified to PriceSource contains your data, with one or more subdirectories (daily, weekly, monthly)
for asset data series of different frequencies.

```
+ <data_root>
|--+ weekly
|  |--+ GLD.csv
|  |--+ IEI.csv
|  |--+ SPY.csv
|--+ daily
   :
 ```
 
 Here is how to specify the root directory for your data:

```python
tst_src = rfp.PriceSource('testdata/2017-Apr')
```

Let's take a peek at the data. The data should be a sequence of "adjusted prices" (adjusted for, say, dividends and stock splits). This means that the true ending value of an investment in the asset over some period is given by the adjusted price at the end of the period, divided by the beginning adjusted price, all multiplied by the initial investment.

```python
price_data = tst_src.loadAllAdjustedPrices(['SPY', 'IEI', 'GLD'], subdir='weekly')
price_data.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>SPY</th>
      <th>IEI</th>
      <th>GLD</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2017-04-03</th>
      <td>220.896225</td>
      <td>115.845558</td>
      <td>119.459999</td>
    </tr>
    <tr>
      <th>2017-04-10</th>
      <td>218.369843</td>
      <td>116.867851</td>
      <td>122.599998</td>
    </tr>
    <tr>
      <th>2017-04-17</th>
      <td>220.323349</td>
      <td>116.943314</td>
      <td>122.309998</td>
    </tr>
    <tr>
      <th>2017-04-24</th>
      <td>223.601120</td>
      <td>116.688652</td>
      <td>120.769997</td>
    </tr>
    <tr>
      <th>2017-05-01</th>
      <td>225.122589</td>
      <td>116.301956</td>
      <td>117.010002</td>
    </tr>
  </tbody>
</table>
</div>



### Compute portfolio returns

For example, compute returns for a portfolio consisting of 40% large U.S. stocks (SPY), 40% U.S. Treasury bonds (IEI), and 20% gold (GLD), rebalanced every four weeks.

```python
portfolio_1_weights = {'SPY': 0.4, 'IEI': 0.4, 'GLD': 0.2}
pf_1_returns = rfp.computePortfolioReturns(tst_src, portfolio_1_weights, "PF_1", rebal_period=4, 
                                           period='weekly', start_date='2017-05-01')
```

```python
pf_1_returns.head(10)
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>PF_1</th>
    </tr>
    <tr>
      <th>Date</th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>2017-05-01</th>
      <td>-0.004831</td>
    </tr>
    <tr>
      <th>2017-05-08</th>
      <td>-0.000385</td>
    </tr>
    <tr>
      <th>2017-05-15</th>
      <td>0.004611</td>
    </tr>
    <tr>
      <th>2017-05-22</th>
      <td>0.007605</td>
    </tr>
    <tr>
      <th>2017-05-29</th>
      <td>0.006685</td>
    </tr>
    <tr>
      <th>2017-06-05</th>
      <td>-0.003417</td>
    </tr>
    <tr>
      <th>2017-06-12</th>
      <td>-0.002579</td>
    </tr>
    <tr>
      <th>2017-06-19</th>
      <td>0.003017</td>
    </tr>
    <tr>
      <th>2017-06-26</th>
      <td>-0.006514</td>
    </tr>
    <tr>
      <th>2017-07-03</th>
      <td>-0.005629</td>
    </tr>
  </tbody>
</table>
</div>



### Analyze the returns

For example, here we can use some of the metrics from the *empyrical* package to assess the performance of this portfolio over the study period.

```python
import empyrical.stats as estats
import pandas as pd
```

```python
period='weekly'

# risk-free rate -- for Sharpe ratio
rf_rate = 0.003 # ann. rate of 0.3%
weekly_rf_rate = (1 + rf_rate)**(1/52) - 1

stats_spec = {'Annual Return':lambda x:estats.annual_return(x, period),
              'Max Drawdown':estats.max_drawdown,
              'Annual Volatility':lambda x: estats.annual_volatility(x, period), 
              'Sharpe Ratio':lambda x: estats.sharpe_ratio(x, risk_free=weekly_rf_rate, period=period)}

stats = [f(pf_1_returns['PF_1']) for f in stats_spec.values()]

pd.DataFrame({'PF_1': stats}, index=stats_spec.keys())
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>PF_1</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Annual Return</th>
      <td>0.085432</td>
    </tr>
    <tr>
      <th>Max Drawdown</th>
      <td>-0.138613</td>
    </tr>
    <tr>
      <th>Annual Volatility</th>
      <td>0.090113</td>
    </tr>
    <tr>
      <th>Sharpe Ratio</th>
      <td>0.922193</td>
    </tr>
  </tbody>
</table>
</div>



Plot the cumulative returns of the portfolio.

```python
cum_returns2 = estats.cum_returns(pf_1_returns, 100)
cum_returns2.plot.line(figsize=(10,5));
```


![png](docs/images/output_17_0.png)

