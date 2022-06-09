# music_downloader
An app to download playlists from Spotify via Youtube.

# Dependencies

## Python
You need Python installed to execute the program. 
You also need the dependencies from the file requirements.txt, 
you can install it executing `pip3 install -r requirements.txt`.

## Another dependencies
For execute the program properly you need to have an account on [Spotify for developers](https://developer.spotify.com/)
and to change the parameters in credentials.json file after create the account.  
If you want, you can put your Youtube account cookies in a file called **cookies.txt** inside music_downloader dir.
The problem of don't have it, it's if there is some restriction,
like age restriction for example, the music will not be downloaded.
You can get the your cookies account using an extension of your preferred browser.


# How to execute
To execute just type `python3 interface.py` or `./interface.py`.
When executing change the **username** by the username (not e-mail) of the playlist owner,
and change **playlist** by the playlist name.
