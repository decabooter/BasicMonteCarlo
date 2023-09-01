# -*- coding: utf-8 -*-
"""
Created on Thu Apr 13 12:25:00 2023

@author: decabooter

Next Steps:
    1. combine the two passes through the examples so that I'm not traversing twice (save time?)
    2. add in distribution statistics--average revenue, 10%/90% revenue--by brute force/algorithmically(?)
"""

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import datetime
#import pymc as pm

sns.set_style('whitegrid')

num_reps = 10000 # used for initial graphs of population shape--nothing afterwards.

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

#create lognormal user distribution per site
siteUsersMinMax = [5,25]
users = LogNormal(num_reps)
users.MinMaxtoMuSigma(siteUsersMinMax[0], siteUsersMinMax[1])
users.MakeDistrib(significantDigits=0)
bins = np.arange(users.values.max().round(0))
usersHist = users.NormHist(bins)
usersHist.columns = ["Density", "NormBins", "Number of Users"]
print("Min users = ", siteUsersMinMax[0], " Max users = ", siteUsersMinMax[1])
print ("User Mu = ", users.mu)
print ("User Sigma = ", users.sigma)
print ("Average Users = ", users.Average().round(0))
print(usersHist.to_string(index=False))
#print(usersNormHist.to_string(index=False))

