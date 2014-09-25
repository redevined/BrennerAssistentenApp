#!/usr/bin/env python

import os, datetime


class SourceBuilder() :

	def __init__(self, name, date, index) :
		self.name = name
		self.date = ".".join(str(date).split("-")[::-1])
		path = index.name.split("/")
		self.month = path[len(path)-1]
		self.rows = index.readlines()
		self.code = []
	
	def build(self, head, body, foot, close) :
		heading = "<h2>Abrechnung {}</h2>".format(self.month)
		footer = "<p>{} | {}</p>".format(self.name, self.date)
		trs = []
		
		i = 0
		for row in self.rows :
			info = row.split("_")
			trs.append("""
				<tr class='highlight_{}'>
					<td class='small'>
						<p>{}</p>
					</td>
					<td class='small'>
						<p>{}</p>
					</td>
					<td class='large'>
						<p>{}</p>
					</td>
				</tr>
			""".format(i, *info))
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


def export(name, path, indices) :
	
	source = []
	html = [line.strip("\t\r\n") for line in open(os.path.join("res", "template.html"))]
	sh, sr, sf = html.index("<!--HEADING-->"), html.index("<!--ROWS-->"), html.index("<!--FOOTER-->")
	html_split = html[:sh], html[sh+1:sr], html[sr+1:sf], html[sf+1:]
	
	if not os.path.exists(path) :
		try :
			os.makedirs(path)
		except Exception :
			return "Creating a directory on internal SD card failed."
	
	for index in indices :
		source.append(SourceBuilder(name, datetime.date.today(), index))
	
	for builder in source :
		builder.build(*html_split)
	
	for builder in source :
		error = builder.export(path)
		if error :
			return error


