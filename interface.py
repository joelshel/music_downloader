#!/usr/bin/env python3

from functools import partial
from multiprocessing.pool import ThreadPool
from os.path import expanduser
from queue import Queue
import threading
from time import sleep

from os import environ
# environ["KIVY_NO_CONSOLELOG"] = "1"

from kivy.app import App
from kivy.clock import Clock
from kivy.config import Config
from kivy.properties import StringProperty, NumericProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
import download as dl


class Ticket():
    def __init__(self, type:str, value=None):
        self.type = type
        self.value = value


class Error(Popup):
    text = StringProperty("")

    def __init__(self, text, **kwargs):
        super().__init__(**kwargs)
        self.text = text


class MainLayout(BoxLayout):
    max = NumericProperty(0)
    value = NumericProperty(0)
    text = StringProperty("0/0")

    def thread_download(self, username, playlist):
        if threading.active_count() < 2:
            self.queue = Queue()

            threading.Thread(target=self.download,
                args=(username, playlist),
                daemon=True
                ).start()

    def download(self, username, playlist):
        destination = f"{expanduser('~')}/Music/{playlist}/"
        
        self.queue.put(Ticket("Update max", 0))
        Clock.schedule_once(lambda dt: self.check_queue(), -1)

        self.queue.put(Ticket("Update value", 0))
        Clock.schedule_once(lambda dt: self.check_queue(), -1)
        sleep(.5)
        text_queue = Queue()
        update = threading.Thread(
            target=self.auto_update_text,
            args=(text_queue,),
            daemon=True
        )
        update.start()

        paths = dl.get_music_paths(username, playlist)
        getting_playlist_queue.put("All playlist data got")
        update.join()
        del getting_playlist_queue

        if type(paths) is list:
            if None in paths:
                paths = [path for path in paths if path != None]
                error = "Some music URLs weren't found\n" + \
                        "This can be due a poor wifi connection"
                
                Clock.schedule_once(lambda dt: self.throw_popup(error), -1)
        
        if type(paths) == str:
            Clock.schedule_once(lambda dt: self.throw_popup(paths), -1)
            self.queue.put(Ticket("Update text", "0/0"))
            Clock.schedule_once(lambda dt: self.check_queue(), -1)
        else:
            self.queue.put(Ticket("Update max", len(paths)))
            Clock.schedule_once(lambda dt: self.check_queue(), -1)
            
            value = 0
            self.queue.put(Ticket("Update value", value))
            Clock.schedule_once(lambda dt: self.check_queue(), -1)

            #? using ThreadPool instead of Pool so it's possible to kill the
            #? app during execution. Sometimes the message "Segmentation fault
            #? (core dumped)" due trying to write musics without permission
            with ThreadPool(10) as p:
                for downloaded_music in p.imap(
                    partial(
                        dl.download_music,
                        playlist=playlist,
                        destination=destination),
                    paths):
                    value += 1
                    self.queue.put(Ticket("Update value", value))
                    Clock.schedule_once(lambda dt: self.check_queue(), -1)
            
            dl.create_m3u(destination)
    
    def throw_popup(self, error):
            popup = Error(text=error)
            popup.open()
    
    def on_value(self, instance, value):
        self.text = f"{self.value}/{self.max}"
    
    def check_queue(self):
        ticket: Ticket = self.queue.get()

        if ticket.type == "Update text":
            self.text = ticket.value
        if ticket.type == "Update value":
            self.value = ticket.value
        if ticket.type == "Update max":
            self.max  = ticket.value

    def auto_update_text(self, text_queue):
        while True:
            max_dots = 3
            for n_dots in range(1, max_dots+1):
                self.queue.put(
                    Ticket(
                        "Update text",
                        f"Getting playlist info{'.'*n_dots}{' '*(max_dots-n_dots)}"
                    )
                )
                Clock.schedule_once(lambda dt: self.check_queue(), -1)
                sleep(.5)
            
            if not text_queue.empty():
                break


class MusicDownloaderApp(App):
    pass


if __name__ == '__main__':
    Config.set('graphics', 'width', '500')
    Config.set('graphics', 'height', '190')
    Config.set('graphics', 'resizable', False)
    MusicDownloaderApp().run()
