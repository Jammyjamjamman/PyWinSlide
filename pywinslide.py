#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 23:12:47 2018

@author: James Sherratt
"""
from datetime import timedelta
    

class Window(object):
    """
    A class used in generating the window of a timeseries.
    
    Attributes:
        init_dat (Iterator((datetime, number))): The initial timeseries tuple
        from the timeseries iterator, for initialising the window.
        win_sz (timedelta): The size of the timeseries window in time.
    """
    
    class Ts_dat(object):
        """
        A class defining a "timeseries" object which contains a
        timestamp and 1 or more values.
        
        Attributes:
            time (datetime): the datetime of the timeseries element.
            val (number): The value corresponding to the datetime.
        """
        def __init__(self, time, val):
            self.time = time
            self.val = val
    
    
    def __init__(self, init_dat, win_sz):
        # Initialise the window.
        self.win = [self.Ts_dat(*init_dat)]
        # store half the window size. This is used to calculate window limits.
        self.half_win_sz = win_sz/2
        self.next_element()
    
    def queue_dat(self, dat):
        """ Queue the next data from a timeseries iterator.
        
            Attributes:
                dat ((datetime, number)): A timeseries tuple from the
                timeseries iterator.
        """
        self.queued_dat = self.Ts_dat(*dat)
    
    def queued_nin_window(self):
        """ Check if the queued timeseries object is not within the current
        window range.
        """
        return self.queued_dat.time > self.cur_win_max

    def next_element(self):
        """ Get the next element to generate the window about. The next element
        is normally within the window, but sometimes it maybe outside the
        window.
        """
        # Add 1 to the position of the current element the window is generated
        # about, to get the next element. If the attribute doesn't exist,
        # create it.
        try:
            self.cur_win_pos += 1
        except AttributeError:
            self.cur_win_pos = 0
        try:
            # Set the value of the time for the window from the next element.
            self.cur_win_time = self.win[self.cur_win_pos].time
            # Get the values of the window limits.
            self.cur_win_min = self.cur_win_time - self.half_win_sz
            self.cur_win_max = self.cur_win_time + self.half_win_sz
        except IndexError:
            # Same as above, but get the values for the queued data if
            # we have reached the end of the elements in the window.
            self.cur_win_time = self.queued_dat.time
            self.cur_win_min = self.cur_win_time - self.half_win_sz
            self.cur_win_max = self.cur_win_time + self.half_win_sz  

    def remove_dat(self):
        """ Remove data which is no longer in the current window limits."""
        while self.win[0].time < self.cur_win_min:
            self.win.pop(0)

    def append_queued(self):
        """ Append the queued data to the window."""
        self.win.append(self.queued_dat)
        
        
    def get_cur_stats(self):
        """ Return the current statistics for the window."""
        return None


class Win_mean_meansq(Window):
    """
    This Window class is used to get a rolling mean and variance from a
    timeseries.
    """
    
    class Ts_dat(Window.Ts_dat):
        """
        A class defining a "timeseries" object which contains a
        timestamp, value and the square of that value.
        
        The constructor requires a timestamp and value.
        """
        def __init__(self, time, val):
            super().__init__(time, val)
            self.val_sq = val*val

    def __init__(self, init_dat, win_sz):
        super().__init__(init_dat, win_sz)
        # Store the window length, keep a total of the values in the window and
        # the total of the values squared. These are used for calculating the
        # mean and variance.
        self.win_len = 1
        self.sum = self.win[self.cur_win_pos].val
        self.sum_sq = self.win[self.cur_win_pos].val_sq
    
    def append_queued(self):
        # Append the queued timeseries data and add its value and value squared
        # to the sum of the queued data. Increment the length of the window.
        super().append_queued()
        self.sum += self.queued_dat.val
        self.sum_sq += self.queued_dat.val_sq
        self.win_len += 1
    
    def remove_dat(self):
        while self.win[0].time < self.cur_win_min:
            # Remove data not in the window from the window.
            last_ts_dat = self.win.pop(0)
            # Subtract the value and value squared from the total.
            # Decrement the window length and the position of the current
            # element we are calculating the window about.
            self.sum -= last_ts_dat.val
            self.sum_sq -= last_ts_dat.val_sq
            self.win_len -= 1
            self.cur_win_pos -= 1
        

    def get_cur_stats(self):
        """ Returns the time, mean and variance for the current window.
        Variance is undefined if the number of elements in the window is 1.
        
        Returns:
            ((datetime, number, number)): The time, mean and variance of a
            window.
        """
        try:
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    (self.sum_sq - self.sum**2/self.win_len)/(self.win_len - 1))
        except ZeroDivisionError:
            # Return variance as none if there's only 1 element in the window.
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    None)
 

def sliding_window(dat_iter,
                   window_sz = timedelta(days=1),
                   Window_cls = Window):
    """
    Creates a generic Window generator from a timeseries iterator.
    
    Args:
        dat_iter (Iterator((datetime, number))): Produces a tuple each
        iteration containing a timestamp and a number which can be averaged.
        window_sz (timedelta): The size of the moving window (in time).
        Default window size is 1 day.
        Window_cls (Window): The class to use to generate a window with (this
        should be a subclass of Window).
    
    Yields:
        None, with the default Window class.
    """
    
    # Get the inital timeseries tuple and use it to generate a Window object.
    dat = next(dat_iter)
    window = Window_cls(dat, window_sz)  
    
    # Iterate through the rest of the timeseries tuple.
    for dat in dat_iter:
        # Queue the next dat in the window.
        window.queue_dat(dat)
        
        # Check if the queued element is not in the window bounds.
        while window.queued_nin_window():
            # Remove elements that are no longer within the window bounds.
            window.remove_dat()
            # Get the statistics for the elements in the window.
            yield window.get_cur_stats()
            # Get the next element from the window.
            window.next_element()
        
        # When the queued element is within the window, append it to the queue.
        window.append_queued()


def sliding_mean_var(dat_iter,
                     window_sz = timedelta(days=1)):
    """
    Creates an iterator which calculates the rolling mean and variance
    from a timeseries iterator.
    The time series iteratore should return values in ascending order of time.
    
    Args:
        dat_iter (Iterator((datetime, number))): Produces a tuple each
        iteration containing a timestamp and a number which can be averaged.
        window_sz (timedelta): The size of the moving window (in time).
        Default window size is 1 day.
    
    Yields:
        (datetime, float, float): A tuple containing the timestamp, mean and
        variance.
        
    TODO:
    1. Improve commments.
    2. Improve how function is written.
    3. Add tests.
    4. Write a more cython-friendly version for speed improvements
    """
    return sliding_window(dat_iter, window_sz, Win_mean_meansq)


class Win_mean_ds(Window):
    """
    This Window class is used to downsample a timeseries. This is done by
    taking the mean of elements within the downsampling frequency. The
    frequency can simply be thought of as the window size.
    
    Health warning: when I say frequency, the class technically wants a period.
    E.g. if I want to sample every 3 mins, freq is set to timedelta(minutes=3).
    
    Attributes:
        init_dat (Iterator((datetime, number))): The initial timeseries tuple
        from the timeseries iterator, for initialising the window.
        frequency (timedelta): The new period in which to take samples
    """
    
    def __init__(self, init_dat, freq):
        if freq.total_seconds == 0.0:
            raise ValueError("frequency of samples must be greater than 0!")
        self.freq = freq
        super().__init__(init_dat, win_sz = freq)
        self.sum = self.win[0].val
        self.win_len = 1

    def next_element(self):
        try:
            self.cur_win_time += self.freq
        except AttributeError:
            self.cur_win_time = self.win[0].time
            # Zero the window time to the number of significant figures of freq.
            if self.freq.microseconds == 0:
                self.cur_win_time = self.cur_win_time.replace(microsecond=0)
                if self.freq.seconds % 60 == 0:
                    self.cur_win_time = self.cur_win_time.replace(second=0)
                    if self.freq.seconds % 3600 == 0:
                        self.cur_win_time = self.cur_win_time.replace(minute=0)
                        if self.freq.seconds % 86400 == 0:
                            self.cur_win_time = self.cur_win_time.replace(hour=0)
        
        # Set the window limits.
        self.cur_win_min = self.cur_win_time - self.half_win_sz
        self.cur_win_max = self.cur_win_time + self.half_win_sz

    def append_queued(self):
        # Append queued data if within the sampling window.
        super().append_queued()
        self.sum += self.queued_dat.val
        self.win_len += 1
        
    def remove_dat(self):
        # Remove data not within the sampling window.
        try:
            while self.win[0].time < self.cur_win_min:
                self.sum -= self.win.pop(0).val
                self.win_len -= 1
        except IndexError:
            pass
            
    def get_cur_stats(self):
        """ Returns the timestamp and mean for the current sample."""
        try:
            return (self.cur_win_time,
                    self.sum/self.win_len)
        except ZeroDivisionError:
            return (self.cur_win_time,
                    None)
            
            
def mean_downresample(dat_iter, freq):
    """
    Creates an iterator which downsamples from a timeseries iterator frequency,
    using the rolling mean.
    The time series iteratore should return values in ascending order of time.
    
    Args:
        dat_iter (Iterator((datetime, number))): Produces a tuple each
        iteration containing a timestamp and a number which can be averaged.
        freq (timedelta): The new frequency of the timeseries after
        downsampling.
    
    Yields:
        (datetime, float): A tuple containing a timestamp and mean.
    """
    return sliding_window(dat_iter, window_sz=freq, Window_cls=Win_mean_ds)
# TODO: write other slidng window functions
# e.g. rolling variance, custom rolling functions