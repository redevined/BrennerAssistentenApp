#!/usr/bin/env python

import os
from datetime import date, datetime

from kivy.app import App
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput


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
		months = ("Januar", "Februar", "Maerz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")
		indices = map(lambda s : s.split("_"), os.listdir(os.path.join("res", "indices"))) # Get each indexed month
		
		for index in indices :
			index[0] = months[int(index[0])-1]
			index_name = " ".join(index)
			self.add_widget(ExportRow(index_name)) # Add widget for every month


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course
	
	def applyCourse(self) :
		new_date = app.getWidgetsFromPath("main", FloatLayout, TextInput)[0].text
		new_times = [widget.text for widget in app.getWidgetsFromPath("main", FloatLayout, Spinner)][::-1]
		
		for limiter in (" ", ".", "/", "-") :
			if limiter in new_date :
				new_date = map(lambda d : d.zfill(2), new_date.split(limiter)) # Split the date string by one of the valid delimiters
		
		try :
			date(*map(lambda i : int(i), new_date[::-1])) # Check if date is valid
		except Exception :
			print("Invalid date or date format") # Throw Error ==> TO-DO: Android popup!
		else :
			index_name = new_date[1] + "_" + new_date[2] # Create an index name
			index = open(os.path.join("res", "indices", index_name), "a") # Open index if existing, create new if not
			index.write("{1}.{2}.{3}_{4}-{5}_{0}\n".format(self.course, *new_date+new_times)) # Append date + time + course to index
			index.close()
			app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()
	
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


class InitScreen(Screen) :

	def createName(self) :
		namefile = open(os.path.join("res", "username"), "w")
		name = app.getWidgetsFromPath("init", FloatLayout, TextInput)[0].text
		namefile.write(name)
		namefile.close()


class MainScreen(Screen) :
	
	date = StringProperty("")
	begin_time = StringProperty("")
	end_time = StringProperty("")
	
	def __init__(self, *args, **kwargs) :
		super(MainScreen, self).__init__(*args, **kwargs)
		now = datetime.today() # Get date of today
		self.date = str(now.day).zfill(2) + "." + str(now.month).zfill(2) + "." + str(now.year).zfill(4)
		self.begin_time = str(now.hour).zfill(2) + ":" + str((now.minute//15+1)%4*15).zfill(2)
		self.end_time = str(now.hour+1).zfill(2) + ":" + str((now.minute//15+1)%4*15).zfill(2)


class AddScreen(Screen) :
	
	def newCourse(self) :
		courses = open(os.path.join("res", "courses"), "a")
		name = app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text
		courses.write(name + "\n") # Append name of new course to courses
		courses.close()
		
		app.getWidgetsFromPath("add", FloatLayout, ScrollView, AddStack)[0].update()
		app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text = "" # Reset TextInput


class ExportScreen(Screen) :
	
	def createAccounting(self) :
		pass # TO-DO: Create export algorithm


### App ###


class AccountApp(App) :

	def build(self) :
		root = ScreenNexus()
		screens = [ MainScreen(), AddScreen(), ExportScreen() ]
		try :
			open(os.path.join("res", "username")).close()
		except Exception :
			screens.insert(0, InitScreen())
		
		for screen in screens :
			root.add_widget(screen)
		return root
		
	def getWidgetsFromPath(self, screen, *path) :
		widgets = [self.root.get_screen(screen)]
		for wclass in path :
			widgets = [child for child in widgets[0].children if isinstance(child, wclass)]
		return widgets
	
	def getAllWidgets(self) :
		widgets = []
		def getChildren(widget) :
			widgets.append(widget)
			try :
				for child in widget.children :
					getChildren(child)
			except Exception :
				pass
		
		for name in "main", "add", "export" :
			getChildren(self.root.get_screen(name))
		return map(lambda w : w.id, widgets)


if __name__ == "__main__" :
	app = AccountApp()
	app.run()


