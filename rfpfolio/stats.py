# AUTOGENERATED! DO NOT EDIT! File to edit: 01_Stats.ipynb (unless otherwise specified).

__all__ = ['default_stats_spec', 'perfStatsRowTable', 'DateRange', 'ret_vol_combos', 'plot_bullet', 'VOL_STANDARD',
           'VOL_DOWNSIDE', 'window_gen', 'window_stats', 'rolling_optimal_combo_stats']

# Cell
import pandas as pd
import numpy as np
import os.path
from typing import NamedTuple
import datetime
import rfpfolio as rfp
import matplotlib.pyplot as plt

# Hide warning on import of empyrical
import warnings
with warnings.catch_warnings():
    warnings.filterwarnings("ignore", category=FutureWarning)
    import empyrical.stats as estats

# Internal Cell
def _ann_rate_to_period_rate(ann_rate, period='weekly'):
    """Convert annual return rate to periodic rate for the specified period ('daily', 'weekly', 'monthly').
    """
    return (1 + ann_rate)**(1/estats.annualization_factor(period, None)) - 1

# Cell
def default_stats_spec(period='weekly', ann_rf_rate=0):
    """Generate specs for some standard statistics, given annual risk-free rate and return period of data."""
    per_rf_rate = _ann_rate_to_period_rate(ann_rf_rate, period)

    stats_spec = {'Annual Return':lambda x:estats.annual_return(x, period),
                  'Max Drawdown':estats.max_drawdown,
                  'Annual Volatility':lambda x: estats.annual_volatility(x, period),
                  'Sharpe Ratio':lambda x: estats.sharpe_ratio(x, risk_free=per_rf_rate, period=period)}
    return stats_spec

# Cell
def perfStatsRowTable(pf_returns, stats_spec, style=False):
    """
    Statistic per row; columns are portfolios.
    """
    valDict = {pf_col: [f(pf_returns[pf_col]) for f in stats_spec.values()] for pf_col in pf_returns.columns}

    if style:
        cm = sns.light_palette("pastel blue", reverse=True, as_cmap=True, input='xkcd')

    df = pd.DataFrame(valDict, index=stats_spec.keys())

    if style:
        return (df
                .style
                .background_gradient(cmap=cm, axis=1)
                .format("{:.2%}")
               )
    else:
        return df

# Cell

class DateRange(NamedTuple):
    start_date: datetime.date
    end_date: datetime.date

def ret_vol_combos(ret1, ret2, nsteps, period='monthly', rebal_period=3):
    """Return and volatility that results from combining two return series in proportions from 0 to 100%.

    Args:
     - ret1: return series 1 (sequence of period returns, such as output by computePortfolioReturns())
     - ret2: return series 2
     - nsteps: number of steps to take in allocation to the returns, between 0 and 100%
     - period: return interval in `ret1`, `ret2`: {'daily', 'weekly', 'monthly'}
     - rebal_period: interval for rebalancing the allocation; expressed as number of periods of type `period`

     Return:
      - Dataframe with results for each allocation between 0 and 100%
        - annualized return
        - annualized standard deviation
        - annualized downside deviation
      - Date range of returns used for these results
    """
    # convert period returns to wr's
    ret1 = ret1.copy() + 1
    ret2 = ret2.copy() + 1

    # combine the two return sequences
    combined = pd.concat([ret1, ret2], axis=1, join='inner')
    # Note: the concat/join ensures we have the same date range for both return sequences;
    # computing the date range here ensures that it accurately reflects dates to compute results
    date_range = DateRange(min(combined.index).date(), max(combined.index).date())

    stepsize = 1 / nsteps
    return_list = []
    vol_list = []
    downside_list = []
    w1_list = []
    for ix in range(nsteps+1):
        w1 = 1 - ix*stepsize
        w2 = ix*stepsize
        res = rfp.pf_period_returns(combined, [w1, w2], rebal_period, f'combined_{w1:4.2}')
        # print(res.head())
        ann_ret = estats.annual_return(res.values, period=period)
        ann_vol = estats.annual_volatility(res.values, period=period)
        ann_downside = estats.downside_risk(res.values, period=period) # option to add `required_return` parameter
        #print(w1, w2, ann_ret, ann_vol)
        return_list.append(ann_ret[0])
        vol_list.append(ann_vol[0])
        downside_list.append(ann_downside[0])
        w1_list.append(w1)

    df = pd.DataFrame({'w1':w1_list, 'ann_ret':return_list, 'standard_dev':vol_list, 'downside_dev':downside_list})
    return df, date_range

# Cell

VOL_STANDARD = 1  # Indicates standard deviation as volatility measure
VOL_DOWNSIDE = 2  # Indicates downside deviation as volatility measure

