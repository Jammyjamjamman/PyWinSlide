# PyWinSlide
Sliding window functions for processing iterative timeseries data in python.

This project is still in very early stages. If you need rolling window functions, I first recommend looking at [pandas dataframes](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rolling.html) .

### Why you may/ may not want to use this script.
The reason I'm making this script as an alternative to the pandas rolling window, is that pandas requires the entire timeseries to be loaded into memory. The functions provided in this script allows data to be processed iteratively, which can reduce memory usage when compared to pandas. However, it is significantly slower than pandas at rolling calcuations.

### What is supplied.
Currently, a generic `Window` class is provided and a `sliding_window` function for using the window class. These are for making new sliding window functions.

Useable functions supplied are:

* `sliding_mean_var()`, for calculating the rolling mean and variance within an iterative window.
* `mean_downresample()`, for reducing the sample frequency of a timeseries e.g. every minute instead of every second, by taking the mean of the values every second within a minute window.

The easiest way to create your own sliding window function, is to create a new class which inherits `Window`. Then, to get the statistics you want from the window, override the method `get_cur_stats()` in your window.


### Using The Script.
The easiest way to use the script currently is to place `pywinslide.py` into the same directory as the script/ jupyter notebook you want to use it with. This is a following example of how to use it:

```py
import pywinslide

"""
The iterator 'timeseries_iter' should yield a tuple of the form (timestamp, number)
every iteration. N.B. The timestamp is a datetime object. The function does not handle
None types or other incorrect types.
"""

# Some timeseries iterator.
timeseries_iter = my_iter

# Create lists of times, means and vars.
times = []
means = []
variances = []
# Create and iterate through a rolling mean and variance function.
# The size of the window is 1.
for time, mean, var in pywinslide.sliding_mean_var(timeseries_iter, window_sz=timedelta(days=1)):
    times.append(time)
    means.append(mean)
    variances.append(var)
```

### Other Plans.
* Add a jupyter notebook, demonstrating using this script.
* Add more comments to the script.
* I would really like to make cython versions of these scripts in the future. However, I have no experience in using cython.
