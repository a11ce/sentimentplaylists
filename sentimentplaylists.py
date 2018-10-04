import spotipy
import spotipy.util as util
import os
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from textblob import TextBlob 

#this is me
SPOTIFY_USERNAME = "oxa11ce"

# UNCOMMENT THE LARGE PLAYLIST IF NOT TESTING
#this a very large playlist (about 5k songs)
#SPOTIFY_CORPUS_PLAYLIST = "spotify:user:oxa11ce:playlist:5mbCI94sPHLJssUO3t3fIf"
#this is a much smaller playlist for faster testing
SPOTIFY_CORPUS_PLAYLIST = "spotify:user:oxa11ce:playlist:5PBI12H84cg9KIMc4SKfn1"

SPOTIFY_SCOPE= "playlist-read-private"
 # spotipy authorization
token = util.prompt_for_user_token(SPOTIFY_USERNAME,SPOTIFY_SCOPE)
sp = spotipy.Spotify(token)

GENIUS_TOKEN = os.environ.get("GENIUS_CLIENT_ACCESS_TOKEN", None)
assert GENIUS_TOKEN is not None, "Must declare environment variable: GENIUS_CLIENT_ACCESS_TOKEN"


def main():
   

    tracks = tracksInPlaylist(SPOTIFY_USERNAME, SPOTIFY_CORPUS_PLAYLIST)
    print(namesOfTracks(tracks))
    #print(idsOfTracks(tracks))
    polaritiesDict = trackNamesPolaritiesDict(tracks)
    #print(polaritiesDict)
    print(averagePolarity(polaritiesDict))
        
    
def tracksInPlaylist(user,playlist):
    #spotify only gives 100 at a time, thanks ackleyrc
    batch = sp.user_playlist_tracks(user,playlist)
    tracks = batch['items']
    while batch['next']:
        batch = sp.next(batch)
        tracks.extend(batch['items'])
    return tracks    

def namesOfTracks(tracks):
    names = []
    for track in tracks:        
        names.append(nameOfTrack(track))
    return names    

def nameOfTrack(track):
    return track['track']['name']

def idsOfTracks(tracks):
    ids = []
    for track in tracks:
        ids.append(idOfTrack(track))
    return ids

def idOfTrack(track):
    return track['track']['id']

def artistOfTrack(track):
    return track['track']['artists'][0]['name']

def lyricsOfTracks(tracks):
    lyrics = []
    for track in tqdm(tracks):
        lyrics.append(lyricsOfTrack(nameOfTrack(track),artistOfTrack(track)))
    return lyrics

def lyricsOfTrack(trackName,artistName):
    # from https://dev.to/willamesoares/how-to-integrate-spotify-and-genius-api-to-easily-crawl-song-lyrics-with-python-4o62
    base_url = 'https://api.genius.com'
    headers = {'Authorization': 'Bearer ' + GENIUS_TOKEN}
    search_url = base_url + '/search'
    data = {'q': trackName + ' ' + artistName}
    response = requests.get(search_url, data=data, headers=headers)    
    json = response.json()
    remote_song_info = None    
    for hit in json['response']['hits']:
        if artistName.lower() in hit['result']['primary_artist']['name'].lower():
            remote_song_info = hit
            break
    lyrics = None
    if remote_song_info:
        song_url = remote_song_info['result']['url']
        page = requests.get(song_url)
        html = BeautifulSoup(page.text, 'html.parser')
        lyrics = html.find('div', class_='lyrics').get_text()
        
    return lyrics    

def polarityOfLyrics(lyrics):
    if(lyrics):
        return TextBlob(lyrics).sentiment.polarity
    else:
        return None

def trackNamesPolaritiesDict(tracks):
    dictionary = {}
    for track in tqdm(tracks):
        dictionary = {**dictionary, **trackNamePolarityDict(track)}
    return dictionary

def trackNamePolarityDict(track):
    return {nameOfTrack(track): polarityOfLyrics(lyricsOfTrack(nameOfTrack(track),artistOfTrack(track)))}        

def averagePolarity(polarityDict):
    count = 0
    sum = 0
    for key,value in polarityDict.items():
        if(value):
            count = count + 1
            sum = sum + value
    return sum/count        

if __name__ == "__main__":
    main()