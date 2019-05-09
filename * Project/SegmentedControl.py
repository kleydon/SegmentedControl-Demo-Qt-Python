# A Segmented Control Class for PyQt

#  A compact, glanceable alternative to radio buttons. Particularly suitable for situations where
#  there is horizontal (but not vertical) space.



# To do:

# * Has been tested under Snow Leopard on the Mac, but may require tuning to accomodate native look under
#   Mac OS X Lion and beyond.
#
# * Currently, the color of the divider, as well as its height, makes some use of hard-coded values
#
# * On Snow Leopard on the Mac, with the native look, using icons taller than the buttons (~25 px high?) breaks the look.
#   This appears to be a limitation of Qt on the Mac, using the Mac native look.
#
#  * In the unlikely event that the "flat" option is set to True, buttons don't look right in their down and checked states.
#    In order to fix this, the paintEvent below would need to be modified.
#
# * To acheive flat joining of buttons, a portion of the button (left, right, or both sides) is "trimmed". Currently,
#   the number of pixels that are trimmed is hard-coded to be greater than the radius of any style of rounded corner.
#   It might be better to base the number of pixels trimmed on the button curvature, if this can be queried in software...
#
# * Currently, a button's minimum size is determined by the contents of the button (text, icon, or both).
#   Potentially, the button could alternatively determine the space available to display its contents (elided text, etc).
#
# * Currently, there's no way implemented to set a *maximum* width or height for the control as a whole
#
# * Currently, there's no way implemented to set a *fixed* width or height for the control as a whole
#
# * Currently, there's no "over" or "hover" state; perhaps this would be desireable



from PyQt4 import QtGui
from PyQt4 import QtCore
import sys, os, platform



