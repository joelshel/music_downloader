#!/usr/bin/env python3

from functools import partial
import http
import json
from multiprocessing.pool import ThreadPool
from os.path import isdir, isfile, expanduser
from os import listdir, mkdir, remove
import re
from urllib3.util.retry import Retry
import requests as r
import spotipy as sp
from spotipy.oauth2 import SpotifyClientCredentials as SCC
from spotipy.client import SpotifyException
import yt_dlp


COOKIES = "cookies.txt"

#* SpotifyOAuth can be used but need to be imported +
#* redirect_uri is needed, you should set a scope and
#* there's need to have some user interaction but
#* you get access to things like private playlists

def get_spotify_data(username, playlist_name):
    with open("credentials.json", "r") as f:
        credent = json.load(f)
    
    # scope = 'playlist-read-private'
    client_id = credent['client_id']
    client_secret = credent['client_secret']
    # redirect_uri = credent['redirect_uri']

    credentials = SCC(client_id, client_secret)
    results = sp.Spotify(client_credentials_manager=credentials)

    try:
        playlists = results.user_playlists(username)
    except SpotifyException:
        return 1

    playlist_dict = {}
    
    while playlists:
        for playlist in playlists['items']:
            playlist_dict[playlist['name']] = playlist['id']
        if playlists['next']:
            playlists = results.next(playlists)
        else:
            break

    if playlist_name not in playlist_dict:
        return 2

    playlist_id = playlist_dict[playlist_name]

    musics = results.playlist(playlist_id)
    music_dict = {}

    while musics:
        try:
            lst = musics['tracks']['items']
            next = musics['tracks']
        except KeyError:
            lst = musics['items']
            next = musics
        
        for i, music in enumerate(lst):
            name = music['track']['name']
            artists=[]
            for artist in music['track']['artists'][:2]:
                artists.append(artist['name'])
            music_dict[i + next['offset']] = name, artists
        
        if next['next']:
            musics = results.next(next)
        else:
            break
    
    return music_dict


def get_music_path(music_data, count=0):
    yt_search_url="https://www.youtube.com/results?"
    i = music_data[0]
    music = music_data[1][0]
    artists = music_data[1][1]
    
    search_term = music + " " + " ".join(artists)
    params = {"search_query": search_term}
    
    session = r.Session()
    retry = Retry(connect=3, backoff_factor=0.5)
    adapter = r.adapters.HTTPAdapter(max_retries=retry)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    
    try:
        result = session.get(yt_search_url, params=params, timeout=(3, 15))
    except r.Timeout: # r.exceptions.SSLError
        if count >= 3:
            return None
        return get_music_path(music_data, count + 1)
    
    #* regex to match /watch?v= and the next 11 characters
    path = re.search("/watch\?v=.{11}", result.text).group()
    return path


def download_music(path, playlist, destination=f"{expanduser('~')}/Music/", count=0):
    # socket timeout is not enough needs another kind of timeout
    yt_url="https://www.youtube.com"
    
    ydl_opts = {
        'cookiefile': COOKIES,
        'format': 'm4a/bestaudio/best',
        'outtmpl': f'{destination}%(title)s.%(ext)s',
        'download_archive': f'{destination}downloaded_songs_{playlist}.txt',
        'cachedir': False,
        'socket_timeout': 10
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url + path])
    except http.cookiejar.LoadError:
        remove_cookies()
    except (yt_dlp.utils.DownloadError, TimeoutError, FileNotFoundError):
        pass
    else:
        return
    
    if count >= 3:
        return
    download_music(path, playlist, destination, count+1)


#* Function created because it is possible to enter the if statement with the
#* file existing and tries to remove without it exists due to multiprocessing
def remove_cookies():
    try:
        if isfile(COOKIES):
            remove(COOKIES)
    except FileNotFoundError:
        pass


def create_m3u(playlist_path):
    music_names = listdir(playlist_path)
    
    playlist_path = playlist_path.split("/")
    path, playlist = "/".join(playlist_path[:-2]), playlist_path[-2]
    
    music_names = [f"./{playlist}/{music_name}\n" for music_name in music_names]
    
    with open(path + "/" + playlist + ".m3u", "w") as m3u:
        m3u.writelines(music_names)


def get_music_paths(username, playlist):
    spotify_data = get_spotify_data(username, playlist)

    if spotify_data == 1:
        return "Username not found"
    elif spotify_data == 2:
        return "Playlist not found"

    with ThreadPool(50) as p:
        paths = list(p.map(get_music_path, spotify_data.items()))

    return paths


def download(paths, playlist, destination=f"{expanduser('~')}/Music/"):
    destination += playlist + "/"

    if not isdir(destination):
        mkdir(destination)
    
    with ThreadPool(10) as p:
        p.map(partial(download_music, playlist=playlist, destination=destination), paths)
    
    create_m3u(destination)


if __name__ == '__main__':
    user = "fhvspad0cvvk4f3a5x5n3ikfm"
    playlist = "14 min"
    paths = get_music_paths(user, playlist)
    download(paths, playlist)
