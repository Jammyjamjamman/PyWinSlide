# PyWinSlide
Sliding window functions for processing iterative timeseries data in python.

This project is still in very early stages. If you need rolling window functions, I first recommend looking at [pandas dataframes](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rolling.html) .

The reason I'm making this script as an alternative to the pandas rolling window, is that pandas requires the entire timeseries to be loaded into memory. The function provided in this script allows data to be processed iteratively.

### Using The Script.
The easiest way currently is to download pywinslide.py into the same directory as the script/ jupyter notebook you want to use it with. This is a following example of how to use it:
```py
import pywinslide

"""
The iterator 'timeseries_iter' should yield a tuple of the form (timestamp, number) every iteration. N.B. The timestamp is a datetime object.
"""
timeseries_iter = my_iter

# Create lists of times, means and vars.
times = []
means = []
variances = []
for time, mean, var in pywinslide.sliding_mean_var:
    times.append(time)
    means.append(mean)
    variances.append(var)
```

### Other Plans.
I would really like to make cython versions of these scripts in the future. However, I have no experience in using cython.
