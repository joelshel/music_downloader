#!/usr/bin/env python3

from functools import partial
from multiprocessing import Pool
from os.path import expanduser
import threading

from os import environ
environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.config import Config
from kivy.app import App
from kivy.clock import Clock
from kivy.logger import Logger, LOG_LEVELS
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import download as dl


#! Func/method outside of class cause kivy doesn't support pickling objects,
#! therefore you can't use Pool.map() within a method of a kivy class

def download(path, playlist, destination):
    dl.download_music(path, playlist, destination)
    return 1


class Error(Popup):
    text = StringProperty("")

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class MainLayout(BoxLayout):
    max = NumericProperty(0)
    value = NumericProperty(-1)
    text = StringProperty("0/0")

    def thread_download(self, username, playlist, destination=f"{expanduser('~')}/Music/"):
        if threading.active_count() < 2:
            threading.Thread(target=self.download,
                args=(username, playlist, destination),
                # daemon=True
                ).start()

    def download(self, username, playlist, destination=f"{expanduser('~')}/Music/"):
        self.text = "Getting playlist info..."
        paths = dl.get_music_paths(username, playlist)

        if None in paths:
            paths = [path for path in paths if path != None]
            error = "Some music URLs weren't found\n" + \
                    "This can be due a poor wifi connection"
            
            Clock.schedule_once(lambda dt: self.throw_popup(error), -1)
        
        if type(paths) == str:
            Clock.schedule_once(lambda dt: self.throw_popup(paths), -1)
        else:
            destination += playlist + "/"
            self.max = len(paths)
            self.value = 0

            with Pool(10) as p:
                for downloaded_music in p.imap(
                    partial(
                        download,
                        playlist=playlist,
                        destination=destination),
                    paths):
                    self.value += downloaded_music
            
            dl.create_m3u(destination)
    
    def throw_popup(self, error):
            popup = Error(text=error)
            popup.open()
    
    def on_value(self, instance, value):
        self.text = f"{self.value}/{self.max}"


class MusicDownloaderApp(App):
    pass


if __name__ == '__main__':
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '190')
    Config.set('graphics', 'resizable', False)
    MusicDownloaderApp().run()