#create lognormal device distribution per site
siteDevicesMinMax = [200,50000]
devices = LogNormal(num_reps)
devices.MinMaxtoMuSigma(siteDevicesMinMax[0], siteDevicesMinMax[1])
devices.MakeDistrib(significantDigits=0)
histBins = [i*siteDevicesMinMax[0] for i in range(2*siteDevicesMinMax[1]//siteDevicesMinMax[0])]
histBins.append(1000000)
deviceHist = devices.NormHist(histBins)
deviceHist.columns = ["Density", "NormBins", "Number of Devices"]
print ("Device Mu = ", devices.mu)
print ("Device Sigma = ", devices.sigma)
print ("Average Devices = ", devices.Average().round(0))
print(deviceHist.to_string(index=False))

fig, (ax1, ax2) = plt.subplots(nrows=2, sharey=False)
sns.scatterplot(data=usersHist, y="Density", x="Number of Users", ax=ax1)
sns.scatterplot(data=deviceHist, y="Density", x="Number of Devices", ax=ax2)

#######################
#Building the device revenue MC biz case
numScenarios = 1000
custPerScenario = 200
discountTable = {
    0: 0,
    250: 0.1,
    1000: 0.15,
    2000: 0.2
    }
costPerDevice = 2.50 #dollar per month
costPerUser = 25 #dollars per month
nonDeviceFraction = 0.1 #fraction of device volume for non-device quantities

#this function will work like the Excel lookup function, where it will provide
# the largest value that is mapped to be equal or less than the inputted value
def lookup(lookupTable, value):
#    for key in reversed(lookupTable.keys()):
    for key in lookupTable.keys():
        if key <= value:
            lookupValue = lookupTable[key]
    return lookupValue

scenarios = pd.DataFrame()

#Generate all of the required scenarios
for j in range(numScenarios):
    if j % 100 == 0:
        now = datetime.datetime.now()
        print("Scenario started: ", j, now.strftime(" %Y-%m-%d %H:%M:%S"))
    scenario = pd.DataFrame()
    for i in range(custPerScenario):
        numPips = devices.GetValue(significantDigits=0)
        numOther = (numPips * nonDeviceFraction).round(0)
        discount = lookup(discountTable, numPips)
        #print("{pips} devices @ {disc}% discount".format(pips=numPips, 
        #                                                  disc=discount*100))
        numUsers = users.GetValue(significantDigits=0)
        monRevPip = (numPips * (1-discount) * costPerDevice).round(0)
        monRevOther = (numOther * (1-discount) * costPerDevice).round(0)
        monRevUsers = (numUsers * (1-discount) * costPerUser).round(0)
        monRevTotal = (monRevPip + monRevOther + monRevUsers).round(0)
        #print("pips: ${pips}, other: ${other}, users: ${users}, total: ${tot}".format(
        #    pips=monRevPip, other=monRevOther, users=monRevUsers, tot=monRevTotal))
        customerID = j*10**np.ceil(np.log10(numScenarios*custPerScenario)+i)
        customer = pd.DataFrame({'Scenario': j,
                                 'Customer': j*10**np.ceil(np.log10(numScenarios*custPerScenario))+i,
                                 'Devices': numPips,
                                 'Other': numOther,
                                 'Users': numUsers,
                                 'Discount': discount,
                                 'Monthly Device Revenue': monRevPip,
                                 'Monthly Other Revenue': monRevOther,
                                 'Monthly Users Revenue': monRevUsers,
                                 'Monthly Total Revenue': monRevTotal},
                                 index=[customerID])
        scenarios = pd.concat([scenarios[:], customer], ignore_index=True)
    #scenarios = pd.concat([scenarios[:], scenario], ignore_index = True)  # I probably should have made this a list of dataframes
#print("Scenarios:")
#print(scenarios.to_string(index=True))

#Determine total monthly and annual revenue numbers for each scenario
totalRevenue = pd.DataFrame(columns=["Scenario", 
                                     "Monthly Device Revenue", 
                                     "Monthly Other Revenue", 
                                     "Monthly Users Revenue",
                                     "Monthly Total Revenue"])
print ("length of scenarios:" , len(scenarios))
#Calculate cumulative monthly revenue per scenario (across all customers in a scenario)
for i in range(len(scenarios)):
    if i % 1000 == 0:
        now = datetime.datetime.now()
        print("Scenario ", i, now.strftime(" %Y-%m-%d %H:%M:%S"))
    #print("Customer:")
    #print(scenarios.loc[i,"Monthly Device Revenue"])
    #print(customer)
    custRev = pd.DataFrame({'Scenario' : scenarios.loc[i,"Scenario"],
                            'Monthly Device Revenue': scenarios.loc[i,"Monthly Device Revenue"],
                            'Monthly Other Revenue': scenarios.loc[i,"Monthly Other Revenue"],
                            'Monthly Users Revenue': scenarios.loc[i,"Monthly Users Revenue"],
                            'Monthly Total Revenue': scenarios.loc[i,"Monthly Total Revenue"]},
                            index=[0])
    #print("cust rev record: ", custRev.to_string(index=True))
    #print(totalRevenue.to_string(index=True))
    if scenarios.loc[i,"Scenario"] in totalRevenue['Scenario'].values:
        totalRevenue.loc[totalRevenue['Scenario']==scenarios.loc[i,"Scenario"],'Monthly Device Revenue'] += scenarios.loc[i,"Monthly device Revenue"]
        totalRevenue.loc[totalRevenue['Scenario']==scenarios.loc[i,"Scenario"],'Monthly Other Revenue'] += scenarios.loc[i,"Monthly Other Revenue"]
        totalRevenue.loc[totalRevenue['Scenario']==scenarios.loc[i,"Scenario"],'Monthly Users Revenue'] += scenarios.loc[i,"Monthly Users Revenue"]
        totalRevenue.loc[totalRevenue['Scenario']==scenarios.loc[i,"Scenario"],'Monthly Total Revenue'] += scenarios.loc[i,"Monthly Total Revenue"]
    else:
        totalRevenue = pd.concat([totalRevenue[:],custRev], ignore_index=True)
    #else:
        #need to figure out how to do addition on specific cells in a dataframe

#print(totalRevenue.to_string(index=True))
        
#calculate the annual revenues
annualDevice = []
annualOther = []
annualUsers = []
annualTotal = []
for i in range(len(totalRevenue)):
    annualDevice.append(totalRevenue.loc[i,'Monthly Device Revenue']*12)
    annualOther.append(totalRevenue.loc[i,'Monthly Other Revenue']*12)
    annualUsers.append(totalRevenue.loc[i,'Monthly Users Revenue']*12)
    annualTotal.append(totalRevenue.loc[i,'Monthly Total Revenue']*12)
        
totalRevenue['Annual Device Revenue'] = annualDevice
totalRevenue['Annual Other Revenue'] = annualOther
totalRevenue['Annual Users Revenue'] = annualUsers
totalRevenue['Annual Total Revenue'] = annualTotal

#print(totalRevenue.to_string(index=True))
revHistogram = np.histogram(totalRevenue['Annual Total Revenue'].values, bins=50, density=False)
revHistDataFrame = pd.DataFrame(revHistogram).T
revHistDataFrame.columns = ["Frequency", "Total Revenue"]


fig2, (ax1) = plt.subplots(nrows=1, sharey=False)
sns.scatterplot(data=revHistDataFrame, y="Frequency", x="Total Revenue", ax=ax1)

#analysis of the numbers
averageRevenue = totalRevenue['Annual Total Revenue'].mean()
revenueRange = totalRevenue['Annual Total Revenue'].quantile([.1,.9])
