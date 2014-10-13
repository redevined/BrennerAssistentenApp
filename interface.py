#!/usr/bin/env python

from datetime import date, time
from jnius import autoclass, cast
from android import activity
from android.runnable import run_on_ui_thread


class Android :

	def __init__(self) :
		self.CONTEXT = autoclass("org.renpy.android.PythonActivity").mActivity
		self.toast = autoclass("android.widget.Toast")
		self.dateDialog = autoclass("android.app.DatePickerDialog")
		self.timeDialog = autoclass("android.app.TimePickerDialog")
	
	@run_on_ui_thread
	def info(self, msg) :
		s = autoclass("java.lang.String")
		self.toast.makeText(self.CONTEXT, cast("java.lang.CharSequence", s(msg)), self.toast.LENGTH_SHORT).show()
	
	def getDateDialogResponse(self, y, m, d) :
		callback = self.dateDialog.OnDateSetListener()
		dialog = self.dateDialog(self.CONTEXT, callback, y, m, d)
		dialog.show()
		return date(callback.year, callback.monthOfYear, callback.dayOfMonth)
	
	def getTimeDialogResponse(self, h, m) :
		callback = self.timeDialog.OnTimeSetListener()
		dialog = self.timeDialog(self.CONTEXT, callback, h, m, True)
		dialog.show()
		return time(callback.hourOfDay, callback.minute)
