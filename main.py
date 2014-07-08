#!/usr/bin/env python

import os
from datetime import date, datetime
import export2pdf

from kivy.app import App
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.spinner import Spinner
from kivy.uix.stacklayout import StackLayout
from kivy.uix.switch import Switch
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
		indices = os.listdir(os.path.join("res", "indices")) # Get each indexed month
		
		for index in indices :
			self.add_widget(ExportRow(index)) # Add widget for every month


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course
	
	def applyCourse(self) :
		months = ("Januar", "Februar", "Marz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")
		new_date = app.getWidgetsFromPath("main", FloatLayout, TextInput)[0].text
		new_times = [widget.text for widget in app.getWidgetsFromPath("main", FloatLayout, Spinner)][::-1]
		
		for limiter in (" ", ".", "/", "-") :
			if limiter in new_date :
				new_date = map(lambda d : d.zfill(2), new_date.split(limiter)) # Split the date string by one of the valid delimiters
		
		try :
			date(*map(lambda i : int(i), new_date[::-1])) # Check if date is valid
		except Exception :
			error = "Invalid date or date format."
		else :
			index_name = months[int(new_date[1])-1] + " " + new_date[2] # Create an index name
			index = open(os.path.join("res", "indices", index_name), "a") # Open index if existing, create new if not
			index.write("{1}.{2}.{3}_{4}-{5}_{0}\n".format(self.course, *new_date+new_times)) # Append date + time + course to index
			index.close()
			app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()
			error = "Course saved."
		finally :
			app.alert(error) # Throw Error ==> TO-DO: Android popup!
	
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


class Alert(Popup) :

	info = StringProperty("")


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
		name = app.getWidgetsFromPath("init", FloatLayout, TextInput)[0].text
		if name != "" :
			namefile = open(os.path.join("res", "username"), "w")
			namefile.write(name)
			app.alert("Welcome " + name + ".")
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
		name = open(os.path.join("res", "username")).readlines()[0]
		rows = app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack, ExportRow)
		
		selected = [row.children[1].text for row in rows if row.children[0].active]
		indices = map(lambda index : open(os.path.join("res", "indices", index)), selected)
		
		error = export2pdf.process(name, indices)
		if error :
			app.alert(error)
		else :
			app.alert("Successfully exported accounting.")
			for index_name in selected :
				os.remove(os.path.join("res", "indices", index_name))
		app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()
		


### App ###


class BrennerApp(App) :

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
	
	def alert(self, text) :
		popup = Alert(title = "Info", info = text)
		popup.open()
		
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
		return widgets


if __name__ == "__main__" :
	app = BrennerApp()
	app.run()


