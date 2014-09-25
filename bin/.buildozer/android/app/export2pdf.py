#!/usr/bin/env python

import os
from datetime import date


class SourceBuilder() :

	def __init__(self, name, index) :
		self.name = name
		path = index.name.split("/")
		self.month = path[len(path)-1]
		self.rows = index.readlines()
		self.code = []
	
	def build(self, day, head, body, foot, close) :
		heading = "<h2>Abrechnung {}</h2>".format(self.month)
		footer = "<p>{} | {}</p>".format(self.name, day)
		trs = []
		
		i = 0
		for row in self.rows :
			info = row.split("_")
			trs.append("<tr class='highlight_{}'><td class='small'><p>{}</p></td><td class='small'><p>{}</p></td><td class='large'><p>{}</p></td></tr>".format(i, *info))
			i = int(not i)
		
		head.append(heading)
		body.extend(trs)
		foot.append(footer)
		self.code = head + body + foot + close
	
	def export(self, path) :
		try :
			accounting = open(os.path.join(path, "Abrechnung " + self.month + ".html"), "w")
		except Exception :
			return "Failed to create the html file."
		else :
			for line in self.code :
				accounting.write(line + "\n")
			accounting.close()


def process(name, indices) :
	
	source = []
	html = map(lambda line : line.strip("\t\r\n"), open(os.path.join("res", "template.html")).readlines())
	markers = [html.index("<!--HEADING-->"), html.index("<!--ROWS-->"), html.index("<!--FOOTER-->")]
	parts = html[:markers[0]], html[markers[0]+1:markers[1]], html[markers[1]+1:markers[2]], html[markers[2]+1:]
	
	androidpath = "/storage/sdcard0/BrennerAbrechnungen"
	if not os.path.exists(androidpath) :
		try :
			os.makedirs(androidpath)
		except Exception :
			return "Creating a directory on internal SD card failed."
	
	for index in indices :
		source.append(SourceBuilder(name, index))
	
	for builder in source :
		now = date.today()
		date_string = str(now.day).zfill(2) + "." + str(now.month).zfill(2) + "." + str(now.year).zfill(4)
		builder.build(date_string, *parts)
	
	for builder in source :
		error = builder.export(androidpath)
		if error :
			return error