# SegmentedControl class
#
#  A compact, glanceable alternative to radio buttons; particularly suitable for situations where
#  there is horizontal (but not vertical) space.
#
#  A control, consisting of a row of SegmentButtons (defined below), such that
#  any rounded corner styling appears at the corners of the control as a whole,
#  and NOT at the corners of each constituent button.
#
#  The control supports signals typical of QButtonGroups:
#  * buttonClicked, buttonIdClicked
#  * buttonPressed, buttonIdPressed
#  * buttonReleased, buttonIdReleased
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
class SegmentedControl(QtGui.QWidget):
	
	#Signals
	
	#Button-based
	buttonClicked = QtCore.pyqtSignal(QtGui.QAbstractButton)
	buttonPressed = QtCore.pyqtSignal(QtGui.QAbstractButton)
	buttonReleased = QtCore.pyqtSignal(QtGui.QAbstractButton)
	
	#ButtonID-based 
	buttonIdClicked = QtCore.pyqtSignal(int);
	buttonIdPressed = QtCore.pyqtSignal(int)
	buttonIdReleased = QtCore.pyqtSignal(int)
	
	
	def __init__(self, is_exclusive=True, parent=None):
		
		#Init the base class
		QtGui.QWidget.__init__(self, parent)
		
		#Init class instance variables
		self.trim_off = 30 #Number picked to be greater than the outer radius of any button curvature
		self.__is_flat = False
		self.__is_enabled = True
		
		#Segment Buttons
		self.segment_buttons = []
		
		#Layout
		self.horiz_layout = QtGui.QHBoxLayout()
		self.horiz_layout.setSpacing(self.calcInterSegmentButtonSpacing()); #space between widgets within a layout	
		self.horiz_layout.setContentsMargins(0, 0, 0, 0) #space around widgets within a layout	
		self.setLayout(self.horiz_layout)
		#self.setGeometry(0, 0, 400, 100)
		
		#Button Group
		self.button_group = QtGui.QButtonGroup(self)
		self.button_group.setExclusive(is_exclusive)
		
		#Signals
		#By Button
		self.button_group.buttonClicked[QtGui.QAbstractButton].connect(self.buttonClicked.emit)
		self.button_group.buttonPressed[QtGui.QAbstractButton].connect(self.buttonPressed.emit)
		self.button_group.buttonReleased[QtGui.QAbstractButton].connect(self.buttonReleased.emit)
	
		#By Button Group ID
		self.button_group.buttonClicked[int].connect(self.buttonIdClicked.emit)
		self.button_group.buttonPressed[int].connect(self.buttonIdPressed.emit)
		self.button_group.buttonReleased[int].connect(self.buttonIdReleased.emit)
			
			
	def sizeHint(self):
		width = 0
		height = 0
		num_buttons = len(self.segment_buttons)	
		if (num_buttons==0):
			return QtCore.QSize()
		for sb in self.segment_buttons:
			width+=sb.sizeHint().width()
			height = max(height, sb.sizeHint().height())
		return QtCore.QSize(width, height)

	def minimumSizeHint(self): 
		return self.sizeHint()
	
	
	def setFlat(self, flat):
		for sb in self.segment_buttons:
			sb.setFlat(flat)		
		self.__is_flat = flat
		self.horiz_layout.setSpacing(self.calcInterSegmentButtonSpacing()); 	
		self.setLayout(self.horiz_layout)
	def isFlat(self):
		return self.__is_flat


	def setEnabled(self, enabled):
		for sb in self.segment_buttons:
			sb.setEnabled(enabled)
		self.__is_enabled = enabled
	def isEnabled(self):
		return self.__is_enabled
	

	def setExclusive(self, is_exclusive):
		self.button_group.setExclusive(is_exclusive)		
	def isExclusive(self):
		return self.button_group.isExclusive()


	def getControlState(self): #Return as a list - in the order of the segment_buttons list - of true/false values
		button_states = [] 
		for sb in self.segment_buttons:
			button_states.append(sb.isChecked())
		return button_states
			
			
	def getButtonState(self, button_index): #Return as a list - in the order of the segment button list - of true/false values
		if (button_index<len(self.segment_buttons)): #Ensure button index is not too large to be in list
			return self.segment_buttons[button_index].isChecked()
			
	def setButtonState(self, button_index, state):
		if (button_index<len(self.segment_buttons)): #Make sure button index is not too large to be in list
			self.segment_buttons[button_index].setChecked(state)
		

		
	def AppendSegmentButton(self, sb_text_str, sb_icon_path="", sb_icon_size=QtCore.QSize() ):
		
		#Calc length of list, before appending
		sb_list_length = len(self.segment_buttons)
		
		#Determine whether the button to be appendend will be left-hand, central or right-hand
		new_lrc_position = segmentButton.SEGMENT_BUTTON_POS_RIGHTMOST
		if (sb_list_length==0):
			new_lrc_position = segmentButton.SEGMENT_BUTTON_POS_CENTRAL
			
		#Adjust whether the button that will PRECEDE the button to be appended
		#will be left-hand, central or righ-hand
		prev_lrc_position = segmentButton.SEGMENT_BUTTON_POS_CENTRAL
		if (sb_list_length>0):
			if (sb_list_length==1):
				prev_lrc_position = segmentButton.SEGMENT_BUTTON_POS_LEFTMOST
			self.segment_buttons[sb_list_length-1].lrc_position = prev_lrc_position
			
		#Create the button, with a unique index (happens to be equal to list length before appending)
		sb = segmentButton(sb_list_length, new_lrc_position, self.isEnabled(), False, self.trim_off, parent=self)
				
		#Flat?
		sb.setFlat(False)
		if (self.isFlat()):
			sb.setFlat(True)
		
		#Text and icon
		sb.setText(sb_text_str);
		if (sb_icon_path):
			sb.setIcon(QtGui.QIcon(sb_icon_path))
			sb.setIconSize(sb_icon_size)
		
		#Append the button to the list of buttons
		self.segment_buttons.append(sb)
		
		#Ensure that all buttons in the control are still the same height
		max_button_height=0
		for sb in self.segment_buttons:
			print sb.sizeHint().height()
			if (max_button_height<sb.sizeHint().height()):	
				max_button_height=sb.sizeHint().height()
		for sb in self.segment_buttons:
			sb.setMinimumSize( sb.sizeHint().width(), max_button_height )
		
		#Add the button to the layout
		self.horiz_layout.addWidget(sb)

		#Add the button to the button group, along with its index
		self.button_group.addButton(sb, sb_list_length)
		
		#Return the button's list index
		return (sb_list_length-1)
				
			
	def calcInterSegmentButtonSpacing(self):
				
		#Handle a Mac-related inconsistency
		if (sys.platform=='darwin' and not self.__is_flat):
			return 12 # True for Aqua theme up to OSX Snow Leopard. (Lion and beyond? Not sure...)
		else:
			return 0 #Where does this come from?
	
