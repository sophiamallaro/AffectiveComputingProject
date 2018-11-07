import spotipy
import urllib
from spotipy.oauth2 import SpotifyClientCredentials

client_ID = 'f82a64e59bf443b5bc2cd79765c90ea8'
client_SECRET = 'd112b2080bd848f1be4df9b659bb6280'
client_credentials_manager = SpotifyClientCredentials(client_id=client_ID, client_secret=client_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'

results = spotify.search(q='artist:' + 'Taylor Swift', type='artist')
items = results['artists']['items']
uri = items[0]['uri']

results = spotify.artist_top_tracks(uri)

for track in results['tracks'][:20]:
    print(track['name'])
    print(track['artists'][0]['name'])
