#Econophysics
import random
import sys
import numpy as np
import scipy.stats as sp
import matplotlib.pyplot as plt

def yardsale_transaction(array):
	#Randomly select two traders
	traderA = random.randint(0,int(sys.argv[1])-1)
	traderB = random.randint(0,int(sys.argv[1])-1)
	while traderA == traderB:
		traderB = random.randint(0,int(sys.argv[1])-1)
	traderAworth = array[traderA]
	traderBworth = array[traderB]

	#Randomly generate a profit for one trader equal to the loss of the other trader
	profit = random.randint(0, min(traderAworth, traderBworth))
	traderAworth += profit
	traderBworth -= profit
	array[traderA] = traderAworth
	array[traderB] = traderBworth
	#Return updated array of traders and their worths
	return array

def theftandfraud_transaction(array):
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

def marriageanddivorce_transaction(array):
	#Randomly select two traders
	traderA = random.randint(0,int(sys.argv[1])-1)
	traderB = random.randint(0,int(sys.argv[1])-1)
	while traderA == traderB:
		traderB = random.randint(0,int(sys.argv[1])-1)
	traderAworth = array[traderA]
	traderBworth = array[traderB]

	#Randomly generate a split of the sum of both traders' worth
	sumOfTraderWorths = traderAworth + traderBworth
	traderAworth = random.randint(0, sumOfTraderWorths)
	traderBworth = sumOfTraderWorths - traderAworth
	array[traderA] = traderAworth
	array[traderB] = traderBworth
	#Return updated array of traders and their worths
	return array

#Initialize an array of traders all with net worth 100
yardsale_traders = [100]*int(sys.argv[1])
theftandfraud_traders = [100]*int(sys.argv[1])
marriageanddivorce_traders = [100]*int(sys.argv[1])

#Run a specified number of transactions
for i in range(0,int(sys.argv[2])):
	yardsale_traders = yardsale_transaction(yardsale_traders)
	theftandfraud_traders = theftandfraud_transaction(theftandfraud_traders)
	marriageanddivorce_traders = marriageanddivorce_transaction(marriageanddivorce_traders)

#Calculate percentiles and create histogram data
yardsale_percentiles = [sp.percentileofscore(yardsale_traders, i) for i in yardsale_traders]
theftandfraud_percentiles = [sp.percentileofscore(theftandfraud_traders, i) for i in theftandfraud_traders]
marriageanddivorce_percentiles = [sp.percentileofscore(marriageanddivorce_traders, i) for i in marriageanddivorce_traders]
yardsale_data = []
theftandfraud_data = []
marriageanddivorce_data = []

#This is my cheat for creating data that represents the wealth distribution.
#There's got to be a python library for this
for i in range (0,len(yardsale_traders)):
	if yardsale_traders[i] != 0:
		yardsale_data = yardsale_data + [yardsale_percentiles[i]]* yardsale_traders[i]
for i in range (0,len(theftandfraud_traders)):
	if theftandfraud_traders[i] != 0:
		theftandfraud_data = theftandfraud_data + [theftandfraud_percentiles[i]]* theftandfraud_traders[i]
for i in range (0,len(marriageanddivorce_traders)):
	if marriageanddivorce_traders[i] != 0:
		marriageanddivorce_data = marriageanddivorce_data + [marriageanddivorce_percentiles[i]]* marriageanddivorce_traders[i]

bins = [0,10,20,30,40,50,60,70,80,90,100]

#Plot results as histograms
fig1 = plt.figure(1)
fig1.suptitle(str(sys.argv[1]) + " traders after " + str(sys.argv[2]) + " transactions", fontsize=20)
ax1 = plt.subplot2grid((2,4), (0, 0), colspan=2)
ax1.hist(yardsale_data, bins)
ax1.set_title('Yardsale')
ax1.set_xlabel('Percentile')
ax1.set_ylabel('Wealth')

ax2 = plt.subplot2grid((2,4), (0, 2), colspan=2)
ax2.hist(theftandfraud_data, bins)
ax2.set_title('Theft-and-fraud')
ax2.set_xlabel('Percentile')

ax3 = plt.subplot2grid((2,4), (1, 1), colspan=2)
ax3.hist(marriageanddivorce_data, bins)
ax3.set_title('Marriage-and-divorce')
ax3.set_xlabel('Percentile')
ax3.set_ylabel('Wealth')

plt.subplots_adjust(top=0.85, hspace=0.4, wspace = 0.8)
plt.show()