#------------------------------------------------------



#  SegmentButton class
#
#  A button, derived from QPushbutton, capable of drawing itself in left-hand,
#  central, and right-hand variations that, when placed side by side (using the
#  SegmentedControl class above), form a control with any styled rounded
#  corners appearing only at the ends of the control as a whole.
#++++++++++++++++++++++++++++++++++++++++++++++++++++++
class SegmentButton(QtGui.QPushButton):

    SEGMENT_BUTTON_POS_LEFTMOST=0 #Left-hand, central, or right-hand
 	SEGMENT_BUTTON_POS_CENTRAL=1
    SEGMENT_BUTTON_POS_RIGHTMOST=2
	
	SEGMENT_BUTTON_SHIFT_HORIZONTAL=1 #QtGui.QStyle.PM_ButtonShiftHorizontal (Default value seems off...)
	SEGMENT_BUTTON_SHIFT_VERTICAL=1   #QtGui.QStyle.PM_ButtonShiftVertical (Default value seems off...)
	
	SEGMENT_BUTTON_TEXT_ICON_SPACING=10 #Space between text and icon, if both present

	
	def __init__(self, index, lrc_position, enabled, selected, trim, parent=None):
		
		#Init the base class
		QtGui.QPushButton.__init__(self, parent)
	
		#Make the button a checkable button
		self.setCheckable(True)

		#Int class instance variables
		self.index = index
		self.lrc_position = lrc_position
		self.setEnabled(enabled)
		self.setChecked(selected)
		self.trim = trim
		self.__margin = 10
		self.setFlat(parent.isFlat()) #Only really makes sense to set to True on a Mac...

		#Prevent any button within the segmented control from having a focus rectangle
		self.setFocusPolicy(QtCore.Qt.NoFocus)

		#Hook up signals
		#self.clicked.connect(self.got_clicked)
	
	
	def paintEvent(self, event):
		
		painter = QtGui.QStylePainter(self)
		
		option = QtGui.QStyleOptionButton()
		self.initStyleOption(option) 
		
		option.text = ""
		option.icon = QtGui.QIcon()
						
		#Draw button shape/bg - trimming side(s) if necessary
		#If left-most segment...
		if (self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_LEFTMOST):
			option.rect.adjust(0, 0, self.trim, 0) # clip the right-most pixels	
		#If right-most segment...
		elif self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_RIGHTMOST:
			option.rect.adjust(-self.trim, 0, 0, 0) # clip the left-most pixels
		else: #a center segment
			option.rect.adjust(-self.trim/2, 0, self.trim/2, 0) # clip the right and left-most pixels
		self.style().drawControl(QtGui.QStyle.CE_PushButton, option, painter)
		
		
		#Determine where to draw text and/or icon
		#+++++++++++++++++++++++
		button_contents_rect = QtCore.QRect(option.rect)
		button_contents_width = button_contents_rect.width() - self.trim  - 2*self.__margin
		button_contents_height = button_contents_rect.height()
		
		text_width = self.fontMetrics().boundingRect(self.text()).width()
		text_height = self.fontMetrics().boundingRect(self.text()).height()
		icon_width = self.iconSize().width()
		icon_height = self.iconSize().height()
		
		text_offset_x = 0
		text_offset_y = 0
		icon_offset_x = 0
		icon_offset_y = 0
		
		text_offset_y += button_contents_height/2 - text_height/2
		icon_offset_y += button_contents_height/2 - icon_height/2
	
	
		#If we're using Mac Aqua (non-flat) widgets, adjust... **NOTE**: may need to be further adjusted for Lion...
		if (not self.isFlat() and sys.platform=='darwin'):
			text_offset_y -= 3
			icon_offset_y -= 2
			if (self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_LEFTMOST):
				text_offset_x += 6
				icon_offset_x += 6
			elif (self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_RIGHTMOST):
				text_offset_x -= 6
				icon_offset_x -= 6
				
		#If the button is de-pressed, and we're not using Mac Aqua (non-Flat)
		if (self.isEnabled() and self.isDown() and (not self.isFlat() and sys.platform=='darwin')==False ): #If button is de-pressed, and not using Mac Aqua
				text_offset_x += SegmentButton.SEGMENT_BUTTON_SHIFT_HORIZONTAL #QtGui.QStyle.PM_ButtonShiftHorizontal
				text_offset_y += SegmentButton.SEGMENT_BUTTON_SHIFT_VERTICAL #QtGui.QStyle.PM_ButtonShiftVertical
				icon_offset_x += SegmentButton.SEGMENT_BUTTON_SHIFT_HORIZONTAL
				icon_offset_y += SegmentButton.SEGMENT_BUTTON_SHIFT_VERTICAL
				
		#If there's text only
		if ( self.text() and self.icon().isNull() ):
			text_offset_x += self.__margin + button_contents_width/2 - text_width/2
			if (self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_LEFTMOST):
				text_offset_x += 0 
			elif (self.lrc_position==SegmentButton.SEGMENT_BUTTON_POS_RIGHTMOST):
				text_offset_x += self.trim
			else: #A central button...
				text_offset_x += self.trim/2
				
		#If there's an icon only
		elif ( self.text()=="" and self.icon().isNull()==False ):
			icon_offset_x += self.__margin + button_contents_width/2 - icon_width/2
			
		#If there's text and an icon
		elif ( self.text() and self.icon().isNull()==False ):
			#Align with left edge
			text_offset_x += SegmentButton.SEGMENT_BUTTON_TEXT_ICON_SPACING + icon_width
			if (self.lrc_position == SegmentButton.SEGMENT_BUTTON_POS_LEFTMOST): #****
				text_offset_x += 0
				icon_offset_x += 0				
			elif (self.lrc_position == SegmentButton.SEGMENT_BUTTON_POS_RIGHTMOST):
				text_offset_x += self.trim
				icon_offset_x += 0
				#Push to the middle				
			else: #a central button...
				text_offset_x += self.trim/2
				icon_offset_x += 0
			#Find x coordinates for left side of icon and text
			text_offset_x += self.__margin + button_contents_width/2-(icon_width+SegmentButton.SEGMENT_BUTTON_TEXT_ICON_SPACING+text_width)/2
			icon_offset_x += self.__margin + button_contents_width/2-(icon_width+SegmentButton.SEGMENT_BUTTON_TEXT_ICON_SPACING+text_width)/2
		#-----------------------
		
		
		#Draw text
		if (self.text()):
			button_contents_rect.translate(text_offset_x, text_offset_y);
			painter.setPen(self.determineTextColor())
			painter.drawText( button_contents_rect, QtCore.Qt.AlignLeft, self.text() )
			
		#Draw icon
		if ( not self.icon().isNull() ):
			icon_coords = QtCore.QPoint(icon_offset_x, icon_offset_y)
			self.drawSegmentIcon(painter, icon_coords)
		
		
		#Draw border lines manually for between button segments (if button outlines are being drawn...)
		# *** STILL HAVE TO MAKE COLOR RELATIVE TO THE BUTTON COLOR PALETTE...
		if (not self.isFlat() or sys.platform == 'darwin'):
			
			#Set divider color/transparency.	
			painter.setPen(self.determineDividerColor())
			
			#Draw the divider lines
			pen_width=1
			pen = QtGui.QPen(QtCore.Qt.black, pen_width, QtCore.Qt.SolidLine)
			painter.setPen(pen)
			divider_x = 0
			divider_top = option.rect.top() + self.calcSeperatorButtonRectTopOffset()
			divider_bottom = option.rect.bottom() - self.calcSeperatorButtonRectBottomOffset()
			#If left-most or central segment...
			if (self.lrc_position == SegmentButton.SEGMENT_BUTTON_POS_RIGHTMOST):
				divider_x = option.rect.left()+(self.trim)
				painter.drawLine(divider_x, divider_top, divider_x, divider_bottom)
			elif (self.lrc_position == SegmentButton.SEGMENT_BUTTON_POS_CENTRAL):
				h = option.rect.left()+(self.trim/2)
				painter.drawLine(divider_x, divider_top, divider_x, divider_bottom)
			
					
	def drawSegmentIcon(self, painter, pos):
				
		#Determine version of icon
		if (self.isEnabled()):
			enabled_or_disabled_icon = QtGui.QIcon.Normal
		else:
			enabled_or_disabled_icon = QtGui.QIcon.Disabled
		#Selected?	
		if (self.isChecked()):
			checked_or_unchecked_icon = QtGui.QIcon.On
		else:
			checked_or_unchecked_icon = QtGui.QIcon.Off
		pixmap = self.icon().pixmap( QtCore.QSize(self.iconSize().width(), self.iconSize().height()), enabled_or_disabled_icon, checked_or_unchecked_icon )
		
		#Draw icon
		painter.drawPixmap(pos, pixmap);
	
	
	def determineTextColor(self): # **Really, this should happen a level above, at the segmented control as a whole...**	
		#Set text color/transparency.
		#Initially assume widget is enabled and selected
		text_color = QtGui.QColor(0, 0, 0, 255)
		if (not self.isEnabled()):
			text_color.setAlphaF(text_color.alphaF()*.60)
		if (not self.isChecked()):
			text_color.setAlphaF(text_color.alphaF()*.90)
		return text_color
	

	def determineDividerColor(self):
		divider_color = QtGui.QColor(0, 0, 0, 255)
		if (not self.isEnabled()):
			divider_color.setAlphaF(divider_color.alphaF()*.80)
		return divider_color
	

	def sizeHint(self): #*** May need work....
	
		val = QtGui.QPushButton.sizeHint(self)
		val.setWidth( val.width() + 2*self.__margin - self.trim) #Is this right?
		
		#If button has an icon AND text, accomodate some spacing between them
		if ( self.text() and self.icon().isNull()==False ):
			val.setWidth( val.width() + SegmentButton.SEGMENT_BUTTON_TEXT_ICON_SPACING) 
		
		#If we're using Mac Aqua (non-flat) widgets, adjust... **NOTE**: may need to be further adjusted for Mac OS Lion...
		if (not self.isFlat() and sys.platform=='darwin'):
			val.setWidth( val.width() + 20 ) #Is this right?
		
		return val
		
		
	def minimumSizeHint(self): 
		return self.sizeHint()
	

	def calcSeperatorButtonRectTopOffset(self):
		#Handle a Mac-related inconsistency
		if (sys.platform == 'darwin'):
			if (not self.isFlat()):
				return 4 # True for Aqua theme up to OSX Snow Leopard. (Lion and beyond? Not sure...)
			else:
				return 1
		else:
			return 1 #Where does this come from?
		
	def calcSeperatorButtonRectBottomOffset(self):
		#Handle a Mac-related inconsistency
		if (sys.platform == 'darwin') :
			if (not self.isFlat()):
				return 7 # True for Aqua theme up to OSX Snow Leopard. (Lion and beyond? Not sure...)
			else:
				return 1 #Where does this come from?
		else:
			return 1 #Where does this come from?
		
