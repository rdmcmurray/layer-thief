import math

class LTUi(object):

	def __init__(self):
		self.currentRow = 0
		self.maxCols = 0

		self.margins = [20, 8]
		self.heights = {
			"button" : [20, 17, 14],
			"textBox" : [17, 14, 12],
			"popUp" : [20, 17, 15],
			"editText" : [22, 19, 16],
			"checkBox" : [22, 18, 10],
			"colorPreviewImage" : [12],
		}
		self.heights["margin"] = self.margins
		self.heights["row"] = [
			self.h("margin") + self.h("margin", 1)
		]

	def h(self, obj, index=0):
		if obj in self.heights.keys():
			return self.heights.get(obj)[index]

	# returns an x coord based on col offset
	# you can offset from right with negative col arg BUT that relies on w() receiving largest value first, such as window width for maxCols
	def x(self, cols=0):
		x = self.margins[0] + cols * self.margins[0]

		if math.copysign(1.0, cols) == 1:
			margs = math.floor(cols)
		else:
			margs = math.ceil(cols) + 1
			x += self.w(self.maxCols)

		x += margs * self.margins[1]

		return x

	# acts as a register
	# returns incremented y coord by row
	def y(self, incrementRow=0):
		self.currentRow += incrementRow
		r = self.margins[0]
		r += (self.margins[0] + self.margins[1]) * self.currentRow

		return r

	# returns width based on cols spanned
	def w(self, cols=1):
		if cols > self.maxCols: 
			self.maxCols = cols

		if cols <= 1: # return col width w/o margin
			w = self.margins[0]
		else:
			w = cols * self.margins[0]
			margs = math.floor(cols) - 1
			w += margs * self.margins[1]

		return w