def plot_bullet(ret1, ret2, nsteps, period='monthly', rebal_period=3, vol=VOL_STANDARD, fig_size=(14,10)):
    """Generate a plot of return vs. volatility that results from combining two return series in proportions from 0 to 100%.

    Args:
     - ret1: return series 1 (sequence of period returns, such as output by computePortfolioReturns())
     - ret2: return series 2
     - nsteps: number of steps to take in allocation to the returns, between 0 and 100%
     - period: return interval in `ret1`, `ret2`: {'daily', 'weekly', 'monthly'}
     - rebal_period: interval for rebalancing the allocation; expressed as number of periods of type `period`
     - vol: which volatility measure(s) to include in the plot can be one of {VOL_STANDARD, VOL_DOWNSIDE}, or a
     boolean or of these values (indicating to plot both)
     - fig_size: size of plot
     """

    df, date_range = ret_vol_combos(ret1, ret2, nsteps, period, rebal_period)

    # extract values needed for plot from df
    w1_list = [f"{w1:5.2}" for w1 in df.w1] # text to annotate points on scatter plot
    return_list = df.ann_ret
    vol_list = df.standard_dev
    downside_list = df.downside_dev

    fig = plt.figure(figsize=fig_size)
    ax1 = fig.add_subplot(111)
    ax1.set_ylabel('annualized return')
    ax1.set_xlabel('standard deviation')

    # If we are plotting 2 types of deviation, create another x axis, duplicating y-axis
    if vol >= VOL_STANDARD | VOL_DOWNSIDE:
        ax2 = ax1.twiny()
        ax2.set_xlabel('downside deviation')
    else:
        ax2 = ax1
        if vol & VOL_DOWNSIDE:
            ax1.set_xlabel('downside deviation')

    # Plot return vs. volatility (one or more types of volatility)
    if vol & VOL_STANDARD:
        ax1.scatter(vol_list, return_list, marker="D", c='b', label="standard deviation")
    if vol & VOL_DOWNSIDE:
        ax2.scatter(downside_list, return_list, marker="s", c='g', label="downside deviation")

    # Title
    start_date = date_range.start_date.strftime('%b %Y')
    end_date = date_range.end_date.strftime('%b %Y')
    fig.suptitle(f'{ret1.columns[0]}(1.0) --> {ret2.columns[0]}(0.0) - {start_date} to {end_date}')

    fig.legend()

    for txt, x1, x2, y in zip (w1_list, vol_list, downside_list, return_list):
        if vol & VOL_STANDARD:
            ax1.annotate(txt, (x1, y), fontsize=8)
        if vol & VOL_DOWNSIDE:
            ax2.annotate(txt, (x2, y), fontsize=8)

# Cell

def window_gen(datetime_index, window_len, window_step):
    """Create a sequence of (start_date, end_date) for a fixed-width rolling window.

    Args:
     - datetime_index: iterable of dates that index some dataset (exptected to be at a fixed period, say weekly)
     - window_len: size of the window, expressed in number of `datetime_index1 intervals
     - window_step: number of periods to advance window on each iteration
    """
    for start_ix in range(0, len(datetime_index) - window_len + 1, window_step):
        yield(datetime_index[start_ix], datetime_index[start_ix + window_len - 1])

# Cell

def window_stats(return_series, window_len, window_step, stat_fns):
    """Compute statistics over a rolling window of the specified return series.

    Args:
     - return_series: a sequence of period returns (.01 = 1% return), indexed by date
     - window_len: length of window of return series to use for computation of stats, repeatedly
     - window_step: number of periods to advance window on each iteration (`window_step` == `window_len`
     => contiguous nonoverlapping windows)
     - stat_fns: a sequence of functions, each accepts an iterable of period returns as its only arg

     Returns:
      - A datframe whose columns are the outputs of `stat_fns`, applied to the window at each step, and
      indexed by the date of the last period of the window at this step. The column order corresponds to the
      order of stat_fns.
    """
    date_list = []
    stats_list = []
    rs_len = return_series.shape[0]

    for start_date, end_date in window_gen(return_series.index, window_len, window_step):
        window = return_series[start_date : end_date]

        # compute stats on this window
        stats_list.append([fn(window) for fn in stat_fns])

        # date corresponding to value for the window is the last date included in the window
        date_list.append(end_date)

    return pd.DataFrame(stats_list, index=date_list)

# Cell
def rolling_optimal_combo_stats(ret1, ret2, window_len, window_step, nsteps=20, period='monthly', rebal_period=3,
                               downside_vol=True):
    """Find the optimal (volatility-minimizing) combination of two return series over a rolling window.

    Args:
     - ret1: a sequence of period returns (.01 = 1% return), indexed by date
     - ret2: a sequence of period returns (.01 = 1% return), indexed by date
     - window_len: length of window of return series to use for computation of stats, repeatedly
     - window_step: number of periods to advance window on each iteration (`window_step` == `window_len`
     => contiguous nonoverlapping windows)
     - nsteps: divide toe [0.0, 1.0] interval into this many steps in the search for the min vol combination
     - period: return interval in `ret1`, `ret2`: {'daily', 'weekly', 'monthly'}
     - rebal_period: interval for rebalancing the allocation; expressed as number of periods of type `period`
     - downside_vol: If true, use downside deviation as volatility metric, else standard deviation

    Return:
     - DataFrame containing portfolio performance stats for the optimal portfolio over each window.
    """
    # column name of chosen volatility metric
    vol_column = 'downside_dev' if downside_vol else 'standard_dev'

    # find the inner-joined indices of the two return series
    joined_index = pd.concat([ret1, ret2], axis=1, join='inner').index

    #print(joined_index)

    data = []
    dates = []
    for start_date, end_date in window_gen(joined_index, window_len, window_step):

        df, _ = ret_vol_combos(ret1[start_date:end_date], ret2[start_date:end_date], nsteps, period, rebal_period)

        # pick "optimal" portfolio -- choose one with minimum volatility (could use std or downside)
        # index of row with lowest value for downside_dev
        best_row_idx = sorted(enumerate(df.downside_dev), key=lambda x: x[1])[0][0]

        data.append(df.iloc[best_row_idx])
        dates.append(end_date)

    return pd.DataFrame(data, index=dates)