#------------------------------------------------------

#-----------------------------------------------------------------------------




#Demo...
#++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

#Callbacks
#++++++++++++++++
#Button-based Callbacks
#Clicked
def firstRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: First Row: ", sc0.segment_buttons[button.index].text()
def secondRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Second Row: ", sc1.segment_buttons[button.index].text()
def thirdRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Third Row, ", sc2.segment_buttons[button.index].text()
def fourthRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Fourth Row, ", sc3.segment_buttons[button.index].text()
def fifthRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Fifth Row, ", sc4.segment_buttons[button.index].text()
def sixthRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Sixth Row, ", sc5.segment_buttons[button.index].text()
def seventhRowClickedButton(button):
	if (button.isEnabled()):
		print "Clicked: Seventh Row, ", sc6.segment_buttons[button.index].text()
		
#Pressed
def firstRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: First Row: ", sc0.segment_buttons[button.index].text()
def secondRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Second Row: ", sc1.segment_buttons[button.index].text()
def thirdRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Third Row, ", sc2.segment_buttons[button.index].text()
def fourthRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Fourth Row, ", sc3.segment_buttons[button.index].text()
def fifthRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Fifth Row, ", sc4.segment_buttons[button.index].text()
def sixthRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Sixth Row, ", sc5.segment_buttons[button.index].text()
def seventhRowPressedButton(button):
	if (button.isEnabled()):
		print "Pressed: Seventh Row, ", sc6.segment_buttons[button.index].text()
		
