import aiohttp, asyncio,json
class votes():
    async def user_voted(client,ID):
         """
            client = your DBL token
            ID = the USER you are trying to get

            If user has voted, it will return True.
            If the user HAS NOT voted, it will return False.
            Keep that in mind!
         """
         voteurl="https://discordbots.org/api/bots/543966796944769044/votes"
         async with aiohttp.ClientSession(headers=client).get(voteurl) as r:
                 
            
         
             json=await r.text()
         if ID in str(json):
             return True
         else:
             return False
    async def vote_updates(client,timer=60,):
         """
            client = your DBL token
            timer = delay between checks. Defaults to 60 seconds.

            If user has voted, it will return True.
            If the user HAS NOT voted, it will return False.
            Keep that in mind!
         """
         with open("votes_temp.txt") as PreviousText:
             PreviousText = PreviousText.read()
         voteurl="https://discordbots.org/api/bots/543966796944769044/votes"
         async with aiohttp.ClientSession(headers=client).get(voteurl) as r:
            text=r.text()
            
            
         

         if PreviousText != text:
            print("User Voted")
            return True
            with open("votes_temp.txt", 'w') as CurrentText:
                CurrentText.write(text)
        
        
