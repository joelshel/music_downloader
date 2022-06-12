#!/usr/bin/env python3

import kivy
from kivy.app import App
from kivy.config import Config
from kivy.properties import StringProperty
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.popup import Popup
import download as dl

kivy.require("2.1.0")

class LabelInput(BoxLayout):
    label_text = StringProperty("default")
    input_text = StringProperty("")

    def alter_input_text(self):
        self.input_text = self.ids.text_input.text


class Interface(BoxLayout):
    pass


class PopupWidget(BoxLayout):
    
    def get_error_text(self):
        with open('error.txt', 'r') as f:
            return f.read()


class ErrorPopup(Popup):
    pass


class DownloadButton(Button):

    def throw_popup(self):
        popup = ErrorPopup()
        popup.open()


    def download(self, username, playlist):
        has_error = dl.download(username, playlist)
        if type(has_error) == str:
            self.throw_popup()


class MusicDownloaderApp(App):

    def build(self):
        Config.set('graphics', 'width', '500')
        Config.set('graphics', 'height', '150')
        Config.set('graphics', 'resizable', False)

        return Interface()


if __name__ == '__main__':
    MusicDownloaderApp().run()
