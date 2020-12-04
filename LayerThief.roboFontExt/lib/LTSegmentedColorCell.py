import AppKit

class LTSegmentedColorCell(AppKit.NSSegmentedCell):

	segmentColors = []
	segmentInitialX = 0
	segmentMargin = 0
	selectionFrameScale = 0
	colorFrameScale = 0
	selectionFrameColor = AppKit.NSColor.whiteColor()
	highlightScale = 0
	highlightColor = AppKit.NSColor.labelColor()
	highlightAlpha = 0.1725	# alpha has to be applied at draw time for dynamic colors to respond to appearance changes

	# drawSegment_inFrame_withView_ simply draws on top of the MacOS NSSegmentedControl chrome in the bounds of each segment.
	# drawWithFrame_inView_ redraws the whole control, but the clickable tracking area is determined by the control properties, not the image drawn.
	def drawWithFrame_inView_(self, frame, view):
		segments = view.segmentCount()
		segmentX  = self.segmentInitialX

		for i in range(segments):
			# draw color circle and interior stroke
			sw = self.widthForSegment_(i)
			colorFrameOffset = (sw - sw * self.colorFrameScale) / 2
			colorFrame = AppKit.NSMakeRect(segmentX + colorFrameOffset, frame.origin.y + colorFrameOffset, sw - colorFrameOffset * 2, frame.size.height - colorFrameOffset * 2)
			path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(colorFrame)			
			path.setClip()
			self.segmentColors[i].setFill()
			path.fill()
			path.setLineWidth_((sw * self.highlightScale) * 2) # double the stroke & clip the overhang
			self.highlightColor.colorWithAlphaComponent_(self.highlightAlpha).setStroke()
			path.stroke()

			if self.isSelectedForSegment_(i):
				# draw selection dot in the middle
				selectionFrameOffset = (sw - sw * self.selectionFrameScale) / 2
				selectionFrame = AppKit.NSMakeRect(segmentX + selectionFrameOffset, frame.origin.y + selectionFrameOffset, sw - selectionFrameOffset * 2, frame.size.height - selectionFrameOffset * 2)
				path = AppKit.NSBezierPath.bezierPathWithOvalInRect_(selectionFrame)
				self.selectionFrameColor.setFill()
				path.fill()

			segmentX += self.widthForSegment_(i) + self.segmentMargin
