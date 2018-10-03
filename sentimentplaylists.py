import spotipy
import spotipy.util as util
import os


#this is me
SPOTIFY_USERNAME = "oxa11ce"
#this a very large playlist (about 5k songs)
SPOTIFY_CORPUS_PLAYLIST = "spotify:user:oxa11ce:playlist:5mbCI94sPHLJssUO3t3fIf"

SPOTIFY_SCOPE= "playlist-read-private"

 # spotipy authorization
token = util.prompt_for_user_token(SPOTIFY_USERNAME,SPOTIFY_SCOPE)
sp = spotipy.Spotify(token)


def main():
   

    tracks = tracksInPlaylist(SPOTIFY_USERNAME, SPOTIFY_CORPUS_PLAYLIST)
    print(namesOfTracks(tracks))
    
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
        
        names.append(track['track']['name'])
    return names    

if __name__ == "__main__":
    main()