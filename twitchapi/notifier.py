import aiohttp


class Twitch:
    def __init__(self, client_id, client_secret):
       self.data = {'client_id': client_id, 'client_secret': client_secret, 'grant_type': 'client_credentials'}
    
    async def authorization(self):
        async with aiohttp.ClientSession() as session:
            async with session.post('https://id.twitch.tv/oauth2/token', data=self.data) as resp:
                d = await resp.json()
                return d['access_token']
        
    async def get_stream_status(self, token, login):
        url = 'https://api.twitch.tv/helix/streams'
        headers = {'Authorization': 'Bearer '+ token, 'Client-Id': self.data['client_id']}
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=headers, params={'user_login': login}) as resp:
                return await resp.json()

