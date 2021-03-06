![GitHub Workflow Status](https://img.shields.io/github/workflow/status/rickatx/rfpfolio/CI)
<!-- 
https://shields.io/category/build
-->

# Welcome to rfpfolio
> Generate historical return data for portfolios, with rebalancing.


This Python package is designed to solve a simple problem: examining the historical performance of a portfolio of assets with a specified, fixed weighting for each asset, and periodic rebalancing to the specified weighting.

You can get a good understanding of the value of this by browsing the information and graphics at https://portfoliocharts.com/

Using this package, you can perform portfolio analysis using your own data, and are not restricted to choices available at portfoliocharts.com. This is useful if you are interested in exploring portfolios that include alternative asset classes, equity allocations to a particular set of stocks, or allocations to some dynamic strategy (for which you have separately procured or generated data.)

The most common application for this Python package is to import it into a Jupyter notebook, use it to generate portfolio returns for an asset weighting of interest, and then use other tools for analyzing and plotting the portfolio returns.

## Install

Clone this repo to your machine. Navigate your shell to the cloned repo's root directory and run:

```
pip install .
```
or:
```
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
|
|--+ daily
      :
 ```
 
 Here is how to specify the root directory for your data:

```python
import rfpfolio as rfp

tst_src = rfp.PriceSource('testdata/2017-Apr')
```

We can see what data files are available in subdirectory, and their date coverage as follows:

```python
tst_src.list_return_dates('weekly')
```

    2017-03-27 => 2020-05-25  AGG.csv
    2017-04-03 => 2020-06-29  GLD.csv
    2017-04-03 => 2020-06-29  IEI.csv
    2017-04-03 => 2020-06-29  PDBC.csv
    2017-04-03 => 2020-06-29  SHV.csv
    2017-04-03 => 2020-06-29  SPY.csv
    2017-04-03 => 2020-06-29  TLT.csv
    2017-03-27 => 2020-05-25  VT.csv
    2017-04-03 => 2020-06-29  VTI.csv
    

Let's take a peek at the data. The data should be a sequence of "adjusted prices" (adjusted for, say, dividends and stock splits). This means that the true ending value of an investment in the asset over some period is given by the adjusted price at the end of the period, divided by the beginning adjusted price, all multiplied by the initial investment.

```python
price_data = tst_src.load_all_adjusted_prices(['SPY', 'IEI', 'GLD'], subdir='weekly')
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



### Load Asset Returns

Usually, we are more interested in the asset returns over each period, rather than the adjusted prices. Load the period returns as follows:

```python
return_data = tst_src.load_all_period_returns(['SPY', 'IEI', 'GLD'], subdir='weekly')
return_data.head()
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
      <th>2017-04-10</th>
      <td>-0.011437</td>
      <td>0.008825</td>
      <td>0.026285</td>
    </tr>
    <tr>
      <th>2017-04-17</th>
      <td>0.008946</td>
      <td>0.000646</td>
      <td>-0.002365</td>
    </tr>
    <tr>
      <th>2017-04-24</th>
      <td>0.014877</td>
      <td>-0.002178</td>
      <td>-0.012591</td>
    </tr>
    <tr>
      <th>2017-05-01</th>
      <td>0.006804</td>
      <td>-0.003314</td>
      <td>-0.031134</td>
    </tr>
    <tr>
      <th>2017-05-08</th>
      <td>-0.003004</td>
      <td>0.002822</td>
      <td>-0.001538</td>
    </tr>
  </tbody>
</table>
</div>



### Compute portfolio returns

For example, compute returns for a portfolio consisting of 40% large U.S. stocks (SPY), 40% U.S. Treasury bonds (IEI), and 20% gold (GLD), rebalanced every four weeks.

```python
portfolio_1_weights = [('SPY', 0.4), ('IEI', 0.4), ('GLD', 0.2)]
pf_1_returns = rfp.computePortfolioReturns(tst_src, portfolio_1_weights, "Portfolio_1", rebal_period=4, 
                                           period='weekly', start_date='2017-05-01')
```

```python
pf_1_returns.head()
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
      <th>Portfolio_1</th>
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

stats_spec = {'Annual Return':lambda x:estats.annual_return(x, period),
              'Max Drawdown':estats.max_drawdown,
              'Annual Volatility':lambda x: estats.annual_volatility(x, period), 
              'Sharpe Ratio':lambda x: estats.sharpe_ratio(x, period=period)}

stats = [f(pf_1_returns['Portfolio_1']) for f in stats_spec.values()]

pd.DataFrame({'Portfolio_1': stats}, index=stats_spec.keys())
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
      <th>Portfolio_1</th>
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
      <td>0.955435</td>
    </tr>
  </tbody>
</table>
</div>



Plot the cumulative returns of the portfolio.

```python
cum_returns2 = estats.cum_returns(pf_1_returns, 100)
cum_returns2.plot.line(figsize=(10,5));
```


![png](docs/images/output_22_0.png)


## License

Copyright 2020 Richard A. Froom. Licensed under the Apache License, Version 2.0 (the "License"); you may not use this project's files except in compliance with the License. A copy of the License is provided in the LICENSE file in this repository.
