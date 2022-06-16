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

# How to compile
To compile first create a virtual environment, activate it, install the dependencies inside it,
and compile using pyinstaller.
When you're done you can deactivate venv.

```
$ python3 -m venv music_downloader
$ source music_downloader/bin/activate
$ pip3 install -r requirements.txt
$ bash compiler.sh
$ deactivate
```

The compiled file'll be in the dist directory (created automatically by pyinstaller).

# How to execute
To execute just type `python3 interface.py` or `./interface.py`.
When the app is compiled you can also do the same with the compiled app
or simple open it with the files explorer.
When executing change the **username** by the username (not e-mail) of the playlist owner,
and change **playlist** by the playlist name.
