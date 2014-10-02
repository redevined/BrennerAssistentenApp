#!/usr/bin/env python

import os, htmlport, json
from datetime import datetime, date, time
from interface import Android

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
		for line in app.store["courses"] :
			self.add_widget(AddRow(line.strip("\n")))


class ExportStack(StackLayout) :
	
	def __init__(self, *args, **kwargs) :
		super(ExportStack, self).__init__(*args, **kwargs)
		self.update()
		
	def update(self) :
		self.clear_widgets()
		for index in app.store["indices"].keys() :
			self.add_widget(ExportRow(index))


class AddRow(FloatLayout) :
	
	course = StringProperty("")
	
	def __init__(self, course, *args, **kwargs) :
		super(AddRow, self).__init__(*args, **kwargs)
		self.course = course
	
	def applyCourse(self) :
		main_screen = app.root.get_screen("main")
		new_date = main_screen._date
		new_time = main_screen._time
		
		ind = app.store["indices"]
		indname = ("Januar", "Februar", "Marz", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober", "November", "Dezember")[new_date.month-1] + " " + str(new_date.year)
		info = (main_screen.getDate(), main_screen.getTime(), self.course)
		
		if ind.has_key(indname) :
			ind[indname].append(info)
		else :
			ind[indname] = [info]
		
		app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()
		droid.info("Course saved.")
	
	def delCourse(self) :
		app.store["courses"].remove(self.course)
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
		app.store["user"] = name
		droid.info("Welcome " + name + ".")


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
		return " - ".join(str(t).rsplit(":", 1)[0] for t in self._time)
	
	def setDate(self) :
		self._date = droid.getDateDialogResponse(self._date.year, self._date.month, self._date.day)
	
	def setTime(self) :
		self._time = [droid.getTimeDialogResponse(t.hour, t.minute) for t in self._time]


class AddScreen(Screen) :
	
	def newCourse(self) :
		name = app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text
		app.store["courses"].append(name)
		
		app.getWidgetsFromPath("add", FloatLayout, ScrollView, AddStack)[0].update()
		app.getWidgetsFromPath("add", FloatLayout, TextInput)[0].text = ""


class ExportScreen(Screen) :
	
	def createAccounting(self) :
		rows = app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack, ExportRow)
		selected = [row.children[1].text for row in rows if row.children[0].active]
		ind = { key: value for (key, value) in app.store["indices"].items() if key in selected }
		
		# path = "/storage/sdcard0/BrennerAbrechnungen"
		path = "/tmp"
		error = htmlport.export(app.store["user"], path, ind)
		
		if error :
			droid.info(error)
		else :
			app.store["indices"] = { key: value for (key, value) in app.store["indices"].items() if key not in selected }
			droid.info("Successfully exported accounting.")
		
		app.getWidgetsFromPath("export", FloatLayout, ScrollView, ExportStack)[0].update()


### App ###


class Store() :
	
	def __init__(self, name) :
		self.name = name
		if os.path.exists(name) :
			self.data = self.load()
		else :
			self.data = { "courses": [], "indices": {} }
	
	def __del__(self) :
		self.save()
	
	def __getitem__(self, attr) :
		return self.data[attr]
	
	def __setitem__(self, attr, val) :
		self.data[attr] = val
	
	def load(self) :
		return json.load(open(self.name))
	
	def save(self) :
		json.dump(self.data, open(self.name, "w"))


class BrennerApp(App) :

	def build(self) :
		Builder.load_file("style.kv")
		self.store = Store("config.json")
		
		root = ScreenNexus()
		screens = [ MainScreen(), AddScreen(), ExportScreen() ]
		if not self.store.data.has_key("user") :
			screens.insert(0, InitScreen())
		
		for screen in screens :
			root.add_widget(screen)
		return root
	
	def on_stop(self) :
		del(self.store)
		
	def getWidgetsFromPath(self, screen, *path) :
		widgets = [self.root.get_screen(screen)]
		for wclass in path :
			widgets = [child for child in widgets[0].children if isinstance(child, wclass)]
		return widgets


if __name__ == "__main__" :
	droid = Android()
	app = BrennerApp()
	app.run()


