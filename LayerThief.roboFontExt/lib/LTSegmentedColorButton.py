import AppKit
import vanilla
import LTSegmentedColorCell

class LTSegmentedColorButton(vanilla.SegmentedButton):

	defaultCellClass = LTSegmentedColorCell.LTSegmentedColorCell
	nsSegmentedCellMargin = 3			# hardcoded in NSSegmentedControl
	nsSegmentedCellSegmentMargin = 1	# hardcoded in NSSegmentedControl
	selectionFrameScale = 0.227			# * 22px target size = ~5px
	colorFrameScale = 0.727				# * 22px target size = ~16px
	highlightScale = 0.045				# * 22px target size = ~1px
	defaultSegmentColor = AppKit.NSColor.magentaColor()
	segmentDescriptions = []
	defaultSegmentSelection = 0

	def __init__(self, posSize, segmentDescriptions, callback=None):
		self.segmentDescriptions = segmentDescriptions
		self.defaultCellClass.segmentColors = []

		# allow specific height to be set from posSize
		if posSize[3] >= 24: 
			sizeStyle = "regular"
		elif posSize[3] >= 21: 
			sizeStyle = "small"
		else: 
			sizeStyle = "mini"

		# initial margin
		segmentedButtonWidth = self.nsSegmentedCellMargin * 2
		
		# make sure widths exist in dict, harvest colors for cell
		for i, desc in enumerate(self.segmentDescriptions):
			segmentWidth = desc.get("width")
			# if no width correct the dict
			if segmentWidth == None:
				segmentWidth = posSize[3]
				desc.update({"width": segmentWidth})
			# accumulate width from segment + margin if no control width set
			if posSize[2] == 0: 
				segmentedButtonWidth += segmentWidth + self.nsSegmentedCellSegmentMargin
			# cell colors
			self.defaultCellClass.segmentColors.append(desc.get("NSColor", self.defaultSegmentColor))
		
		# set frame adjustment to pull the first circle flush with the initial control x coord		
		segmentWidth = self.segmentDescriptions[0].get("width", posSize[3])
		self.frameAdjustments = { sizeStyle: ((self.nsSegmentedCellMargin + (segmentWidth - (segmentWidth * self.colorFrameScale)) / 2) * -1, 2, 0, 0) }
		self.defaultCellClass.segmentInitialX = self.nsSegmentedCellMargin
		self.defaultCellClass.segmentMargin = self.nsSegmentedCellSegmentMargin
		self.defaultCellClass.selectionFrameScale = self.selectionFrameScale
		self.defaultCellClass.colorFrameScale = self.colorFrameScale
		self.defaultCellClass.highlightScale = self.highlightScale
		self.nsSegmentedCellClass = self.defaultCellClass

		posSize = (posSize[0], posSize[1], segmentedButtonWidth, posSize[3])
		vanilla.SegmentedButton.__init__(self, posSize, self.segmentDescriptions, callback, "one", sizeStyle)
		
		# set first segment selected
		if self.defaultSegmentSelection in range(len(self.segmentDescriptions)):
			vanilla.SegmentedButton.set(self, self.defaultSegmentSelection)
