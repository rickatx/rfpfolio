# Welcome to rfpfolio
> Create portfolios with rebalancing, and measure performance.


```python
rfp.
```

This file will become your README and also the index of your documentation.

## Install

`pip install rfpfolio`

## How to use

Some code examples:

```python
tst_src = rfp.PriceSource('testdata/2017-Apr')
```

```python
price_data = tst_src.loadAllAdjustedPrices(['SPY', 'IEI', 'GLD'])
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


