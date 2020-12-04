import AppKit
import vanilla
import mojo
import LTAddLayerSheet
import LTUi

class LayerThief(object):

	# obj
	ui = LTUi.LTUi()
	layerSheet = None

	# ranges roughly aligned with NSColor systemColors used in LTAddLayerSheet
	hues = [
		{"title":"Pink", "ranges": [(296, 350)]},
		{"title":"Red", "ranges": [(0, 12), (351, 360)]},
		{"title":"Orange", "ranges": [(13, 40)]},
		{"title":"Yellow", "ranges": [(41, 65)]},
		{"title":"Green", "ranges": [(66, 160)]},
		{"title":"Teal", "ranges": [(161, 205)]},
		{"title":"Blue", "ranges": [(206, 240)]},
		{"title":"Indigo", "ranges": [(241, 265)]},
		{"title":"Purple", "ranges": [(266, 295)]},
	]

	# font
	openFonts = []
	openFontDisplayNames = []
	sourceLayerDisplayNames = []
	targetLayerColorHues = []
	newLayerWasAdded = 0
	selectedSourceFont = 0
	selectedSourceLayer = 0
	selectedTargetFont = 0
	overwriteGlyphs = 1
	overwriteMarks = 0
	targetLayerAddIndex = 0
	fontOpenActionIndex = 0
	ltOpeningFontWithUi = 0

	# string
	layerPopUpActionTitle = "Add Layer..."
	fontPopUpOpenTitle = "Open Font..."
	glyphsCheckBoxTitle = "Overwrite Target Layer Glyphs"
	marksCheckBoxTitle = "Include Marks"
	sourceFontTitle = "Source:"
	targetFontTitle = "Target:"
	copyButtonTitle = "Copy"
	noFamilyTitle = "(No Family Name)"
	sourceFontKey = "S"
	sourceLayerKey = "s"
	targetFontKey = "T"
	targetLayerKey = "t"
	copyButtonKey = "c" # using cmd also
	overWriteGlyphsKey = "com.rmc.layerthief.overwriteGlyphs"
	overWriteMarksKey = "com.rmc.layerthief.overwriteMarks"

	def __init__(self):
		# window
		self.fullWidth = self.ui.w(11.4)
		self.winWidth = self.ui.w() + self.fullWidth + self.ui.w()
		# window ui
		self.w = vanilla.Window((0, 0), "Layer Thief")
		# events
		self.w.bind("became key", self.windowBecameKey)
		self.w.bind("close", self.windowWillClose)
		mojo.events.addObserver(self, "fontWillClose", "fontWillClose")
		mojo.events.addObserver(self, "fontDidOpen", "fontDidOpen")
		# source ui
		self.w.sourceFontLabel = vanilla.TextBox((self.ui.x(), self.ui.y() + 1, self.ui.w(2.4), self.ui.h("textBox")), self.sourceFontTitle, alignment="right")
		self.w.sourceFontPopUp = vanilla.PopUpButton((self.ui.x(2.4), self.ui.y(), self.ui.w(9), self.ui.h("popUp")), [], callback=self.fontPopUpCallback)
		self.w.sourceLayerPopUp = vanilla.PopUpButton((self.ui.x(2.4), self.ui.y(1), self.ui.w(9), self.ui.h("popUp")), [], callback=self.layerPopUpCallback)
		self.w.sourceFontPopUp.getNSPopUpButton().setKeyEquivalent_(self.sourceFontKey)
		self.w.sourceLayerPopUp.getNSPopUpButton().setKeyEquivalent_(self.sourceLayerKey)
		# target ui
		self.w.targetFontLabel = vanilla.TextBox((self.ui.x(), self.ui.y(2) + 1, self.ui.w(2.4), self.ui.h("textBox")), self.targetFontTitle, alignment="right")
		self.w.targetFontPopUp = vanilla.PopUpButton((self.ui.x(2.4), self.ui.y(), self.ui.w(9), self.ui.h("popUp")), [], callback=self.fontPopUpCallback)
		self.w.targetLayerPopUp = vanilla.PopUpButton((self.ui.x(2.4), self.ui.y(1), self.ui.w(9), self.ui.h("popUp")), [], callback=self.layerPopUpCallback)
		self.w.targetFontPopUp.getNSPopUpButton().setKeyEquivalent_(self.targetFontKey)
		self.w.targetLayerPopUp.getNSPopUpButton().setKeyEquivalent_(self.targetLayerKey)
		# control ui
		# magic numbers for box fitment and checkbox placement ^ _ ^
		bfa = vanilla.Box.allFrameAdjustments
		vanilla.Box.allFrameAdjustments = {"Box-None": (-13, -4, 24, 0)}
		self.w.actionBox = vanilla.Box((self.ui.x(), self.ui.y(2), self.fullWidth, self.ui.h("row") * 2))
		vanilla.Box.allFrameAdjustments = bfa
		# checks
		self.overwriteGlyphs = mojo.extensions.getExtensionDefault(self.overWriteGlyphsKey, fallback=self.overwriteGlyphs)
		self.w.glyphsCheckBox = vanilla.CheckBox((self.ui.x(), self.ui.y() + 11, self.ui.w(7), self.ui.h("checkBox", 1)), self.glyphsCheckBoxTitle, callback=self.glyphsCheckBoxCallback, value=self.overwriteGlyphs, sizeStyle="small")
		self.overwriteMarks = mojo.extensions.getExtensionDefault(self.overWriteMarksKey, fallback=self.overwriteMarks)
		self.w.marksCheckBox = vanilla.CheckBox((self.ui.x(), self.ui.y(1) + 3, self.ui.w(7), self.ui.h("checkBox", 1)), self.marksCheckBoxTitle, callback=self.marksCheckBoxCallback, value=self.overwriteMarks, sizeStyle="small")
		# copy
		self.w.copyButton = vanilla.Button((self.ui.x(-4) + 1, self.ui.y(), self.ui.w(4), self.ui.h("button")), self.copyButtonTitle, callback=self.copyButtonCallback)
		# self.w.copyButton.getNSButton().setKeyEquivalentModifierMask_(AppKit.NSCommandKeyMask)
		# self.w.copyButton.getNSButton().setKeyEquivalent_(self.copyButtonKey)
		# bottom margin
		self.w.resize(self.winWidth, self.ui.y(1.4))
		# gobble up open fonts, if any
		if AllFonts():
			self.openFonts = AllFonts()
			self._refresh()
		#
		# self.windowBecameKey() fires for the first time
		#
		self.w.open()
		self.w.center()

	def _refresh(self, sourcePreserveIndex=0, targetPreserveIndex=0):
		self._updateFontDisplayNames()
		self._updateFontPopUp("source", sourcePreserveIndex)
		self._updateLayerPopUp("source", sourcePreserveIndex)
		self._updateFontPopUp("target", targetPreserveIndex)
		self._updateLayerPopUp("target", targetPreserveIndex)
		self._verifyCanCopy()

	def _verifyCanCopy(self):
		o = self.openFonts
		c = self.w.copyButton

		c.enable(0)

		if o:
			if o[self.selectedSourceFont] != o[self.selectedTargetFont]:
				c.enable(1)
			else:
				s = self.w.sourceLayerPopUp.getItem()
				if s in o[self.selectedSourceFont].layerOrder:
					t = self.w.targetLayerPopUp.getItem()
					if t in o[self.selectedTargetFont].layerOrder:
						if s != t:
							c.enable(1)

	def _getSelectedPopUpFont(self, popUp):
		if popUp == "source":
			return self.selectedSourceFont
		elif popUp == "target":
			return self.selectedTargetFont

	def _setSelectedPopUpFont(self, popUp, newValue):
		if popUp == "source":
			self.selectedSourceFont = newValue
		elif popUp == "target":
			self.selectedTargetFont = newValue

	def _getPopUpUi(self, popUp, uiType):
		if popUp == "source":
			if uiType == "font":
				return self.w.sourceFontPopUp
			elif uiType == "layer":
				return self.w.sourceLayerPopUp
		elif popUp == "target":
			if uiType == "font":
				return self.w.targetFontPopUp
			elif uiType == "layer":
				return self.w.targetLayerPopUp

	def _updateFontDisplayNames(self):
		self.openFontDisplayNames = []

		for font in self.openFonts:
			if font.info.familyName != None:
				name = font.info.familyName
			else:
				name = self.noFamilyTitle
			if font.info.styleName != None:
				name += " "
				name += font.info.styleName

			self.openFontDisplayNames.append(name)

	def _updateFontPopUp(self, popUp, preserveCurrentIndex=0):
		p = self._getPopUpUi(popUp, "font")
		f = self._getSelectedPopUpFont(popUp)

		# if user cancels opening fonts, the selected "open font" option is out of range, so correct it
		i = len(self.openFonts) - 1
		current = p.get()
		if current > i:
			current = f

		p.setItems(self.openFontDisplayNames)
		# if preserve index, set to what was current...
		if preserveCurrentIndex:
			p.set(current)
			self._setSelectedPopUpFont(popUp, current)
		# otherwise, use the last value set by fontPopUpCallback()
		# unless its out of range due to a closure, etc
		else:
			if f > i:
				self._setSelectedPopUpFont(popUp, i)
			p.set(f)
		# add separator
		p.getNSPopUpButton().menu().addItem_(AppKit.NSMenuItem.separatorItem())
		# add "open font" option
		p.getNSPopUpButton().addItemWithTitle_(self.fontPopUpOpenTitle)
		self.fontOpenActionIndex = p.getNSPopUpButton().menu().numberOfItems() - 1

	def _updateLayerPopUp(self, popUp, preserveCurrentIndex=0):
		p = self._getPopUpUi(popUp, "layer")
		f = self._getSelectedPopUpFont(popUp)
		popUpIsSource = (0, 1)[popUp == "source"]
		popUpIsTarget = not popUpIsSource

		if not self.openFonts:
			p.getNSPopUpButton().removeAllItems()
			p.enable(0)
		else:
			layers = self.openFonts[f].layers
			# source layer display names used for new layer name suggestions in LTAddLayerSheet
			if popUpIsSource:
				self.sourceLayerDisplayNames = self.openFonts[f].layerOrder
			# if LTAddLayerSheet added a layer, set it as current
			if self.newLayerWasAdded and popUpIsTarget:
				current = len(layers) - 1
				preserveCurrentIndex = 1
				self.newLayerWasAdded = 0
			else:
				current = p.get()

			p.getNSPopUpButton().removeAllItems()
			# colors for LTAddLayerSheet suggestions
			if popUpIsTarget:
				self.targetLayerColorHues = []
			# draw layer color preview images
			for layer in layers:
				item = AppKit.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(layer.name, None, "")
				color = AppKit.NSColor.colorWithDeviceRed_green_blue_alpha_(layer.color[0], layer.color[1], layer.color[2], layer.color[3])
				# store target layer colors so that LTAddLayerSheet can make "intelligent" suggestions
				if popUpIsTarget:
					self._getTargetLayerHue(color.hueComponent())
				item.setImage_(self._makeColorPreviewImage(color))
				p.getNSPopUpButton().menu().addItem_(item)

			if preserveCurrentIndex and current > -1:
				p.set(current)
			# target layer list, include add layer action
			if popUpIsTarget:
				# add separator
				p.getNSPopUpButton().menu().addItem_(AppKit.NSMenuItem.separatorItem())
				# add add layer option
				p.getNSPopUpButton().addItemWithTitle_(self.layerPopUpActionTitle)
				self.targetLayerAddIndex = p.getNSPopUpButton().menu().numberOfItems() - 1
			elif popUpIsSource:
				self.sourceLayer = p.get()

			p.enable(1)

	def _makeColorPreviewImage(self, fillColor=AppKit.NSColor.magentaColor(), strokeColor=AppKit.NSColor.labelColor(), strokeAlpha=0.25, strokeWidth=1):
		size = AppKit.NSMakeSize(self.ui.w(), self.ui.h("colorPreviewImage"))
		rect = AppKit.NSMakeRect(0, 0, size.width, size.height)
		path = AppKit.NSBezierPath.bezierPathWithRect_(rect)
		img = AppKit.NSImage.imageWithSize_flipped_drawingHandler_(size, False, lambda arg: _draw())

		def _draw():
			fillColor.setFill()
			# alpha has to be applied at draw time for dynamic colors to respond to appearance changes
			strokeColor.colorWithAlphaComponent_(strokeAlpha).setStroke()
			path.setLineWidth_(strokeWidth)
			path.fill()
			path.stroke()
			return True

		return img

	def _getTargetLayerHue(self, hueComponent=0.83):
		hueComponent *= 360
		for i, hue in enumerate(self.hues):
			for hueRange in hue.get("ranges"):
				if hueComponent >= hueRange[0] and hueComponent <= hueRange[1]:
					h = hue.get("title")
					# cycle duplicates to the end, recency is used in color suggestion
					if h in self.targetLayerColorHues:
						h = self.targetLayerColorHues.pop(self.targetLayerColorHues.index(h))
					self.targetLayerColorHues.append(h)

	def _openNewFonts(self, popUp):
		preserveSource = (1, 0)[popUp == "source"]
		preserveTarget = not preserveSource
		self.ltOpeningFontWithUi = 1
		# open file ui
		newFonts = OpenFont()
		# cancel fires windowBecameKey(), so only new additions handled here
		if newFonts:
			addFonts = []
			# one font else multiple
			if not isinstance(newFonts, list):
				addFonts.append(newFonts)
			else:
				addFonts = newFonts

			o = self.openFonts
			a = 1
			i = 0

			for font in addFonts:
				# for some reason only one font would open with interface per self.w in my use
				if font.hasInterface() != True:
					font.openInterface()
				for f in o:
					if f.path == font.path:
						i = o.index(f)
						f = font
						a = 0
						break
				if a:
					o.append(font)
					i = len(o) - 1
				else:
					a = 1

			self._setSelectedPopUpFont(popUp, i)
			self._refresh(preserveSource, preserveTarget)

		self.ltOpeningFontWithUi = 0

	#
	# events
	#

	def windowBecameKey(self, sender):
		# did a font name, layers, etc change while we were away?
		self._refresh(1, 1)

	def windowWillClose(self, sender):
		mojo.events.clearObservers()

	def fontDidOpen(self, font):
		# if *we* initiate opening a font and not RF, stay on top
		if self.ltOpeningFontWithUi:
			self.w.getNSWindow().makeKeyAndOrderFront_(None)
			return

		# otherwise, get that font for our list
		# external open resigns key for us, so let windowBecameKey() update the ui on return
		f = font.get("font")
		a = 1

		for fo in self.openFonts:
			if fo.path == f.path:
				fo = f
				a = 0
				break
		if a:
			self.openFonts.append(f)

	def fontWillClose(self, font):
		f = font.get("font")
		o = self.openFonts
		s = 1
		t = 1 
		# font with ui closes, make sure to kill layer sheet and/or refresh
		if f in o:
			if f == o[self.w.sourceFontPopUp.get()]:
				if self.layerSheet != None:
					self.layerSheet.closeAddLayerSheetCallback(None)
				s = 0
			if f == o[self.w.targetFontPopUp.get()]:
				t = 0
			o.remove(f)
			self._refresh(s, t)

	def fontPopUpCallback(self, sender):
		s = sender.get()
		popUp = ("target", "source")[sender == self.w.sourceFontPopUp]
		# user chose a font
		if s <= (len(self.openFonts) - 1):
			self._setSelectedPopUpFont(popUp, s)
			self._updateLayerPopUp(popUp)
			self._verifyCanCopy()
		# user chose open font option
		elif s == self.fontOpenActionIndex:
			self._openNewFonts(popUp)

	def layerPopUpCallback(self, sender):
		s = sender.get()
		if sender == self.w.sourceLayerPopUp:
			self.sourceLayer = s
			self._verifyCanCopy()
		elif sender == self.w.targetLayerPopUp:
			self._verifyCanCopy()
			if s == self.targetLayerAddIndex:
				self.layerSheet = LTAddLayerSheet.LTAddLayerSheet(self)

	def glyphsCheckBoxCallback(self, sender):
		self.overwriteGlyphs = sender.get()
		mojo.extensions.setExtensionDefault(self.overWriteGlyphsKey, self.overwriteGlyphs)

	def marksCheckBoxCallback(self, sender):
		self.overwriteMarks = sender.get()
		mojo.extensions.setExtensionDefault(self.overWriteMarksKey, self.overwriteMarks)

	def copyButtonCallback(self, sender):
		sourceLayer = self.openFonts[self.selectedSourceFont].getLayer(self.w.sourceLayerPopUp.getItem())
		targetLayer = self.openFonts[self.selectedTargetFont].getLayer(self.w.targetLayerPopUp.getItem())

		for sourceGlyph in sourceLayer:
			if self.overwriteGlyphs or sourceGlyph.name not in targetLayer.keys():
				newGlyph = sourceGlyph.copy()
				if not self.overwriteMarks:
					newGlyph.markColor = None
				targetLayer[sourceGlyph.name] = newGlyph

OpenWindow(LayerThief)
