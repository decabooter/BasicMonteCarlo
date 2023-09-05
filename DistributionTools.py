# -*- coding: utf-8 -*-
"""
Created on Tue Sep  5 16:34:28 2023

@author: decabooter
"""
import numpy as np
import pandas as pd

class LogNormal (object):
    def __init__(self, num_reps):
        self.num_reps = num_reps
        self.mu = 10
        self.sigma = 1
        self.values = []
        
    # MinMax assumes values represent 90% range of values
    def MinMaxtoMuSigma (self, minValue, maxValue):
        self.mu = (np.log(minValue)+np.log(maxValue))/2
        self.sigma = (np.log(maxValue)-np.log(minValue))/3.29
        return [self.mu,self.sigma]
    
    def Average (self):
        average = np.exp(self.mu + self.sigma**2 / 2)
        return average
    
    def MakeDistrib (self, significantDigits):
        self.values = np.random.lognormal(self.mu, self.sigma, self.num_reps).round(significantDigits)
        return self.values
    
    def GetValue (self, significantDigits):
        value = np.random.lognormal(self.mu, self.sigma, 1).round(significantDigits)
        return value[0]
    
    #this function outputs a 2 column data frame: [count, bin] where bin values
    # are defined by binArray (1D number array)
    def Histogram (self, binArray):
        histogram = np.histogram(self.values, bins=binArray, density=False)
        histDataFrame = pd.DataFrame(histogram).T
        histDataFrame.columns = ["count", "bin"]
        return histDataFrame
    
    #this function outputs a 3 column data frame: [count, bin, bin labels]
    # where bin values and count are normalized vs. num_reps and 
    # bin labels = the actual values.
    # goal:  create a dataframe that bins appropriately, but can be printed
    def NormHist (self, binArray):
        histogram = self.Histogram(binArray)
        normHist = pd.DataFrame()
        normHist["count"] = histogram["count"]/self.num_reps
        normHist["bin"] = histogram["bin"]/self.num_reps
        normHist["binLabels"] = histogram["bin"]
        return normHist
