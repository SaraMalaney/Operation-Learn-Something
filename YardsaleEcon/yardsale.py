#Yardsale Economics
import random
import sys

def transaction(array):
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

#Initialize an array of traders all with net worth 100
traders = [100]*int(sys.argv[1])

#Run a specified number of transactions
for i in range(0,int(sys.argv[2])):
	traders = transaction(traders)

#Show results
print traders