#Released
def firstRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: First Row: ", sc0.segment_buttons[button.index].text()
def secondRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Second Row: ", sc1.segment_buttons[button.index].text()
def thirdRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Third Row, ", sc2.segment_buttons[button.index].text()
def fourthRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Fourth Row, ", sc3.segment_buttons[button.index].text()
def fifthRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Fifth Row, ", sc4.segment_buttons[button.index].text()
def sixthRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Sixth Row, ", sc5.segment_buttons[button.index].text()
def seventhRowReleasedButton(button):
	if (button.isEnabled()):
		print "Released: Seventh Row, ", sc6.segment_buttons[button.index].text()

#ButtonID-based Callbacks
#Clicked
def firstRowClickedButtonId(button_id):
	if (sc0.segment_buttons[button_id].isEnabled()):
		print "Clicked: First Row, Button #", button_id
def secondRowClickedButtonId(button_id):
	if (sc1.segment_buttons[button_id].isEnabled()):
		print "Clicked: Second Row, Button #", button_id
def thirdRowClickedButtonId(button_id):
	if (sc2.segment_buttons[button_id].isEnabled()):
		print "Clicked: Third Row, Button #", button_id
def fourthRowClickedButtonId(button_id):
	if (sc3.segment_buttons[button_id].isEnabled()):
		print "Clicked: Fourth Row, Button #", button_id
