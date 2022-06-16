pyinstaller interface.py -Fw --clean \
    --add-data "musicdownloader.kv:." \
    --paths "music_downloader/lib/python3.8/site-packages/" \
    --exclude-module pyinstaller \
    --exclude-module pyinstaller-hooks-contrib \
    --exclude-module Pygments \
    --exclude-module docutils \



cp credentials.json dist/
