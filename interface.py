#!/usr/bin/env python3

import threading
from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import download as dl


class Error(Popup):
    text = StringProperty("")

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class MainLayout(BoxLayout):
    def download(self, username, playlist):
        if threading.active_count() <= 2:
            error = dl.download(username, playlist)

            if type(error) == str:
                Clock.schedule_once(lambda dt: self.throw_popup(error), -1)

    def thread_download(self, username, playlist):
        threading.Thread(target=self.download,
            args=(username, playlist),
            # daemon=True
            ).start()
    
    def throw_popup(self, error):
            popup = Error(text=error)
            popup.open()


class MusicDownloaderApp(App):
    pass


if __name__ == '__main__':
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '170')
    Config.set('graphics', 'resizable', False)
    # Config.set('kivy', 'log_level', 'error')
    # Config.set('kivy', 'log_enable', 0)
    MusicDownloaderApp().run()
