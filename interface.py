#!/usr/bin/env python

from datetime import date, time
from jnius import autoclass


class Android :

	def __init__(self) :
		self.CONTEXT = autoclass("android.content.Context")
		self.toast = autoclass("android.widget.Toast")
		self.dateDialog = autoclass("android.app.DatePickerDialog")
		self.timeDialog = autoclass("android.app.TimePickerDialog")
	
	def info(self, msg) :
		self.toast.makeText(self.CONTEXT, msg, self.toast.LENGTH_SHORT).show()
	
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
