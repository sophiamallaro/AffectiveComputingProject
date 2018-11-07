import spotipy
import urllib
from spotipy.oauth2 import SpotifyClientCredentials

client_ID = 'f82a64e59bf443b5bc2cd79765c90ea8'
client_SECRET = 'd112b2080bd848f1be4df9b659bb6280'
client_credentials_manager = SpotifyClientCredentials(client_id=client_ID, client_secret=client_SECRET)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

lz_uri = 'spotify:artist:36QJpDe2go2KgaRleHCDTp'
results = spotify.artist_top_tracks(lz_uri)

for track in results['tracks'][:10]:
    print(track['name'])
    print(track['artists'][0]['name'])
    #print(track['artists'])
    #print('track    : ' + track['name'])
    #print(track['artists'])
    #print('audio    : ' + track['preview_url'])
    #print('cover art: ' + track['album']['images'][0]['url'])

    urllib.request.urlretrieve(track['preview_url'], 'test.mp3')
