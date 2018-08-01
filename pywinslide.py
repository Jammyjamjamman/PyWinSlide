#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 23:12:47 2018

@author: james
"""
from datetime import timedelta


def moving_average(dat_iter, window_sz = timedelta(days=1)):
    """
    Creates an iterator which calculates the moving average
    from a timeseries iterator.
    The time series iteratore should return values in ascending order of time.
    
    Args:
        dat_iter (Iterator((datetime, number))): Produces a tuple each
        iteration containing a timestamp and a number which can be averaged.
        window_sz (timedelta): The size of the moving window (in time).
        Default window size is 1 day.
    
    Yields:
        (datetime, float): The next "moving average" as a tuple containing the
        timestamp and datetime.
        
    TODO:
    1. Improve commments.
    2. Improve how function is written.
    3. Add tests.
    4. Write a more cython-friendly version for speed improvements
    """
    half_window = window_sz/2

    window = []
    cur_win_pos = 0

    next_time, next_val = next(dat_iter)

    win_min = next_time - half_window
    win_max = next_time + half_window

    # Calculate sum of elements in the window.
    # This sum will be modified as values are
    # appended and removed from the window.
    while next_time <= win_max:
        window.append((next_time, next_val))
        try:
            next_time, next_val = next(dat_iter)
        except StopIteration:
            break

    # Calculate sum of elements in the window.
    # This sum will be modified as are appended
    # and removed from the window.
    cur_sum = sum(dat[1] for dat in window)
    # keep a running total of the elements in the window.
    # This will change as elements are added/ removed from the window
    window_len = len(window)

    # 2. Calculate the means.
    # The loop is finished when the last element in the window is reached.
    while cur_win_pos != window_len:
        win_min = window[cur_win_pos][0] - half_window
        win_max = window[cur_win_pos][0] + half_window

        # 2.1 Remove values not within current window bounds.
        while window[0][0]  < win_min:
            cur_sum -= window.pop(0)[1]
            cur_win_pos -= 1
            window_len -= 1

        # 2.2 Insert the next values from iterator, within window.
        while next_time <= win_max:
            try:
                temp_time, temp_val = next_time, next_val
                next_time, next_val = next(dat_iter)
            except StopIteration:
                break
            else:
                window.append((temp_time, temp_val))
                window_len += 1
                cur_sum += temp_val
        
        # 2.3 Complete and emit the mean calculation.
        yield window[cur_win_pos][0], (cur_sum/window_len)
        cur_win_pos += 1

        # 3. If we have reached the end of the window,
        # check if there's any values left in the iterator.
        if cur_win_pos == window_len:
            try:
                temp_time, temp_val = next_time, next_val
                next_time, next_val = next(dat_iter)
            except StopIteration:
                pass
            else:
                window.append((temp_time, temp_val))
                cur_sum += temp_val
                window_len += 1
    
    
# TODO: write other slidng window functions
# e.g. rolling variance, custom rolling functions