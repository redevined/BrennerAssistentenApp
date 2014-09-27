#!/usr/bin/env python

import os, datetime


template = """
<html>
	<head>
		<style type='text/css'>
			body { font-family: Sans-Serif; }
			div { position: absolute; margin-left: auto; margin-right: auto; left: 20px; right: 20px; }
			#content { top: 20px; }
			#footer { font-size: 12px; bottom: 20px; 	}
			.left { width: 50%; float: left; text-align: left; }
			.right { width: 50%; float: left; text-align: right; }
			table { width: 100%; line-height: 35px; border-collapse: collapse; text-align: left; }
			#header { border-bottom: 2px solid #444; }
			#header p { font-weight: bold; }
			.small { width: 25%; }
			.large { width: 50%; }
			.highlight_0 { background-color: #79b; }
			.highlight_1 { background-color: #dee; }
		</style>
	</head>
	<body>
		<div id='content'>
			<!--HEADING-->
			<table>
				<tr id='header'>
					<td class='small'>
						<p>Datum</p>
					</td>
					<td class='small'>
						<p>Uhrzeit</p>
					</td>
					<td class='large'>
						<p>Kurs</p>
					</td>
				</tr>
				<!--ROWS-->
			</table>
		</div>
		<div id='footer'>
			<hr />
			<span class='left'>
				<!--FOOTER-->
			</span>
			<span class='right'>
				<p>erstellt durch die BrennerAssistentenApp</p>
			</span>
		</div>
	</body>
</html>
"""


class SourceBuilder() :

	def __init__(self, name, date, index) :
		self.name = name
		self.date = ".".join(str(date).split("-")[::-1])
		self.month, self.infos = index
		
		self.build()
	
	def build(self) :
		heading = "<h2>Abrechnung {}</h2>".format(self.month)
		rows = ""
		footer = "<p>{} | {}</p>".format(self.name, self.date)
		i = 0
		for info in self.infos :
			rows += """
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
			""".format(i, *info)
			i = int(not i)
		
		self.code = template.replace("<!--HEADING-->", heading).replace("<!--ROWS-->", rows).replace("<!--FOOTER-->", footer)
	
	def write(self, path) :
		if not os.path.exists(path) :
			try :
				os.makedirs(path)
			except Exception :
				return "Creating a directory on internal SD card failed."
		
		try :
			accounting = open(os.path.join(path, "Abrechnung " + self.month + ".html"), "w")
		except Exception :
			return "Failed to create the html file."
		else :
			accounting.write(self.code)
			accounting.close()


def export(name, path, indices) :
	
	source = (SourceBuilder(name, datetime.date.today(), index) for index in indices.items())
	
	for builder in source :
		error = builder.write(path)
		if error :
			return error


