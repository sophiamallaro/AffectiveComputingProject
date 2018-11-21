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
        user_tracks[track['id']] = (track['name'], track['artists']) # id = name, artist
        downloadMP3(track['preview_url'], track['id'])


def downloadMP3(url, id):
    saveAs = "data/" + id + ".mp3"
    if url is not None:
        urllib.request.urlretrieve(url, saveAs)
    else:
        del user_tracks[id]


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


def addTrackToPlaylist(sp, playlist_id, songs):
    song_ids = []
    for counter, key in enumerate(songs):
        if counter < 50:
            song_ids.append(key)
    sp.user_playlist_add_tracks('al321rltkr20p7oftb0i801lk', playlist_id, song_ids)


def make_playlist(name, songs):
    sp = generate_token()
    playlists = sp.user_playlist_create(USERNAME, name, public=False)
    playlistID = playlists['id']
    addTrackToPlaylist(sp, playlistID, songs)
    return playlistID


def get_dictionary():
    sp = generate_token()
    get_user_tracks(sp)
    return user_tracks

def get_starting_data(title1, artist1, title2, artist2, title3, artist3):
    sp = generate_token()
    user_requests = {}
    user_requests = add_track(sp, user_requests, artist1, title1)
    user_requests = add_track(sp, user_requests, artist2, title2)
    user_requests = add_track(sp, user_requests, artist3, title3)
    print(user_requests)


def add_track(sp, user_requests, artistName, trackName):
    searchVal = "artist:" + artistName + " track:" + trackName
    results = sp.search(q=searchVal, type="track")
    try:
        song = results['tracks']['items'][0]
        saveAs = "userdata/" + song['id'] + ".mp3"
        user_requests[song['id']] = song['name']#, song['artists']
        if song['preview_url'] is not None:
            urllib.request.urlretrieve(song['preview_url'], saveAs)
    except:
        pass
    return user_requests


