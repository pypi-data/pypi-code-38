import urllib
class random():
    def anime():
		for line in urllib.request.urlopen('http://neko-bot.net/info/totalanime.txt'):
                   
			nekomax=line

			nekomin=6
		total=randint(int(nekomin),int(nekomax))
		return 'http://neko-bot.net/anime/anime'+str(total)+'.png'

    def neko():
		for line in urllib.request.urlopen('http://neko-bot.net/info/totalnekos.txt'):
                   
			nekomax=line

			nekomin=6
		total=randint(int(nekomin),int(nekomax))
		return 'http://neko-bot.net/nekos/neko'+str(total)+'.png'
