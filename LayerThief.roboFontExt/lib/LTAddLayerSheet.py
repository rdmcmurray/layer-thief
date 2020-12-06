import AppKit
import vanilla
import re
import LTSegmentedColorButton
import LTUi

class LTAddLayerSheet(object):

	ui = LTUi.LTUi()
	parent = None

	# strings
	cancelAddLayerButton = "Cancel"
	addLayerButton = "Add Layer"
	layerNameTitle = "Name:"
	layerColorTitle = "Color:"
	cancelButtonKey = "\x1b"
	addLayerButtonKey = "\r"

	# color button segments
	segments = [
		{"title": "Pink", "NSColor": AppKit.NSColor.systemPinkColor()},
		{"title": "Red", "NSColor": AppKit.NSColor.systemRedColor()},
		{"title": "Orange", "NSColor": AppKit.NSColor.systemOrangeColor()},
		{"title": "Yellow", "NSColor": AppKit.NSColor.systemYellowColor()},
		{"title": "Green", "NSColor": AppKit.NSColor.systemGreenColor()},
		{"title": "Teal", "NSColor": AppKit.NSColor.systemTealColor()},
		{"title": "Blue", "NSColor": AppKit.NSColor.systemBlueColor()},
		{"title": "Indigo", "NSColor": AppKit.NSColor.systemIndigoColor()},
		{"title": "Purple", "NSColor": AppKit.NSColor.systemPurpleColor()},
		# {"title": "Brown", "NSColor": AppKit.NSColor.systemBrownColor()},
		# {"title": "Gray", "NSColor": AppKit.NSColor.systemGrayColor()},
	]

	def __init__(self, parent):
		self.parent = parent
		self.sheetWidth = self.ui.w() + self.ui.w(9.6) + self.ui.w()
		self.ui.currentRow = 0
		# sheet
		self.addLayerSheet = vanilla.Sheet((0, 0), self.parent.w)
		# color
		self.addLayerSheet.addLayerColorLabel = vanilla.TextBox((self.ui.x(), self.ui.y(), self.ui.w(2), self.ui.h("textBox")), self.layerColorTitle, alignment="right")
		self.addLayerSheet.colorButton = LTSegmentedColorButton.LTSegmentedColorButton((self.ui.x(2), self.ui.y(), 0, 22), self._suggestSegmentOrder())
		# name
		self.addLayerSheet.layerNameLabel = vanilla.TextBox((self.ui.x(), self.ui.y(1) + 3, self.ui.w(2), self.ui.h("textBox")), self.layerNameTitle, alignment="right")
		self.addLayerSheet.layerName = vanilla.EditText((self.ui.x(2), self.ui.y(), self.ui.w(7.6), self.ui.h("editText")), "", callback=self.layerNameEditCallback)
		self.addLayerSheet.layerName.getNSTextField().cell().setWraps_(False)
		self.addLayerSheet.layerName.getNSTextField().cell().setScrollable_(True)
		self.addLayerSheet.errorLabel = vanilla.TextBox((self.ui.x(2), self.ui.y(1), self.ui.w(7.6), self.ui.h("textBox", 1)), "Layer name already taken", sizeStyle="small")
		# buttons
		self.addLayerSheet.cancelButton = vanilla.Button((self.ui.x(-7.6), self.ui.y(1), self.ui.w(3.6), self.ui.h("button")), self.cancelAddLayerButton, callback=self.closeAddLayerSheetCallback)
		self.addLayerSheet.addLayerButton = vanilla.Button((self.ui.x(-4), self.ui.y(), self.ui.w(4), self.ui.h("button")), self.addLayerButton, callback=self.addLayerButtonCallback)
		self.addLayerSheet.cancelButton.getNSButton().setKeyEquivalent_(self.cancelButtonKey)
		self.addLayerSheet.addLayerButton.getNSButton().setKeyEquivalent_(self.addLayerButtonKey)
		# setup
		self.addLayerSheet.layerName.set(self._suggestLayerName())
		self.addLayerSheet.errorLabel.show(0)
		self.addLayerSheet.resize(self.sheetWidth, self.ui.y(1.4))
		self.addLayerSheet.open()

	def _suggestLayerName(self):
		# suggestion is based on source font + layer, but killed on repeat
		p = self.parent

		suggestion = p.openFontDisplayNames[p.selectedSourceFont]
		suggestion += " "
		suggestion += self.parent.sourceLayerDisplayNames[p.selectedSourceLayer]

		# already exists, no suggestion
		if suggestion in self.parent.targetLayerDisplayNames: 
			suggestion = ""

		return suggestion

	def _suggestSegmentOrder(self):
		t = self.parent.targetLayerColorHues
		h = []

		for i, hue in enumerate(self.parent.hues):
			c = hue.get("title")
			if c not in t:
				h.append(c)
		# first unused color
		if len(h) > 0: 
			c = h[0]
		# none unused, pick up from the last used color and get the next in sequence
		else:
			for i, segment in enumerate(self.segments):
				if segment.get("title") == t[-1]:
					j = i + 1
					if j > len(self.segments) - 1:
						j = 0
					c = self.segments[j].get("title")
					break
		# sorry for all the loops, am noob
		for i, segment in enumerate(self.segments):
			if segment.get("title") == c:
				for j in range(i):
					self.segments.append(self.segments.pop(0))

		return self.segments

	def layerNameEditCallback(self, sender):
		name = sender.get()
		nameClean = re.sub("[^\w\s\.,`~!@#$%^&*()_+\[\]\{\}\\\|<>/?;:\'\"-=]", "", name)

		error = self.addLayerSheet.errorLabel
		button = self.addLayerSheet.addLayerButton

		# don't duplicate sibling layer names
		if nameClean in self.parent.targetLayerDisplayNames:
			showError = 1
			enableButton = 0
		elif nameClean == "":
			showError = 0
			enableButton = 0
		else:
			showError = 0
			enableButton = 1

		error.show(showError)
		button.enable(enableButton)
		button.getNSButton().highlight_(enableButton)

		sender.set(nameClean)

	def addLayerButtonCallback(self, sender):
		p = self.parent
		newLayer = p.openFonts[p.selectedTargetFont].newLayer(self.addLayerSheet.layerName.get())
		colorButton = self.addLayerSheet.colorButton

		c = colorButton.segmentDescriptions[colorButton.get()]["NSColor"]
		lc = c.colorUsingColorSpaceName_(AppKit.NSCalibratedRGBColorSpace)
		newLayer.color = lc.getRed_green_blue_alpha_(None, None, None, None)
		p.openFonts[p.selectedTargetFont].save()
		p.newLayerWasAdded = 1
		self.closeAddLayerSheetCallback(None)

	def closeAddLayerSheetCallback(self, sender):
		self.parent.layerSheet = None
		self.addLayerSheet.close()
		del self
