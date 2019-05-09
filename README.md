# SegmentedControl-Demo-Qt-Python

Strangely, PyQt doesn't include a "stock" segmented control (set of mutually-exclusive, visually abbutting buttons), so I wrote one in Python.


## Usage:

```
#Disabled, Two Buttons:
sc0 = SegmentedControl()
sc0.AppendSegmentButton("No")
sc0.AppendSegmentButton("Yes")
sc0.setEnabled(False)

#Enabled, Three Buttons:
sc1 = SegmentedControl()
sc1.AppendSegmentButton("No")
sc1.AppendSegmentButton("Maybe")
sc1.AppendSegmentButton("Yes")

#Enabled, NOT Mutually Exclusive:
sc2 = SegmentedControl(False)
sc2.AppendSegmentButton("No")
sc2.AppendSegmentButton("Maybe")
sc2.AppendSegmentButton("Yes")

#Text with Icon:
sc3 = SegmentedControl()
sc3.AppendSegmentButton("No", "./../Images/img20x20.png", QtCore.QSize(12, 12))
sc3.AppendSegmentButton("Maybe", "./../Images/img20x20.png", QtCore.QSize(12, 12))
sc3.AppendSegmentButton("Yes", "./../Images/img20x20.png", QtCore.QSize(12, 12))

#Icon Only:
sc4 = SegmentedControl()
sc4.AppendSegmentButton("", "./../Images/img20x20.png", QtCore.QSize(14, 14))
sc4.AppendSegmentButton("", "./../Images/img20x20.png", QtCore.QSize(14, 14))
sc4.AppendSegmentButton("", "./../Images/img20x20.png", QtCore.QSize(14, 14))

#Larger Icon:
sc5 = SegmentedControl()
sc5.AppendSegmentButton("", "./../Images/img30x30.png", QtCore.QSize(30, 30))
sc5.AppendSegmentButton("", "./../Images/img30x30.png", QtCore.QSize(30, 30))
sc5.AppendSegmentButton("", "./../Images/img30x30.png", QtCore.QSize(30, 30))

#Mixed; Four Buttons, with an Initial Selection:
sc6 = SegmentedControl()
sc6.AppendSegmentButton("No")
sc6.AppendSegmentButton("Yes", "./../Images/img10x10.png", QtCore.QSize(10, 10))
sc6.AppendSegmentButton("", "./../Images/img20x20.png", QtCore.QSize(20, 20))
sc6.AppendSegmentButton("", "./../Images/img30x30.png", QtCore.QSize(30, 30))
sc6.setButtonState(1, True)

#Setting up Button Callbacks
#Clicked:
sc0.buttonIdClicked.connect(firstRowClickedButtonId)
#Pressed:
sc0.buttonIdPressed.connect(firstRowPressedButtonId)
#Released:
sc0.buttonIdReleased.connect(firstRowReleasedButtonId)
```

