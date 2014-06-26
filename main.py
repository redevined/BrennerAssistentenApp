#!/usr/bin/env python

import sys, os
from kivy.app import App

from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.stacklayout import StackLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.textinput import TextInput
from kivy.properties import StringProperty


### Classes ###


class AddStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(AddStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		template = open(os.path.join("res/template.txt"))
		for line in template :
			if line[0] == "." : # Save Courses with a leading "."
				self.add_widget(AddRow(line[1:]))
		template.close()


class ExportStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(ExportStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		template = open(os.path.join("res/template.txt"))
		for line in template :
			if line[0] == "*" : # Save months with a leading "*"
				self.add_widget(ExportRow(line[1:]))
		template.close()


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course.strip("\n")
	
	def applyCourse(self) :
		pass
	
	def delCourse(self) :
		template = open(os.path.join("res/template.txt"), "r+")
		template_lines = template.readlines().remove("." + self.course + "\n")
		template.writelines(template_lines)


class ExportRow(FloatLayout) :

	month = StringProperty("")
	
	def __init__(self, month, *args, **kwargs) :
		super(ExportRow, self).__init__(*args, **kwargs)
		self.month = month.strip("\n")


### Screen Manager ###


class ScreenNexus(ScreenManager) :

	def __init__(self, *args, **kwargs) :
		super(ScreenNexus, self).__init__(*args, **kwargs)
		texture = Image("res/tile.png").texture
		texture.wrap = "repeat"
		texture.uvsize = (12, 24)
		
		with self.canvas.before :
			Color(1, 1, 1)
			Rectangle(texture = texture, size = (Window.width, Window.height), pos = self.pos)


### Screens ###


class MainScreen(Screen) :
	
	pass


class AddScreen(Screen) :
	
	def newCourse(self, name) :
		template = open(os.path.join("res/template.txt"), "a")
		template.write("." + name + "\n")
		template.close()
		
		for child in self.children[0].children :
			if type(child) == ScrollView :
				stack = child.children[0]
				stack.update()
			elif "NewTextInput" in str(child) :
				child.text = ""


class ExportScreen(Screen) :
	
	def createAccounting(self) :
		pass


### App ###


class AccountApp(App) :
	
	def build(self) :
		return ScreenNexus().add_widget(MainScreen())
		

if __name__ == "__main__" :
	AccountApp().run()


