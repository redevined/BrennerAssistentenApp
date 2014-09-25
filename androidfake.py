#!/usr/bin/env python

class Android :
	
	def __init__(self) :
		print "Initializing fake 'Android' instance..."
	
	def makeToast(self, msg) :
		print "Show notification: {}".format(msg)
	
	def dialogCreateDatePicker(self, y, m, d) :
		print "Creating DatePicker"
		self.dialog = { "year": y, "month": m, "day": d }
	
	def dialogCreateTimePicker(self, h, m, some_stupid_boolean) :
		print "Creating TimePicker"
		self.dialog = { "hour": h, "minute": m }
	
	def dialogShow(self) :
		print "Show dialog: {}".format(self.dialog)
	
	def dialogGetResponse(self) :
		return type("Response", (), { "result": self.dialog })()
	
	def dialogDismiss(self) :
		print "Destroying dialog"
