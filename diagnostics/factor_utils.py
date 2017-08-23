
import pandas as pd
import numpy as np
import datetime as dt



def quantize_factor(factor_data, quantiles=5, bins=None, by_group=False):
    """
    Computes period wise factor quantiles.
    Parameters
    ----------
    factor_data : pd.DataFrame - MultiIndex
        A MultiIndex DataFrame indexed by date (level 0) and asset (level 1),
        containing the values for a single alpha factor, forward returns for
        each period, the factor quantile/bin that factor value belongs too, and
        (optionally) the group the asset belongs to.
    quantiles : int or sequence[float]
        Number of equal-sized quantile buckets to use in factor bucketing.
        Alternately sequence of quantiles, allowing non-equal-sized buckets
        e.g. [0, .10, .5, .90, 1.] or [.05, .5, .95]
        Only one of 'quantiles' or 'bins' can be not-None
    bins : int or sequence[float]
        Number of equal-width (valuewise) bins to use in factor bucketing.
        Alternately sequence of bin edges allowing for non-uniform bin width
        e.g. [-4, -2, -0.5, 0, 10]
        Only one of 'quantiles' or 'bins' can be not-None
    by_group : bool
        If True, compute quantile buckets separately for each group.
    Returns
    -------
    factor_quantile : pd.Series
        Factor quantiles indexed by date and asset.
    """

    def quantile_calc(x, _quantiles, _bins):
        if _quantiles is not None and _bins is None:
            return pd.qcut(x, _quantiles, labels=False) + 1
        elif _bins is not None and _quantiles is None:
            return pd.cut(x, _bins, labels=False) + 1
        raise ValueError('Either quantiles or bins should be provided')

    grouper = [factor_data.index.get_level_values('date')]
    if by_group:
        grouper.append('group')

    factor_quantile = factor_data.groupby(grouper)['factor'] \
        .apply(quantile_calc, quantiles, bins)
    factor_quantile.name = 'factor_quantile'

    return factor_quantile.dropna()






def compute_forward_returns(prices, periods=(1, 5, 10), filter_zscore=None):
    """
    Finds the N period forward returns (as percent change) for each asset
    provided.
    Parameters
    ----------
    prices : pd.DataFrame
        Pricing data to use in forward price calculation.
        Assets as columns, dates as index. Pricing data must
        span the factor analysis time period plus an additional buffer window
        that is greater than the maximum number of expected periods
        in the forward returns calculations.
    periods : sequence[int]
        periods to compute forward returns on.
    filter_zscore : int or float
        Sets forward returns greater than X standard deviations
        from the the mean to nan.
        Caution: this outlier filtering incorporates lookahead bias.
    Returns
    -------
    forward_returns : pd.DataFrame - MultiIndex
        Forward returns in indexed by date and asset.
        Separate column for each forward return window.
    """

    forward_returns = pd.DataFrame(index=pd.MultiIndex.from_product(
        [prices.index, prices.columns], names=['date', 'asset']))

    for period in periods:
        delta = prices.pct_change(period).shift(-period)

        if filter_zscore is not None:
            mask = abs(delta - delta.mean()) > (filter_zscore * delta.std())
            delta[mask] = np.nan

        forward_returns[period] = delta.stack()

    forward_returns.index = forward_returns.index.rename(['date', 'asset'])

    return forward_returns


def demean_forward_returns(factor_data, grouper=None):
    """
    Convert forward returns to returns relative to mean
    period wise all-universe or group returns.
    group-wise normalization incorporates the assumption of a
    group neutral portfolio constraint and thus allows allows the
    factor to be evaluated across groups.
    For example, if AAPL 5 period return is 0.1% and mean 5 period
    return for the Technology stocks in our universe was 0.5% in the
    same period, the group adjusted 5 period return for AAPL in this
    period is -0.4%.
    Parameters
    ----------
    factor_data : pd.DataFrame - MultiIndex
        Forward returns in indexed by date and asset.
        Separate column for each forward return window.
    grouper : list
        If True, demean according to group.
    Returns
    -------
    adjusted_forward_returns : pd.DataFrame - MultiIndex
        DataFrame of the same format as the input, but with each
        security's returns normalized by group.
    """

    factor_data = factor_data.copy()

    if not grouper:
        grouper = factor_data.index.get_level_values('date')

    cols = get_forward_returns_columns(factor_data.columns)
    factor_data[cols] = factor_data.groupby(grouper)[cols] \
        .transform(lambda x: x - x.mean())

    return factor_data




def aggregate_returns(returns, convert_to='M'):
    """
    Parameters

    Aggregates returns by day, week, month, or year.
    returns : pd.DataFrame
        Daily returns for all assets
    """

    if convert_to == 'W':
        return returns.groupby(
            [lambda x: x.year,
             lambda x: x.month,
             lambda x: x.isocalendar()[1]]).apply(cumulate_returns)
    elif convert_to == 'M':
        return returns.groupby(
            [lambda x: x.year, lambda x: x.month]).apply(cumulate_returns)
    elif convert_to == 'Y':
        return returns.groupby(
            [lambda x: x.year]).apply(cumulate_returns)
    else:
        ValueError('convert_to must be weekly, monthly or yearly')


def get_annualized_returns(returns, periods=252):
    return (1+cumulate_returns(returns)) ** (periods/len(returns))


def cumulate_returns(returns):
    return (1 + returns).cumprod().loc[returns.last_valid_index(), :] - 1

def get_forward_returns_columns(columns):
    return columns[columns.astype('str').str.isdigit()]



