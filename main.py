#!/usr/bin/env python

import os, htmlport
from datetime import datetime, date, time
from androidhelper import Android
# from androidfake import Android

from kivy.app import App
from kivy.lang import Builder
from kivy.core.image import Image
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.uix.textinput import TextInput


### Classes ###


class AddStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(AddStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		courses = open(os.path.join("res", "courses.txt"))
		for line in courses :
			self.add_widget(AddRow(line.strip("\n")))
		courses.close()


class ExportStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(ExportStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		indices = [index for index in os.listdir(os.path.join("res", "indices")) if index[0] != "."] 
		
		for index in indices :
			self.add_widget(ExportRow(index))


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course
	
	def applyCourse(self) :
		months = ("Januar", "Februar", "Marz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")
		
		main_screen = app.root.get_screen("main")
		new_date = main_screen._date
		new_time = main_screen._time
		
		index_name = months[new_date.month-1] + " " + str(new_date.year)
		index = open(os.path.join("res", "indices", index_name), "a")
		index.write("{}_{}_{}\n".format(main_screen.getDate(), main_screen.getTime(), self.course))
		index.close()
		
		app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()
		droid.makeToast("Course saved.")
	
	def delCourse(self) :
		new_courses = open(os.path.join("res", "courses.txt")).readlines()
		new_courses.remove(self.course + "\n")
		courses = open(os.path.join("res", "courses.txt"), "w")
		courses.writelines(new_courses)
		courses.close()
		self.parent.update()


class ExportRow(FloatLayout) :

	month = StringProperty("")
	
	def __init__(self, month, *args, **kwargs) :
		super(ExportRow, self).__init__(*args, **kwargs)
		self.month = month


### Screen Manager ###


class ScreenNexus(ScreenManager) :

	def __init__(self, *args, **kwargs) :
		super(ScreenNexus, self).__init__(*args, **kwargs)
		texture = Image(os.path.join("res", "tile.png")).texture
		texture.wrap = "repeat"
		texture.uvsize = (12, 24)
		
		with self.canvas.before :
			Color(1, 1, 1)
			Rectangle(texture = texture, size = (Window.width, Window.height), pos = self.pos)


### Screens ###


class InitScreen(Screen) :

	def createName(self) :
		name = app.getWidgetsFromPath("init", FloatLayout, TextInput)[0].text
		if name != "" :
			namefile = open(os.path.join("res", "username"), "w")
			namefile.write(name)
			droid.makeToast("Welcome " + name + ".")
			namefile.close()


class MainScreen(Screen) :
	
	_date = ObjectProperty(None)
	_time = ObjectProperty(None)
	
	def __init__(self, *args, **kwargs) :
		now = datetime.today()
		self._date = now.date()
		self._time = [time(now.hour, (now.minute//15+1)%4*15), time((now.hour + 1)%24, (now.minute//15+1)%4*15)]
		super(MainScreen, self).__init__(*args, **kwargs)
	
	def getDate(self) :
		return ".".join(str(self._date).split("-")[::-1])
	
	def getTime(self) :
		print self._time
		return " - ".join(str(t).rsplit(":", 1)[0] for t in self._time)
	
	def setDate(self) :
		droid.dialogCreateDatePicker(self._date.year, self._date.month, self._date.day)
		droid.dialogShow()
		res = droid.dialogGetResponse().result
		droid.dialogDismiss()
		
		self._date = date(res["year"], res["month"], res["day"])
	
	def setTime(self) :
		def getResponse(t) :
			droid.dialogCreateTimePicker(t.hour, t.minute, True)
			droid.dialogShow()
			res = droid.dialogGetResponse().result
			droid.dialogDismiss()
			
			return time(res["hour"], res["minute"])
		
		self._time = [getResponse(t) for t in self._time]


class AddScreen(Screen) :
	
	def newCourse(self) :
		courses = open(os.path.join("res", "courses.txt"), "a")
		name = app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text
		courses.write(name + "\n")
		courses.close()
		
		app.getWidgetsFromPath("add", FloatLayout, ScrollView, AddStack)[0].update()
		app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text = ""


class ExportScreen(Screen) :
	
	def createAccounting(self) :
		name = open(os.path.join("res", "username")).readlines()[0]
		rows = app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack, ExportRow)
		
		selected = [row.children[1].text for row in rows if row.children[0].active]
		indices = [open(os.path.join("res", "indices", index)) for index in selected]
		
		path = "/storage/sdcard0/BrennerAbrechnungen"
		# path = "/tmp"
		error = htmlport.export(name, path, indices)
		
		if error :
			droid.makeToast(error)
		else :
			droid.makeToast("Successfully exported accounting.")
			for index_name in selected :
				os.remove(os.path.join("res", "indices", index_name))
		
		app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()


### App ###


class BrennerApp(App) :

	def build(self) :
		Builder.load_file("style.kv")
		
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


if __name__ == "__main__" :
	droid = Android()
	app = BrennerApp()
	app.run()


