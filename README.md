# PyWinSlide
Sliding window functions for processing iterative timeseries data in python.

This project is still in very early stages. If you need rolling window functions, for now, I recommend looking at [pandas dataframes](https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.rolling.html) .

The reason I'm making this script as an alternative to the pandas rolling window, is that pandas requires the entire timeseries to be loaded into memory. The function provided in this script allows data to be processed iteratively.

I would really like to make cython versions of these scripts in the future. However, I have no experience in using cython.
