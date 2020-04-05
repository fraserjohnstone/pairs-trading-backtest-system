## Setup

#### Python Version

Ensure that you are running Python version 3.x

#### Dependencies

pandas (0.24.2)

numpy (1.16.6)

statsmodels (0.11.0)

matplotlib (2.2.5)

#### The Aim

The aim of this software is to to identify if it would be possible to implement a cost-effective and profitable pairs trading algorithm in python.

This README does not attempt to go into specifics about how pairs trading works but the general principle is this: if two stocks display sufficient cointegration, then we can sell one and buy the other at a ratio such that when we reverse the positions upon the expected mean reversion, we will make money.

This is an extremely difficult thing to do correctly. To understand the specifics I would point you in the direction of 'Pairs Trading: Quantitative Methods and Analysis' by Ganapathy Vidyamurthy.

This project at current is a spike in order to identify how one would go about applying the rigorous analysis required in both defining a suitable level of cointegration for a pair, and then correctly creating hedged trades in order to make money in such a way that we can be 'hands off'.

Understand that for many reasons, using this algorithm in its current state, although displaying promising results, would not be wise in the real world. Again, this is a spike and as such ignores crucial factors such as market charges etc.

All of the data used for backtesting are historic cryptocurrency prices gathered from Bitfinex

#### What it does currently

If you were to execute the file `run_backtest.py`, the software will gather 10000 prices ending one month ago for all cryptocurrencies defined in `asset_service.py`. These samples are at 15 minute intervals, though this can be changed to any interval you wish. All possible pair combinations of time-series generated from the asset prices will be examined for signs of cointegration, and any pairs showing suitable cointegration will be passed to the model.

The model runs the trading algorithm over each time series passed in, and upon completion of each will save a plot to `backtest/results/` showing the change in how much money you would have, referred to in the model as 'balance'.

#### Contribute

Please get in touch by sending me an email (fraserjohnstone12345@hotmail.com) if you wish to contribute.
