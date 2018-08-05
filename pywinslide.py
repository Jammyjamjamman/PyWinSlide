#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Aug  1 23:12:47 2018

@author: James Sherratt
"""
from datetime import timedelta


class Ts_val_valsq(object):
    """
    A class defining a "timeseries" object which contains a
    timestamp, value and the square of that value.
    
    The constructor requires a timestamp and value.
    """
    def __init__(self, time, val):
        self.time = time
        self.val = val
        self.val_sq = val*val
    

class Win_mean_meansq(object):
    def __init__(self, init_Ts_val_valsq, win_sz):
        self.win = [init_Ts_val_valsq]
        self.sum = init_Ts_val_valsq.val
        self.sum_sq = init_Ts_val_valsq.val_sq
        self.win_len = 1
        self.half_win_sz = win_sz/2
        self.next_element_update()
    
    
    def append_dat(self, ts_val_valsq_ins):
        self.win.append(ts_val_valsq_ins)
        self.sum += ts_val_valsq_ins.val
        self.sum_sq += ts_val_valsq_ins.val_sq
        self.win_len += 1
        
    
    def remove_dat(self):
        while self.win[0].time < self.cur_win_min:
            last_ts_val_valsq_ins = self.win.pop(0)
            self.sum -= last_ts_val_valsq_ins.val
            self.sum_sq -= last_ts_val_valsq_ins.val_sq
            self.win_len -= 1
            self.cur_win_pos -= 1
    
    
    def update_with_other_ts_val(self, ts_val_valsq_ins):
        self.cur_win_time = ts_val_valsq_ins.time
        self.cur_win_min = self.cur_win_time - self.half_win_sz
        self.cur_win_max = self.cur_win_time + self.half_win_sz
    
    
    def next_element_update(self):
        try:
            self.cur_win_pos += 1
        except AttributeError:
            self.cur_win_pos = 0
        self.cur_win_time = self.win[self.cur_win_pos].time
        self.cur_win_min = self.cur_win_time - self.half_win_sz
        self.cur_win_max = self.cur_win_time + self.half_win_sz
        self.remove_dat()
        
        
    
    def get_stats(self):
        try:
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    (self.sum**2 - self.sum_sq)/(self.win_len - 1))
        except ZeroDivisionError:
            return (self.cur_win_time,
                    self.sum/self.win_len,
                    None)


def sliding_mean_var(dat_iter,
                     window_sz = timedelta(days=1),
                     Ts_cls = Ts_val_valsq,
                     Win_cls = Win_mean_meansq):
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
    
    next_dat = Ts_cls(*next(dat_iter))
    
    window = Win_cls(next_dat, window_sz)
    
    for dat in dat_iter:
        next_dat = Ts_cls(*dat)
        
        while next_dat.time > window.cur_win_max:
            window.remove_dat()
            
            yield window.get_stats()
            
            try:
                window.next_element_update()
            except IndexError:
                window.update_with_other_ts_val(next_dat)
                break
        
        window.append_dat(next_dat)


# TODO: write other slidng window functions
# e.g. rolling variance, custom rolling functions