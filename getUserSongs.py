import spotipy.oauth2 as oauth2
import sys
import spotipy
import spotipy.util as util
import urllib.request


CLIENT_ID = '0e7ea227ef7d407b8bf47a4c545adb3c'
CLIENT_SECRET = '267e96c4713f46d4885a4ea6a099ead4'
USERNAME = 'al321rltkr20p7oftb0i801lk'
user_tracks = {} # dictionary of all user tracks


def generate_token(): # generate api token
    token = util.prompt_for_user_token(
        username=USERNAME,
        scope='user-library-read playlist-modify-private',
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
        redirect_uri='http://www.google.com')
    sp = spotipy.Spotify(auth=token)
    return sp


def make_dictionary(tracks):
    for item in tracks['items']:
        track = item['track']
        user_tracks[track['id']] = (track['name'], track['artists'][0]['name']) # id = name, artist
        downloadMP3(track['preview_url'], track['id'])


def downloadMP3(url, id):
    saveAs = "data/" + id + ".mp3"
    if url is not None:
        urllib.request.urlretrieve(url, saveAs)


def get_user_tracks(sp):
    playlists = sp.current_user_playlists(limit=50)
    for playlist in playlists['items']:
        print(playlist['name'])
        print('  total tracks', playlist['tracks']['total'])
        results = sp.user_playlist(USERNAME, playlist['id'], fields="tracks,next")
        tracks = results['tracks']
        make_dictionary(tracks)
        while tracks['next']:
            tracks = sp.next(tracks)
            make_dictionary(tracks)


def addTrackToPlaylist(sp, playlist_id):
    song_ids = []
    for counter, key in enumerate(user_tracks):
        if counter < 50:
            song_ids.append(key)
    sp.user_playlist_add_tracks('al321rltkr20p7oftb0i801lk', playlist_id, song_ids)


def make_playlist(sp):
    playlists = sp.user_playlist_create(USERNAME, 'TEST PLAYLIST3', public=False)
    playlistID = playlists['id']
    return playlistID


def get_songs():
    sp = generate_token()
    get_user_tracks(sp)
    #print(user_tracks)
    id = make_playlist(sp)
    addTrackToPlaylist(sp, id)
    return user_tracks

if __name__ == "__main__":
    get_songs()