def fifthRowClickedButtonId(button_id):
	if (sc4.segment_buttons[button_id].isEnabled()):
		print "Clicked: Fifth Row, Button #", button_id
def sixthRowClickedButtonId(button_id):
	if (sc5.segment_buttons[button_id].isEnabled()):
		print "Clicked: Sixth Row, Button #", button_id
def seventhRowClickedButtonId(button_id):
	if (sc6.segment_buttons[button_id].isEnabled()):
		print "Clicked: Seventh Row, Button #", button_id	

#Pressed
def firstRowPressedButtonId(button_id):
	if (sc0.segment_buttons[button_id].isEnabled()):
		print "Pressed: First Row, Button #", button_id
def secondRowPressedButtonId(button_id):
	if (sc1.segment_buttons[button_id].isEnabled()):
		print "Pressed: Second Row, Button #", button_id
def thirdRowPressedButtonId(button_id):
	if (sc2.segment_buttons[button_id].isEnabled()):
		print "Pressed: Third Row, Button #", button_id
def fourthRowPressedButtonId(button_id):
	if (sc3.segment_buttons[button_id].isEnabled()):
		print "Pressed: Fourth Row, Button #", button_id
def fifthRowPressedButtonId(button_id):
	if (sc4.segment_buttons[button_id].isEnabled()):
		print "Pressed: Fifth Row, Button #", button_id
def sixthRowPressedButtonId(button_id):
	if (sc5.segment_buttons[button_id].isEnabled()):
		print "Pressed: Sixth Row, Button #", button_id	
def seventhRowPressedButtonId(button_id):
	if (sc6.segment_buttons[button_id].isEnabled()):
		print "Pressed: Seventh Row, Button #", button_id
		
