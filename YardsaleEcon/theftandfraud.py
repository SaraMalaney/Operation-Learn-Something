#Theft and Fraud model
import random
import sys
import numpy as np
import scipy.stats as sp
import matplotlib.pyplot as plt

def transaction(array):
	#Randomly select two traders
	traderA = random.randint(0,int(sys.argv[1])-1)
	traderB = random.randint(0,int(sys.argv[1])-1)
	while traderA == traderB:
		traderB = random.randint(0,int(sys.argv[1])-1)
	traderAworth = array[traderA]
	traderBworth = array[traderB]

	#Randomly generate a profit for one trader equal to the loss of the other trader
	#In this model, the profit is some fraction of the loser's worth
	profit = random.randint(0, traderBworth)
	traderAworth += profit
	traderBworth -= profit
	array[traderA] = traderAworth
	array[traderB] = traderBworth

	#Return updated array of traders and their worths
	return array

#Initialize an array of traders all with net worth 100
traders = [100]*int(sys.argv[1])

#Run a specified number of transactions
for i in range(0,int(sys.argv[2])):
	traders = transaction(traders)

#Show results
#print traders

#Calculate percentiles and create histogram data
percentiles = [sp.percentileofscore(traders, i) for i in traders]
data = []

#This is my cheat for creating data that represents the wealth distribution.
#There's got to be a python library for this
for i in range (0,len(traders)):
	if traders[i] != 0:
		data = data + [percentiles[i]]* traders[i]

bins = [0,10,20,30,40,50,60,70,80,90,100]

#Plot results as histogram
plt.hist(data, bins)
plt.title("Theft-and-fraud model of " + str(sys.argv[1]) + " traders after " + str(sys.argv[2]) + " transactions")
plt.xlabel("Percentile")
plt.ylabel("Wealth")
plt.show()
