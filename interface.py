#!/usr/bin/env python3

import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.properties import StringProperty
from kivy.config import Config

kivy.require("2.1.0")

class LabelInput(BoxLayout):
    label_text = StringProperty("default")
    input_text = StringProperty("")

    def alter_input_text(self):
        self.input_text = self.ids.text_input.text


class Interface(BoxLayout):
    pass


class MusicDownloaderApp(App):

    def build(self):
        Config.set('graphics', 'width', '500')
        Config.set('graphics', 'height', '150')
        Config.set('graphics', 'resizable', False)

        return Interface()


if __name__ == '__main__':
    MusicDownloaderApp().run()