#Released
def firstRowReleasedButtonId(button_id):
	if (sc0.segment_buttons[button_id].isEnabled()):
		print "Released: First Row, Button #", button_id
def secondRowReleasedButtonId(button_id):
	if (sc1.segment_buttons[button_id].isEnabled()):
		print "Released: Second Row, Button #", button_id
def thirdRowReleasedButtonId(button_id):
	if (sc2.segment_buttons[button_id].isEnabled()):
		print "Released: Third Row, Button #", button_id
def fourthRowReleasedButtonId(button_id):
	if (sc3.segment_buttons[button_id].isEnabled()):
		print "Released: Fourth Row, Button #", button_id
def fifthRowReleasedButtonId(button_id):
	if (sc4.segment_buttons[button_id].isEnabled()):
		print "Released: Fifth Row, Button #", button_id
def sixthRowReleasedButtonId(button_id):
	if (sc5.segment_buttons[button_id].isEnabled()):
		print "Released: Sixth Row, Button #", button_id
def seventhRowReleasedButtonId(button_id):
	if (sc6.segment_buttons[button_id].isEnabled()):
		print "Released: Seventh Row, Button #", button_id
#----------------


app = QtGui.QApplication([])

widget = QtGui.QWidget()

vlayout = QtGui.QVBoxLayout(widget)
vlayout.setSpacing(5)
vlayout.setContentsMargins(10, 10, 10, 10)

#Set up the segmented controls
#++++++++++++++++

ql0 = QtGui.QLabel(" \n1. Disabled, Two Buttons:")
sc0 = SegmentedControl()
sc0.AppendSegmentButton("No")
sc0.AppendSegmentButton("Yes")
sc0.setEnabled(False)

ql1 = QtGui.QLabel(" \n2. Enabled, Three Buttons:")
sc1 = SegmentedControl()
sc1.AppendSegmentButton("No")
sc1.AppendSegmentButton("Maybe")
sc1.AppendSegmentButton("Yes")

ql2 = QtGui.QLabel(" \n3. Enabled, NOT Mutually Exclusive:")
sc2 = SegmentedControl(False)
sc2.AppendSegmentButton("No")
sc2.AppendSegmentButton("Maybe")
sc2.AppendSegmentButton("Yes")

ql3 = QtGui.QLabel(" \n4. Text with Icon:")
sc3 = SegmentedControl()
sc3.AppendSegmentButton("No", "./img20x20.png", QtCore.QSize(12,12))
sc3.AppendSegmentButton("Maybe", "./img20x20.png", QtCore.QSize(12,12))
sc3.AppendSegmentButton("Yes", "./img20x20.png", QtCore.QSize(12,12))

ql4 = QtGui.QLabel(" \n5. Icon Only:")
sc4 = SegmentedControl()
sc4.AppendSegmentButton("", "./img20x20.png", QtCore.QSize(14,14))
sc4.AppendSegmentButton("", "./img20x20.png", QtCore.QSize(14,14))
sc4.AppendSegmentButton("", "./img20x20.png", QtCore.QSize(14,14))

ql5 = QtGui.QLabel(" \n6. Larger Icon:")
sc5 = SegmentedControl()
sc5.AppendSegmentButton("", "./img30x30.png", QtCore.QSize(30,30))
sc5.AppendSegmentButton("", "./img30x30.png", QtCore.QSize(30,30))
sc5.AppendSegmentButton("", "./img30x30.png", QtCore.QSize(30,30))

ql6 = QtGui.QLabel(" \n6. Mixed, Four Buttons, Initial Selection:")
sc6 = SegmentedControl()
sc6.AppendSegmentButton("No")
sc6.AppendSegmentButton("Yes", "./img10x10.png", QtCore.QSize(10,10))
sc6.AppendSegmentButton("", "./img20x20.png", QtCore.QSize(20,20))
sc6.AppendSegmentButton("", "./img30x30.png", QtCore.QSize(30,30))

sc6.setButtonState(1, True)
print sc6.getButtonState(0)

