#!/usr/bin/env python3

from functools import partial
import http
import json
from multiprocessing import Pool
from os.path import isdir, isfile, expanduser
from os import listdir, mkdir, remove
import re
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


def get_music_path(music_data):
    yt_search_url="https://www.youtube.com/results?"
    i = music_data[0]
    music = music_data[1][0]
    artists = music_data[1][1]
    
    search_term = music + " " + " ".join(artists)
    params = {"search_query": search_term}
    result = r.get(yt_search_url, params)
    
    #* regex to match /watch?v= and any 11 caracters after that
    path = re.search("/watch\?v=.{11}", result.text).group()
    return path


def download_music(path, playlist, destination=f"{expanduser('~')}/Music/", count=0):
    yt_url="https://www.youtube.com"
    
    ydl_opts = {
        'cookiefile': COOKIES,
        'format': 'm4a/bestaudio/best',
        'outtmpl': f'{destination}%(title)s.%(ext)s',
        'download_archive': f'{destination}downloaded_songs_{playlist}.txt',
        'cachedir': False,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([yt_url + path])
    except http.cookiejar.LoadError:
        if isfile(COOKIES):
            remove(COOKIES)
    except yt_dlp.utils.DownloadError:
        pass
    else:
        return
    
    if count >= 3:
        return
    download_music(path, playlist, destination, count+1)


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

    with Pool(50) as p:
        paths = list(p.map(get_music_path, spotify_data.items()))

    return paths


def download(paths, playlist, destination=f"{expanduser('~')}/Music/"):
    destination += playlist + "/"

    if not isdir(destination):
        mkdir(destination)
    
    with Pool(10) as p:
        p.map(partial(download_music, playlist=playlist, destination=destination), paths)
    
    create_m3u(destination)


if __name__ == '__main__':
    user = "fhvspad0cvvk4f3a5x5n3ikfm"
    playlist = "14 min"
    paths = get_music_paths(user, playlist)
    download(paths, playlist)
