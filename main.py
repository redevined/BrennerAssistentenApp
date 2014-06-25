#!/usr/bin/env python

from kivy.app import App

from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen


class ScreenNexus(ScreenManager) :

	def __init__(self, *args, **kwargs) :
		super(ScreenNexus, self).__init__(*args, **kwargs)
		texture = Image("tile.png").texture
		texture.wrap = "repeat"
		texture.uvsize = (12, 24)
		
		with self.canvas.before :
			Color(1, 1, 1)
			Rectangle(texture = texture, size = (Window.width, Window.height), pos = self.pos)


class MainScreen(Screen) :
	
	pass


class AddScreen(Screen) :
	
	pass


class ExportScreen(Screen) :
	
	pass


class AccountApp(App) :
	
	def build(self) :
		return ScreenNexus().add_widget(MainScreen())
		

if __name__ == "__main__" :
	AccountApp().run()
