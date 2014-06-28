#!/usr/bin/env python

import os
from datetime import date

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
		courses = open(os.path.join("res", "courses")) # Read courses from file
		for line in courses :
			self.add_widget(AddRow(line.strip("\n"))) # Add widget for every course
		courses.close()


class ExportStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(ExportStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		indices = map(lambda s : s.replace("_", " "), os.listdir(os.path.join("res", "indices"))) # Get each indexed month
		for index in indices :
			self.add_widget(ExportRow(index)) # Add widget for every month


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course
	
	def applyCourse(self, children) :
		months = ("Januar", "Februar", "M\xC3rz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")
		
		for child in children : # Iterate over child widgets
			if "NewTextInput" in str(child) :
				new_date = child.text # Get the text of the TextInput widget
		for limiter in (" ", ".", "/", "-") :
			if limiter in new_date :
				new_date = new_date.split(limiter) # Split the date string by one of the valid delimiters
		
		try :
			date(*map(lambda i : int(i), new_date[::-1])) # Check if date is valid
		except Exception :
			print("Invalid date or date format") # Throw Error ==> TO-DO: Android popup!
		else :
			index = months[int(new_date[1])-1] + "_" + new_date[2] # Create an index name
			indices = open(os.path.join("res", "indices", index), "a") # Open index if existing, create new if not
			indices.write("{1}.{2}.{3} {0}\n".format(self.course, *new_date)) # Append date + course to index
			indices.close()
	
	def delCourse(self) :
		new_courses = open(os.path.join("res", "courses")).readlines()
		new_courses.remove(self.course + "\n") # Delete course from lines of file
		courses = open(os.path.join("res", "courses"), "w")
		courses.writelines(new_courses) # Write back the new lines
		courses.close()
		self.parent.update() # Update AddStack widget


class ExportRow(FloatLayout) :

	month = StringProperty("")
	
	def __init__(self, month, *args, **kwargs) :
		super(ExportRow, self).__init__(*args, **kwargs)
		self.month = month


### Screen Manager ###


class ScreenNexus(ScreenManager) :

	def __init__(self, *args, **kwargs) :
		super(ScreenNexus, self).__init__(*args, **kwargs)
		texture = Image(os.path.join("res", "tile.png")).texture # Create background texture
		texture.wrap = "repeat"
		texture.uvsize = (12, 24)
		
		with self.canvas.before : # Draw background
			Color(1, 1, 1)
			Rectangle(texture = texture, size = (Window.width, Window.height), pos = self.pos)


### Screens ###


class MainScreen(Screen) :
	
	date = StringProperty("")
	
	def __init__(self, *args, **kwargs) :
		super(MainScreen, self).__init__(*args, **kwargs)
		today = date.today() # Get date of today
		self.date = str(today.day).zfill(2) + "." + str(today.month).zfill(2) + "." + str(today.year).zfill(2)


class AddScreen(Screen) :
	
	def newCourse(self, name, children) :
		courses = open(os.path.join("res", "courses"), "a")
		courses.write(name + "\n") # Append name of new course to courses
		courses.close()
		
		for child in children : # Iterate over child widgets
			if isinstance(child, ScrollView) :
				stack = child.children[0]
				stack.update() # Update AddStack widget
			elif "NewTextInput" in str(child) :
				child.text = "" # Remove text of TextInput widget


class ExportScreen(Screen) :
	
	def createAccounting(self) :
		pass # TO-DO: Create export algorithm


### App ###


class AccountApp(App) :
	
	def build(self) :
		return ScreenNexus().add_widget(MainScreen())
		
	def getWidget(self) :
		pass # TO-DO: Create function to get widgets
		

if __name__ == "__main__" :
	app = AccountApp()
	app.run()


