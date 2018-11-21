import spotipy
import spotipy.util as util
import urllib.request
from call_models import get_va_scores, get_basic_combine, generate_playlist_va, generate_playlist_be
from titles import get_text_scores
from pprint import pprint
import numpy as np

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
    return user_requests


def add_track(sp, user_requests, artistName, trackName):
    searchVal = "artist:" + artistName + " track:" + trackName
    results = sp.search(q=searchVal, type="track")
    try:
        song = results['tracks']['items'][0]
        saveAs = "userdata/" + song['id'] + ".mp3"
        user_requests[song['id']] = song['name'], song['artists']
        if song['preview_url'] is not None:
            urllib.request.urlretrieve(song['preview_url'], saveAs)
    except:
        pass
    return user_requests


def run_backend(title1, artist1, title2, artist2, title3, artist3):
    user_requests = get_starting_data(title1, artist1, title2, artist2, title3, artist3)
    pprint(user_requests)

    # text
    basic_text_scores, dimensional_text_scores = get_text_scores(user_requests)
    
    # text + dimensional
    user_dimensional_dict = get_va_scores(user_requests, dimensional_text_scores, data = "userdata/")
    print(user_dimensional_dict)

    # text + basic
    user_basic_dict = get_basic_combine('userdata', user_requests, basic_text_scores)
    print(user_basic_dict)

    # dimensional: calculate user valence , user arousal
    user_valence = sum([song["valence"] for song in user_dimensional_dict.values()])/len(user_dimensional_dict)
    user_arousal = sum([song["arousal"] for song in user_dimensional_dict.values()])/len(user_dimensional_dict)

    library_dictionary = get_dictionary()
    library_dictionary = dict(list(library_dictionary.items())[:3])

    library_basic_text_scores, library_dimensional_text_scores = get_text_scores(library_dictionary)
    library_dimensional_dictionary = get_va_scores(library_dictionary, library_dimensional_text_scores)
    song_list = generate_playlist_va(library_dimensional_dictionary, user_valence, user_arousal)
    print(song_list)
    make_playlist("Valence-Arousal", song_list)

    # basic emotion recommendation
    user_basic = user_basic_dict.values()
    user_basic = list(user_basic)
    # print(user_basic)
    user_basic_vec = np.add( user_basic[2], np.add(user_basic[0],user_basic[1] ) )
    np.clip(user_basic_vec, 0, 1, out=user_basic_vec)
    library_basic_dictionary = get_basic_combine('data', library_dictionary, library_basic_text_scores)
    basic_song_list = generate_playlist_be( user_basic_vec, library_basic_dictionary )
    print(basic_song_list)
    make_playlist("Basic-Emotions", basic_song_list)

if __name__ == "__main__":
    run_backend("Happy","Williams","Hello","Adele","We are the champions","Queen")
