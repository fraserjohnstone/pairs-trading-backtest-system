## Setup

#### Python Version

Ensure that you are running Python version 2.7.

#### Dependencies

From the root directory run `pip install -r requirements.txt` to ensure your system has the correct packages installed.

#### Database Setup

  1. Ensure that you have MySql installed on your system.
  2. Create a database called `pairs-trading-backtest`.
  3. Create a MySql user associated with this database and grant all privileges.
  4. Rename the file `src/db_connection_manager.example.json` to `src/db_connection_manager.json`. Replace the example values to match your database and user information.
  5. From the `src/` directory run `python db_setup.py`. This will seed the database with asset/pair information required for the back testing.

## Running

By default the system will simulate trading over a period of 1 year. The test will always have a simulated starting point of exactly one year in the past from the current date/time. This value can be changed by altering the `years_to_gather` value in the `src/config.py` file.

The system can be run in 2 modes:

  1. Single context
  2. All contexts within ranges

Both of the modes will essentially end up running the system based on the set of values outlined below:

  - **_time_period_** (String): the value passed to the bitfinnex api defining the time period between samples gathered. For example, if you would like to gather samples at minute intervals this would be '1m', where as 3 hour intervals would be '3h'. a full list of the values available is outlined in the [bitfinnex documentation](https://docs.bitfinex.com/reference#rest-public-candles)
  - **_block_size_** (Float): Regardless of whether your time_period is defined in minutes, hours, days or otherwise, this value is that time period expressed as hours. For example if your time_period was '15m' (15 minutes), then this value would be 0.25. If your time_period was '1D' (one day), then this value would be 24.0
  - **_z_in_val_** (float): This value is used to define an entry point for any trade.
  - **_z_val_out_** (float): this value is used to define an exit point for any open orders.
  - **_analysis_size_** (float): the number of samples to be used to determine co-integration status of any pair of assets.

Both run modes will store results in log files in the `/src/logs/` directory.

#### Running in 'Single Context' mode

If you would like to see the results of a specific set of parameters then alter the values in `src/run_single_context.py`. This will simulate trading over the specified period with only the one set of values you provide.

To start, run `python run_single_context.py` from the `src/` directory.

#### Running in 'All Contexts' mode

If you would like to run a much more substantial back test then 'All Contexts' mode allows for this. This will essentially run a series of back tests utilising all possible permutations of values defined in ranges supplied in the `src/run_all_contexts.py` file.

An effort has been made to speed up this process by splitting the back tests across all available processors, however it is likely that any attempt to try a large combination of values will result in a very lengthy overall test. To improve this situation the following is possible:

  - When starting each back test, a check is made for the presence of the associated log file. If such a file is found, then the test is skipped.
  - If a log file associated with a specific back test is not the expected length when its process is killed then the log file will be deleted.
  - If a log file for a specific scenario exists but is not the exepcted completed length at the beginning of a run, the file will be overwritten and the scenario will be restarted.

This means that not only can you stop and start the test as you wish without losing much data, but it is also possible to run the test on multiple machines concurrently by running the system from a shared directory (Dropbox folder for example).

The first time that you run the software in this mode, there will be a lengthy gathering of data to allow all possible scenarios to be backtested. From this point on, each time the process is stopped and started the same gathered data will be used resulting in consistent results. You can however force this data to be gathered again by deleting the generated `minute_candles.pickle` file from the `src/` directory.

To start, run `python run_all_contexts.py` from the `src/` directory.

## Stopping

Stopping Single Context mode is as simple as interrupting the single running process (<kbd>ctrl</kbd> + <kbd>c</kbd>), however, in All Contexts mode multiple processes are spawned and you must run `python stop_all.py` from the `src/` directory. This will kill all spawned processes.