sc6_state = sc6.getControlState()
print sc6_state

for i in [0, 1, 2, 3]:
    print sc6.getButtonState(i)
# ----------------


# Hooking up the button-based callbacks
# ++++++++++++++++
# Clicked
sc0.buttonClicked.connect(firstRowClickedButton)
sc1.buttonClicked.connect(secondRowClickedButton)
sc2.buttonClicked.connect(thirdRowClickedButton)
sc3.buttonClicked.connect(fourthRowClickedButton)
# sc4.buttonClicked.connect(fifthRowClickedButton)
# sc5.buttonClicked.connect(sixthRowClickedButton)
# sc6.buttonClicked.connect(seventhRowClickedButton)
'''
# Pressed
sc0.buttonPressed.connect(firstRowPressedButton)
sc1.buttonPressed.connect(secondRowPressedButton)
sc2.buttonPressed.connect(thirdRowPressedButton)
sc3.buttonPressed.connect(fourthRowPressedButton)
sc4.buttonPressed.connect(fifthRowPressedButton)
sc5.buttonPressed.connect(sixthRowPressedButton)
sc6.buttonPressed.connect(seventhRowPressedButton)
#Released
sc0.buttonReleased.connect(firstRowReleasedButton)
sc1.buttonReleased.connect(secondRowReleasedButton)
sc2.buttonReleased.connect(thirdRowReleasedButton)
sc3.buttonReleased.connect(fourthRowReleasedButton)
sc4.buttonReleased.connect(fifthRowReleasedButton)
sc5.buttonReleased.connect(sixthRowReleasedButton)
sc6.buttonReleased.connect(seventhRowReleasedButton)
'''

'''
#Hooking up buttonID-based callbacks
#Clicked
sc0.buttonIdClicked.connect(firstRowClickedButtonId)
sc1.buttonIdClicked.connect(secondRowClickedButtonId)
sc2.buttonIdClicked.connect(thirdRowClickedButtonId)
sc3.buttonIdClicked.connect(fourthRowClickedButtonId)
sc4.buttonIdClicked.connect(fifthRowClickedButtonId)
sc5.buttonIdClicked.connect(sixthRowClickedButtonId)
sc6.buttonIdClicked.connect(seventhRowClickedButtonId)
#Pressed
sc0.buttonIdPressed.connect(firstRowPressedButtonId)
sc1.buttonIdPressed.connect(secondRowPressedButtonId)
sc2.buttonIdPressed.connect(thirdRowPressedButtonId)
sc3.buttonIdPressed.connect(fourthRowPressedButtonId)
sc4.buttonIdPressed.connect(fifthRowPressedButtonId)
sc5.buttonIdPressed.connect(sixthRowPressedButtonId)
sc6.buttonIdPressed.connect(seventhRowPressedButtonId)
#Released
sc0.buttonIdReleased.connect(firstRowReleasedButtonId)
sc1.buttonIdReleased.connect(secondRowReleasedButtonId)
sc2.buttonIdReleased.connect(thirdRowReleasedButtonId)
sc3.buttonIdReleased.connect(fourthRowReleasedButtonId)
'''
sc4.buttonIdReleased.connect(fifthRowReleasedButtonId)
sc5.buttonIdReleased.connect(sixthRowReleasedButtonId)
sc6.buttonIdReleased.connect(seventhRowReleasedButtonId)

#----------------

vlayout.addWidget(ql0)
vlayout.addWidget(sc0)

vlayout.addWidget(ql1)
vlayout.addWidget(sc1)

vlayout.addWidget(ql2)
vlayout.addWidget(sc2)

vlayout.addWidget(ql3)
vlayout.addWidget(sc3)

vlayout.addWidget(ql4)
vlayout.addWidget(sc4)

vlayout.addWidget(ql5)
vlayout.addWidget(sc5)

vlayout.addWidget(ql6)
vlayout.addWidget(sc6)

widget.setGeometry(0, 0, 400, 400)
widget.setWindowTitle('Segmented Buttons')    
widget.show()


app.exec_()

#------------------------------------------------------------------------------






