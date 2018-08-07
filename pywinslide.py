#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 23:12:47 2018

@author: James Sherratt
"""
from datetime import timedelta
    

class Window(object):
    class Ts_dat(object):
        def __init__(self, time, val):
            self.time = time
            self.val = val
    
    
    def __init__(self, init_dat, win_sz):
        self.win = [self.Ts_dat(*init_dat)]
        self.half_win_sz = win_sz/2
        self.next_element()
    
    
    def queue_dat(self, dat):
        self.queued_dat = self.Ts_dat(*dat)
    
    
    def queued_nin_window(self):
        return self.queued_dat.time > self.cur_win_max
    
    
    def next_element(self):
        try:
            self.cur_win_pos += 1
        except AttributeError:
            self.cur_win_pos = 0
        try:
            self.cur_win_time = self.win[self.cur_win_pos].time
            self.cur_win_min = self.cur_win_time - self.half_win_sz
            self.cur_win_max = self.cur_win_time + self.half_win_sz
        except IndexError:
            self.cur_win_time = self.queued_dat.time
            self.cur_win_min = self.cur_win_time - self.half_win_sz
            self.cur_win_max = self.cur_win_time + self.half_win_sz
        
    
    def remove_dat(self):
        while self.win[0].time < self.cur_win_min:
            self.win.pop(0)
        
    
    def append_queued(self):
        self.win.append(self.queued_dat)
        
        
    def get_cur_stats(self):
        return None


class Win_mean_meansq(Window):
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
        self.win_len = 1
        self.sum = self.win[self.cur_win_pos].val
        self.sum_sq = self.win[self.cur_win_pos].val_sq
    
    
    def append_queued(self):
        super().append_queued()
        self.sum += self.queued_dat.val
        self.sum_sq += self.queued_dat.val_sq
        self.win_len += 1
        
    
    def remove_dat(self):
        while self.win[0].time < self.cur_win_min:
            last_ts_dat = self.win.pop(0)
            self.sum -= last_ts_dat.val
            self.sum_sq -= last_ts_dat.val_sq
            self.win_len -= 1
            self.cur_win_pos -= 1
        

    def get_cur_stats(self):
        try:
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    (self.sum_sq - self.sum**2/self.win_len)/(self.win_len - 1))
        except ZeroDivisionError:
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    None)
 

def sliding_window(dat_iter,
                   window_sz = timedelta(days=1),
                   Window_cls = Window):
    
    dat = next(dat_iter)
    window = Window_cls(dat, window_sz)  
    
    for dat in dat_iter:
        window.queue_dat(dat)
        
        while window.queued_nin_window():
            window.remove_dat()
            
            yield window.get_cur_stats()
            window.next_element()
            
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
        (datetime, float, float): The next "rolling mean and variance"
        as a tuple containing the timestamp and datetime.
        
    TODO:
    1. Improve commments.
    2. Improve how function is written.
    3. Add tests.
    4. Write a more cython-friendly version for speed improvements
    """
    return sliding_window(dat_iter, window_sz, Win_mean_meansq)


class Win_mean_ds(Window):
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
            
            if self.freq.microseconds == 0:
                self.cur_win_time = self.cur_win_time.replace(microsecond=0)
                if self.freq.seconds % 60 == 0:
                    self.cur_win_time = self.cur_win_time.replace(second=0)
                    if self.freq.seconds % 3600 == 0:
                        self.cur_win_time = self.cur_win_time.replace(minute=0)
                        if self.freq.seconds % 86400 == 0:
                            self.cur_win_time = self.cur_win_time.replace(hour=0)

        self.cur_win_min = self.cur_win_time - self.half_win_sz
        self.cur_win_max = self.cur_win_time + self.half_win_sz



    def append_queued(self):
        super().append_queued()
        self.sum += self.queued_dat.val
        self.win_len += 1
        
    
    def remove_dat(self):
        try:
            while self.win[0].time < self.cur_win_min:
                self.sum -= self.win.pop(0).val
                self.win_len -= 1
        except IndexError:
            pass
            
    
    
    def get_cur_stats(self):
        try:
            return (self.cur_win_time,
                    self.sum/self.win_len)
        except ZeroDivisionError:
            return (self.cur_win_time,
                    None)
            
            
def mean_downresample(dat_iter, freq):
    return sliding_window(dat_iter, window_sz=freq, Window_cls=Win_mean_ds)
# TODO: write other slidng window functions
# e.g. rolling variance, custom rolling functions