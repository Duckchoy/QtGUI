# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file '*.ui'
##
## Created by: Qt User Interface Compiler version 5.15.3
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class MainUI(object):
        def setupUi(self, RBDS):
                if not RBDS.objectName():
                        RBDS.setObjectName(u"RBDS")
                RBDS.resize(1141, 807)
                font = QFont()
                font.setPointSize(11)
                RBDS.setFont(font)
                self.centralwidget = QWidget(RBDS)
                self.centralwidget.setObjectName(u"centralwidget")
                font1 = QFont()
                font1.setPointSize(12)
                self.centralwidget.setFont(font1)
                self.formLayout = QFormLayout(self.centralwidget)
                self.formLayout.setObjectName(u"formLayout")
                self.frame = QFrame(self.centralwidget)
                self.frame.setObjectName(u"frame")
                self.frame.setMinimumSize(QSize(300, 200))
                self.frame.setMaximumSize(QSize(450, 1000))
                self.gridLayout = QGridLayout(self.frame)
                self.gridLayout.setObjectName(u"gridLayout")
                self.horizontalSpacer_61 = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.gridLayout.addItem(self.horizontalSpacer_61, 4, 0, 1, 1)

                self.verticalLayout_5 = QVBoxLayout()
                self.verticalLayout_5.setObjectName(u"verticalLayout_5")
                self.horizontalLayout_16 = QHBoxLayout()
                self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
                self.horizontalSpacer_36 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_16.addItem(self.horizontalSpacer_36)

                self.label_11 = QLabel(self.frame)
                self.label_11.setObjectName(u"label_11")
                font2 = QFont()
                font2.setPointSize(12)
                font2.setBold(True)
                font2.setWeight(75)
                self.label_11.setFont(font2)

                self.horizontalLayout_16.addWidget(self.label_11)

                self.horizontalSpacer_37 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_16.addItem(self.horizontalSpacer_37)


                self.verticalLayout_5.addLayout(self.horizontalLayout_16)

                self.horizontalLayout_14 = QHBoxLayout()
                self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
                self.horizontalSpacer_32 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_14.addItem(self.horizontalSpacer_32)

                self.label_10 = QLabel(self.frame)
                self.label_10.setObjectName(u"label_10")

                self.horizontalLayout_14.addWidget(self.label_10)

                self.boxAlpha = QLineEdit(self.frame)
                self.boxAlpha.setObjectName(u"boxAlpha")
                self.boxAlpha.setMaximumSize(QSize(30, 30))

                self.horizontalLayout_14.addWidget(self.boxAlpha)

                self.horizontalSpacer_33 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_14.addItem(self.horizontalSpacer_33)


                self.verticalLayout_5.addLayout(self.horizontalLayout_14)

                self.horizontalLayout_15 = QHBoxLayout()
                self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
                self.horizontalSpacer_34 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_15.addItem(self.horizontalSpacer_34)

                self.label_21 = QLabel(self.frame)
                self.label_21.setObjectName(u"label_21")

                self.horizontalLayout_15.addWidget(self.label_21)

                self.boxGridX = QSpinBox(self.frame)
                self.boxGridX.setObjectName(u"boxGridX")
                self.boxGridX.setMaximumSize(QSize(40, 30))
                self.boxGridX.setMinimum(1)
                self.boxGridX.setMaximum(20)
                self.boxGridX.setValue(5)

                self.horizontalLayout_15.addWidget(self.boxGridX)

                self.boxGridY = QSpinBox(self.frame)
                self.boxGridY.setObjectName(u"boxGridY")
                self.boxGridY.setMaximumSize(QSize(40, 30))
                self.boxGridY.setMinimum(1)
                self.boxGridY.setMaximum(20)
                self.boxGridY.setValue(5)

                self.horizontalLayout_15.addWidget(self.boxGridY)

                self.boxGridZ = QSpinBox(self.frame)
                self.boxGridZ.setObjectName(u"boxGridZ")
                self.boxGridZ.setMaximumSize(QSize(40, 30))
                self.boxGridZ.setMinimum(1)
                self.boxGridZ.setMaximum(20)
                self.boxGridZ.setValue(2)

                self.horizontalLayout_15.addWidget(self.boxGridZ)

                self.horizontalSpacer_35 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_15.addItem(self.horizontalSpacer_35)


                self.verticalLayout_5.addLayout(self.horizontalLayout_15)

                self.horizontalLayout_17 = QHBoxLayout()
                self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
                self.horizontalSpacer_38 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_17.addItem(self.horizontalSpacer_38)

                self.checkGenCtrl = QCheckBox(self.frame)
                self.checkGenCtrl.setObjectName(u"checkGenCtrl")
                self.checkGenCtrl.setMaximumSize(QSize(16777215, 30))
                self.checkGenCtrl.setChecked(True)

                self.horizontalLayout_17.addWidget(self.checkGenCtrl)

                self.horizontalSpacer_39 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_17.addItem(self.horizontalSpacer_39)


                self.verticalLayout_5.addLayout(self.horizontalLayout_17)


                self.gridLayout.addLayout(self.verticalLayout_5, 5, 0, 1, 2)

                self.horizontalSpacer_63 = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.gridLayout.addItem(self.horizontalSpacer_63, 8, 0, 1, 1)

                self.verticalLayout_2 = QVBoxLayout()
                self.verticalLayout_2.setObjectName(u"verticalLayout_2")
                self.horizontalLayout_27 = QHBoxLayout()
                self.horizontalLayout_27.setObjectName(u"horizontalLayout_27")
                self.horizontalSpacer_41 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_27.addItem(self.horizontalSpacer_41)

                self.label_25 = QLabel(self.frame)
                self.label_25.setObjectName(u"label_25")
                font3 = QFont()
                font3.setPointSize(12)
                font3.setBold(True)
                font3.setUnderline(False)
                font3.setWeight(75)
                self.label_25.setFont(font3)

                self.horizontalLayout_27.addWidget(self.label_25)

                self.horizontalSpacer_42 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_27.addItem(self.horizontalSpacer_42)


                self.verticalLayout_2.addLayout(self.horizontalLayout_27)

                self.horizontalLayout_30 = QHBoxLayout()
                self.horizontalLayout_30.setObjectName(u"horizontalLayout_30")
                self.horizontalSpacer_45 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_30.addItem(self.horizontalSpacer_45)

                self.label_27 = QLabel(self.frame)
                self.label_27.setObjectName(u"label_27")

                self.horizontalLayout_30.addWidget(self.label_27)

                self.boxDX = QSpinBox(self.frame)
                self.boxDX.setObjectName(u"boxDX")
                self.boxDX.setMaximumSize(QSize(50, 30))
                self.boxDX.setMinimum(1)
                self.boxDX.setMaximum(100)
                self.boxDX.setValue(40)

                self.horizontalLayout_30.addWidget(self.boxDX)

                self.boxDY = QSpinBox(self.frame)
                self.boxDY.setObjectName(u"boxDY")
                self.boxDY.setMaximumSize(QSize(50, 30))
                self.boxDY.setMinimum(1)
                self.boxDY.setMaximum(100)
                self.boxDY.setValue(40)

                self.horizontalLayout_30.addWidget(self.boxDY)

                self.boxDZ = QSpinBox(self.frame)
                self.boxDZ.setObjectName(u"boxDZ")
                self.boxDZ.setMaximumSize(QSize(50, 30))
                self.boxDZ.setMinimum(1)
                self.boxDZ.setMaximum(100)
                self.boxDZ.setValue(20)

                self.horizontalLayout_30.addWidget(self.boxDZ)

                self.horizontalSpacer_64 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_30.addItem(self.horizontalSpacer_64)


                self.verticalLayout_2.addLayout(self.horizontalLayout_30)

                self.horizontalLayout_28 = QHBoxLayout()
                self.horizontalLayout_28.setObjectName(u"horizontalLayout_28")
                self.horizontalSpacer_44 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_28.addItem(self.horizontalSpacer_44)

                self.label_26 = QLabel(self.frame)
                self.label_26.setObjectName(u"label_26")

                self.horizontalLayout_28.addWidget(self.label_26)

                self.boxPosX = QSpinBox(self.frame)
                self.boxPosX.setObjectName(u"boxPosX")
                self.boxPosX.setMaximumSize(QSize(50, 30))
                self.boxPosX.setMinimum(-999999999)
                self.boxPosX.setMaximum(999999999)
                self.boxPosX.setValue(0)

                self.horizontalLayout_28.addWidget(self.boxPosX)

                self.boxPosY = QSpinBox(self.frame)
                self.boxPosY.setObjectName(u"boxPosY")
                self.boxPosY.setMaximumSize(QSize(50, 30))
                self.boxPosY.setMinimum(-999999999)
                self.boxPosY.setMaximum(999999999)
                self.boxPosY.setValue(0)

                self.horizontalLayout_28.addWidget(self.boxPosY)

                self.horizontalSpacer_58 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_28.addItem(self.horizontalSpacer_58)


                self.verticalLayout_2.addLayout(self.horizontalLayout_28)

                self.horizontalLayout_29 = QHBoxLayout()
                self.horizontalLayout_29.setObjectName(u"horizontalLayout_29")
                self.horizontalSpacer_59 = QSpacerItem(13, 22, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_29.addItem(self.horizontalSpacer_59)

                self.verticalLayout_10 = QVBoxLayout()
                self.verticalLayout_10.setObjectName(u"verticalLayout_10")
                self.label_18 = QLabel(self.frame)
                self.label_18.setObjectName(u"label_18")

                self.verticalLayout_10.addWidget(self.label_18)


                self.horizontalLayout_29.addLayout(self.verticalLayout_10)

                self.boxSeed = QSpinBox(self.frame)
                self.boxSeed.setObjectName(u"boxSeed")
                self.boxSeed.setMaximumSize(QSize(50, 30))
                self.boxSeed.setMinimum(1)
                self.boxSeed.setValue(20)

                self.horizontalLayout_29.addWidget(self.boxSeed)

                self.label_2 = QLabel(self.frame)
                self.label_2.setObjectName(u"label_2")
                font4 = QFont()
                font4.setPointSize(13)
                self.label_2.setFont(font4)

                self.horizontalLayout_29.addWidget(self.label_2)

                self.horizontalSpacer_60 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_29.addItem(self.horizontalSpacer_60)


                self.verticalLayout_2.addLayout(self.horizontalLayout_29)


                self.gridLayout.addLayout(self.verticalLayout_2, 7, 0, 1, 2)

                self.horizontalLayout_2 = QHBoxLayout()
                self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
                self.horizontalSpacer_7 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_2.addItem(self.horizontalSpacer_7)

                self.viewGDS = QPushButton(self.frame)
                self.viewGDS.setObjectName(u"viewGDS")

                self.horizontalLayout_2.addWidget(self.viewGDS)

                self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_2.addItem(self.horizontalSpacer_2)


                self.gridLayout.addLayout(self.horizontalLayout_2, 3, 0, 1, 2)

                self.verticalLayout = QVBoxLayout()
                self.verticalLayout.setObjectName(u"verticalLayout")
                self.horizontalLayout_13 = QHBoxLayout()
                self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
                self.horizontalSpacer_31 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_13.addItem(self.horizontalSpacer_31)

                self.label_9 = QLabel(self.frame)
                self.label_9.setObjectName(u"label_9")
                font5 = QFont()
                font5.setPointSize(12)
                font5.setBold(True)
                font5.setUnderline(False)
                font5.setWeight(75)
                font5.setKerning(True)
                self.label_9.setFont(font5)

                self.horizontalLayout_13.addWidget(self.label_9)

                self.horizontalSpacer_30 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_13.addItem(self.horizontalSpacer_30)


                self.verticalLayout.addLayout(self.horizontalLayout_13)

                self.horizontalLayout = QHBoxLayout()
                self.horizontalLayout.setObjectName(u"horizontalLayout")
                self.horizontalSpacer_20 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout.addItem(self.horizontalSpacer_20)

                self.label_4 = QLabel(self.frame)
                self.label_4.setObjectName(u"label_4")
                self.label_4.setMinimumSize(QSize(0, 15))

                self.horizontalLayout.addWidget(self.label_4)

                self.linePool = QLineEdit(self.frame)
                self.linePool.setObjectName(u"linePool")
                self.linePool.setMinimumSize(QSize(0, 15))
                self.linePool.setMaximumSize(QSize(120, 30))
                self.linePool.setLayoutDirection(Qt.LeftToRight)
                self.linePool.setMaxLength(50)
                self.linePool.setAlignment(Qt.AlignCenter)

                self.horizontalLayout.addWidget(self.linePool)

                self.horizontalSpacer_19 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout.addItem(self.horizontalSpacer_19)


                self.verticalLayout.addLayout(self.horizontalLayout)

                self.horizontalLayout_9 = QHBoxLayout()
                self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
                self.horizontalSpacer_21 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_9.addItem(self.horizontalSpacer_21)

                self.label_5 = QLabel(self.frame)
                self.label_5.setObjectName(u"label_5")

                self.horizontalLayout_9.addWidget(self.label_5)

                self.lineClass = QLineEdit(self.frame)
                self.lineClass.setObjectName(u"lineClass")
                self.lineClass.setMinimumSize(QSize(0, 15))
                self.lineClass.setMaximumSize(QSize(120, 30))
                self.lineClass.setFont(font)
                self.lineClass.setMaxLength(50)
                self.lineClass.setAlignment(Qt.AlignCenter)

                self.horizontalLayout_9.addWidget(self.lineClass)

                self.horizontalSpacer_22 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_9.addItem(self.horizontalSpacer_22)


                self.verticalLayout.addLayout(self.horizontalLayout_9)

                self.horizontalLayout_10 = QHBoxLayout()
                self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
                self.horizontalSpacer_23 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_10.addItem(self.horizontalSpacer_23)

                self.label_6 = QLabel(self.frame)
                self.label_6.setObjectName(u"label_6")

                self.horizontalLayout_10.addWidget(self.label_6)

                self.lineQueue = QLineEdit(self.frame)
                self.lineQueue.setObjectName(u"lineQueue")
                self.lineQueue.setMinimumSize(QSize(0, 15))
                self.lineQueue.setMaximumSize(QSize(120, 30))
                self.lineQueue.setMaxLength(50)
                self.lineQueue.setAlignment(Qt.AlignCenter)

                self.horizontalLayout_10.addWidget(self.lineQueue)

                self.horizontalSpacer_24 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_10.addItem(self.horizontalSpacer_24)


                self.verticalLayout.addLayout(self.horizontalLayout_10)

                self.horizontalLayout_11 = QHBoxLayout()
                self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
                self.horizontalSpacer_25 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_11.addItem(self.horizontalSpacer_25)

                self.label_7 = QLabel(self.frame)
                self.label_7.setObjectName(u"label_7")

                self.horizontalLayout_11.addWidget(self.label_7)

                self.boxSlots = QSpinBox(self.frame)
                self.boxSlots.setObjectName(u"boxSlots")
                self.boxSlots.setMinimumSize(QSize(0, 15))
                self.boxSlots.setMaximumSize(QSize(50, 30))
                self.boxSlots.setMinimum(1)
                self.boxSlots.setMaximum(20)
                self.boxSlots.setValue(4)

                self.horizontalLayout_11.addWidget(self.boxSlots)

                self.horizontalSpacer_27 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_11.addItem(self.horizontalSpacer_27)

                self.label_8 = QLabel(self.frame)
                self.label_8.setObjectName(u"label_8")

                self.horizontalLayout_11.addWidget(self.label_8)

                self.boxHosts = QSpinBox(self.frame)
                self.boxHosts.setObjectName(u"boxHosts")
                self.boxHosts.setMinimumSize(QSize(0, 15))
                self.boxHosts.setMaximumSize(QSize(50, 30))
                self.boxHosts.setMinimum(1)
                self.boxHosts.setMaximum(20)
                self.boxHosts.setValue(4)

                self.horizontalLayout_11.addWidget(self.boxHosts)

                self.horizontalSpacer_26 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_11.addItem(self.horizontalSpacer_26)


                self.verticalLayout.addLayout(self.horizontalLayout_11)

                self.horizontalLayout_12 = QHBoxLayout()
                self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
                self.horizontalSpacer_28 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_12.addItem(self.horizontalSpacer_28)

                self.checkEmail = QCheckBox(self.frame)
                self.checkEmail.setObjectName(u"checkEmail")
                self.checkEmail.setMaximumSize(QSize(16777215, 30))

                self.horizontalLayout_12.addWidget(self.checkEmail)

                self.horizontalSpacer_29 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_12.addItem(self.horizontalSpacer_29)


                self.verticalLayout.addLayout(self.horizontalLayout_12)


                self.gridLayout.addLayout(self.verticalLayout, 9, 0, 1, 2)

                self.label = QLabel(self.frame)
                self.label.setObjectName(u"label")
                font6 = QFont()
                font6.setPointSize(14)
                font6.setBold(True)
                font6.setUnderline(True)
                font6.setWeight(75)
                self.label.setFont(font6)
                self.label.setAlignment(Qt.AlignCenter)

                self.gridLayout.addWidget(self.label, 0, 0, 1, 1)

                self.horizontalSpacer = QSpacerItem(40, 15, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.gridLayout.addItem(self.horizontalSpacer, 1, 0, 1, 1)

                self.horizontalSpacer_62 = QSpacerItem(40, 10, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.gridLayout.addItem(self.horizontalSpacer_62, 6, 0, 1, 1)

                self.verticalLayout_6 = QVBoxLayout()
                self.verticalLayout_6.setObjectName(u"verticalLayout_6")
                self.horizontalLayout_22 = QHBoxLayout()
                self.horizontalLayout_22.setObjectName(u"horizontalLayout_22")
                self.horizontalSpacer_51 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_22.addItem(self.horizontalSpacer_51)

                self.label_24 = QLabel(self.frame)
                self.label_24.setObjectName(u"label_24")
                self.label_24.setFont(font2)

                self.horizontalLayout_22.addWidget(self.label_24)

                self.horizontalSpacer_52 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_22.addItem(self.horizontalSpacer_52)


                self.verticalLayout_6.addLayout(self.horizontalLayout_22)

                self.horizontalLayout_23 = QHBoxLayout()
                self.horizontalLayout_23.setSpacing(0)
                self.horizontalLayout_23.setObjectName(u"horizontalLayout_23")
                self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_23.addItem(self.horizontalSpacer_4)

                self.lineGDS = QLineEdit(self.frame)
                self.lineGDS.setObjectName(u"lineGDS")
                self.lineGDS.setMaximumSize(QSize(150, 30))

                self.horizontalLayout_23.addWidget(self.lineGDS)

                self.pushGDS = QToolButton(self.frame)
                self.pushGDS.setObjectName(u"pushGDS")
                self.pushGDS.setMaximumSize(QSize(130, 30))

                self.horizontalLayout_23.addWidget(self.pushGDS)

                self.horizontalSpacer_5 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_23.addItem(self.horizontalSpacer_5)


                self.verticalLayout_6.addLayout(self.horizontalLayout_23)

                self.horizontalLayout_24 = QHBoxLayout()
                self.horizontalLayout_24.setObjectName(u"horizontalLayout_24")
                self.horizontalSpacer_54 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_24.addItem(self.horizontalSpacer_54)

                self.label_13 = QLabel(self.frame)
                self.label_13.setObjectName(u"label_13")

                self.horizontalLayout_24.addWidget(self.label_13)

                self.boxL = QSpinBox(self.frame)
                self.boxL.setObjectName(u"boxL")
                self.boxL.setMaximumSize(QSize(55, 30))
                self.boxL.setMaximum(255)
                self.boxL.setValue(5)

                self.horizontalLayout_24.addWidget(self.boxL)

                self.label_14 = QLabel(self.frame)
                self.label_14.setObjectName(u"label_14")

                self.horizontalLayout_24.addWidget(self.label_14)

                self.boxD = QSpinBox(self.frame)
                self.boxD.setObjectName(u"boxD")
                self.boxD.setMaximumSize(QSize(55, 30))
                self.boxD.setMaximum(255)
                self.boxD.setValue(81)

                self.horizontalLayout_24.addWidget(self.boxD)

                self.horizontalSpacer_55 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_24.addItem(self.horizontalSpacer_55)


                self.verticalLayout_6.addLayout(self.horizontalLayout_24)

                self.horizontalLayout_25 = QHBoxLayout()
                self.horizontalLayout_25.setObjectName(u"horizontalLayout_25")
                self.horizontalSpacer_56 = QSpacerItem(80, 20, QSizePolicy.Fixed, QSizePolicy.Minimum)

                self.horizontalLayout_25.addItem(self.horizontalSpacer_56)

                self.label_15 = QLabel(self.frame)
                self.label_15.setObjectName(u"label_15")

                self.horizontalLayout_25.addWidget(self.label_15)

                self.horizontalLayout_26 = QHBoxLayout()
                self.horizontalLayout_26.setObjectName(u"horizontalLayout_26")
                self.radioTP = QRadioButton(self.frame)
                self.radioTP.setObjectName(u"radioTP")
                self.radioTP.setChecked(True)

                self.horizontalLayout_26.addWidget(self.radioTP)

                self.radioTN = QRadioButton(self.frame)
                self.radioTN.setObjectName(u"radioTN")

                self.horizontalLayout_26.addWidget(self.radioTN)

                self.horizontalSpacer_57 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_26.addItem(self.horizontalSpacer_57)


                self.horizontalLayout_25.addLayout(self.horizontalLayout_26)


                self.verticalLayout_6.addLayout(self.horizontalLayout_25)


                self.gridLayout.addLayout(self.verticalLayout_6, 2, 0, 1, 2)


                self.formLayout.setWidget(0, QFormLayout.LabelRole, self.frame)

                self.verticalLayout_8 = QVBoxLayout()
                self.verticalLayout_8.setSpacing(4)
                self.verticalLayout_8.setObjectName(u"verticalLayout_8")
                self.horizontalLayout_8 = QHBoxLayout()
                self.horizontalLayout_8.setSpacing(0)
                self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
                self.textBrowser = QTextBrowser(self.centralwidget)
                self.textBrowser.setObjectName(u"textBrowser")
                self.textBrowser.setMaximumSize(QSize(1400, 35))

                self.horizontalLayout_8.addWidget(self.textBrowser)

                self.pushImage = QPushButton(self.centralwidget)
                self.pushImage.setObjectName(u"pushImage")
                self.pushImage.setMaximumSize(QSize(100, 35))

                self.horizontalLayout_8.addWidget(self.pushImage)


                self.verticalLayout_8.addLayout(self.horizontalLayout_8)

                self.graphicsView = QGraphicsView(self.centralwidget)
                self.graphicsView.setObjectName(u"graphicsView")
                self.graphicsView.setMinimumSize(QSize(0, 300))
                self.graphicsView.setMaximumSize(QSize(1500, 1001))
                font7 = QFont()
                font7.setPointSize(12)
                font7.setKerning(True)
                self.graphicsView.setFont(font7)

                self.verticalLayout_8.addWidget(self.graphicsView)

                self.console = QTextEdit(self.centralwidget)
                self.console.setObjectName(u"console")
                self.console.setMinimumSize(QSize(0, 300))

                self.verticalLayout_8.addWidget(self.console)

                self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.verticalLayout_8.addItem(self.horizontalSpacer_3)


                self.formLayout.setLayout(0, QFormLayout.FieldRole, self.verticalLayout_8)

                self.horizontalLayout_7 = QHBoxLayout()
                self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
                self.horizontalSpacer_6 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_6)

                self.pushImport = QPushButton(self.centralwidget)
                self.pushImport.setObjectName(u"pushImport")
                sizePolicy = QSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
                sizePolicy.setHorizontalStretch(0)
                sizePolicy.setVerticalStretch(0)
                sizePolicy.setHeightForWidth(self.pushImport.sizePolicy().hasHeightForWidth())
                self.pushImport.setSizePolicy(sizePolicy)
                self.pushImport.setMinimumSize(QSize(0, 35))
                self.pushImport.setMaximumSize(QSize(80, 35))
                self.pushImport.setFont(font1)
                self.pushImport.setToolTipDuration(-1)
                self.pushImport.setLayoutDirection(Qt.LeftToRight)
                self.pushImport.setStyleSheet(u"QPushButton {\n"
                                              "color: blue}")
                self.pushImport.setFlat(False)

                self.horizontalLayout_7.addWidget(self.pushImport)

                self.horizontalSpacer_49 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_49)

                self.pushInspect = QPushButton(self.centralwidget)
                self.pushInspect.setObjectName(u"pushInspect")
                sizePolicy1 = QSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)
                sizePolicy1.setHorizontalStretch(0)
                sizePolicy1.setVerticalStretch(0)
                sizePolicy1.setHeightForWidth(self.pushInspect.sizePolicy().hasHeightForWidth())
                self.pushInspect.setSizePolicy(sizePolicy1)
                self.pushInspect.setMinimumSize(QSize(0, 35))
                self.pushInspect.setMaximumSize(QSize(80, 35))
                font8 = QFont()
                font8.setPointSize(12)
                font8.setBold(False)
                font8.setWeight(50)
                self.pushInspect.setFont(font8)
                self.pushInspect.setStyleSheet(u"QPushButton {\n"
                                               "color: maroon\n"
                                               "}")

                self.horizontalLayout_7.addWidget(self.pushInspect)

                self.horizontalSpacer_13 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_13)

                self.pushRun = QPushButton(self.centralwidget)
                self.pushRun.setObjectName(u"pushRun")
                sizePolicy.setHeightForWidth(self.pushRun.sizePolicy().hasHeightForWidth())
                self.pushRun.setSizePolicy(sizePolicy)
                self.pushRun.setMinimumSize(QSize(0, 35))
                self.pushRun.setMaximumSize(QSize(80, 35))
                self.pushRun.setFont(font1)
                self.pushRun.setStyleSheet(u"QPushButton {\n"
                                           "color: green\n"
                                           "}")

                self.horizontalLayout_7.addWidget(self.pushRun)

                self.horizontalSpacer_12 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_12)

                self.pushAbort = QPushButton(self.centralwidget)
                self.pushAbort.setObjectName(u"pushAbort")
                sizePolicy.setHeightForWidth(self.pushAbort.sizePolicy().hasHeightForWidth())
                self.pushAbort.setSizePolicy(sizePolicy)
                self.pushAbort.setMinimumSize(QSize(0, 35))
                self.pushAbort.setMaximumSize(QSize(80, 35))
                self.pushAbort.setFont(font1)
                self.pushAbort.setStyleSheet(u"QPushButton {\n"
                                             "color: red}")

                self.horizontalLayout_7.addWidget(self.pushAbort)

                self.horizontalSpacer_48 = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_48)

                self.pushQuit = QPushButton(self.centralwidget)
                self.pushQuit.setObjectName(u"pushQuit")
                self.pushQuit.setMinimumSize(QSize(0, 35))
                self.pushQuit.setMaximumSize(QSize(80, 35))
                self.pushQuit.setFont(font1)

                self.horizontalLayout_7.addWidget(self.pushQuit)

                self.horizontalSpacer_50 = QSpacerItem(40, 20, QSizePolicy.Maximum, QSizePolicy.Minimum)

                self.horizontalLayout_7.addItem(self.horizontalSpacer_50)


                self.formLayout.setLayout(1, QFormLayout.SpanningRole, self.horizontalLayout_7)

                RBDS.setCentralWidget(self.centralwidget)
                #if QT_CONFIG(shortcut)
                self.label_18.setBuddy(self.boxL)
                self.label_13.setBuddy(self.boxPosX)
                #endif // QT_CONFIG(shortcut)

                self.retranslateUi(RBDS)

                QMetaObject.connectSlotsByName(RBDS)
        # setupUi

        def retranslateUi(self, RBDS):
                RBDS.setWindowTitle(QCoreApplication.translate("RBDS", u"RBDS", None))
                self.label_11.setText(QCoreApplication.translate("RBDS", u"Heat Transfer Model Settings", None))
                self.label_10.setText(QCoreApplication.translate("RBDS", u"Thermal Diffusivity ", None))
                self.boxAlpha.setText(QCoreApplication.translate("RBDS", u"1", None))
                self.label_21.setText(QCoreApplication.translate("RBDS", u"Grid-size [X,Y,Z] nm ", None))
                self.checkGenCtrl.setText(QCoreApplication.translate("RBDS", u"Generate defect-free intensities", None))
                self.label_25.setText(QCoreApplication.translate("RBDS", u"Defect Settings", None))
                self.label_27.setText(QCoreApplication.translate("RBDS", u"Defect Size [X,Y,Z] nm ", None))
                self.label_26.setText(QCoreApplication.translate("RBDS", u"Location [X,Y] (in nm w.r.t. Center) ", None))
                self.label_18.setText(QCoreApplication.translate("RBDS", u"Seed Layer Location (substrate at 0%)", None))
                self.label_2.setText(QCoreApplication.translate("RBDS", u"%", None))
                #if QT_CONFIG(tooltip)
                self.viewGDS.setToolTip(QCoreApplication.translate("RBDS", u"Ctrl+G", None))
                #endif // QT_CONFIG(tooltip)
                self.viewGDS.setText(QCoreApplication.translate("RBDS", u"View GDS File with Defect", None))
                self.label_9.setText(QCoreApplication.translate("RBDS", u"MPI Settings", None))
                self.label_4.setText(QCoreApplication.translate("RBDS", u"Pool ", None))
                self.linePool.setText(QCoreApplication.translate("RBDS", u"orto_e_1", None))
                self.linePool.setPlaceholderText(QCoreApplication.translate("RBDS", u"orto_e_1", None))
                self.label_5.setText(QCoreApplication.translate("RBDS", u"Class ", None))
                self.lineClass.setText(QCoreApplication.translate("RBDS", u"SLES12_ALL", None))
                self.lineClass.setPlaceholderText(QCoreApplication.translate("RBDS", u"SLES12_ALL", None))
                self.label_6.setText(QCoreApplication.translate("RBDS", u"Queue ", None))
                self.lineQueue.setText(QCoreApplication.translate("RBDS", u"/ito/clg/1", None))
                self.lineQueue.setPlaceholderText(QCoreApplication.translate("RBDS", u"/ito/clg/1", None))
                self.label_7.setText(QCoreApplication.translate("RBDS", u"Slots ", None))
                self.label_8.setText(QCoreApplication.translate("RBDS", u"Hosts ", None))
                #if QT_CONFIG(tooltip)
                self.checkEmail.setToolTip(QCoreApplication.translate("RBDS", u"Recipient: user@org.com", None))
                #endif // QT_CONFIG(tooltip)
                self.checkEmail.setText(QCoreApplication.translate("RBDS", u"E-mail alert after job completion", None))
                self.label.setText(QCoreApplication.translate("RBDS", u"DOE Parameters & Settings", None))
                self.label_24.setText(QCoreApplication.translate("RBDS", u"Layout Settings", None))
                self.lineGDS.setPlaceholderText(QCoreApplication.translate("RBDS", u"<Full Real Path>", None))
                #if QT_CONFIG(tooltip)
                self.pushGDS.setToolTip(QCoreApplication.translate("RBDS", u"Browse GDS file (Ctrl+O)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushGDS.setText(QCoreApplication.translate("RBDS", u"Upload GDS file", None))
                self.label_13.setText(QCoreApplication.translate("RBDS", u"Layer ID ", None))
                self.label_14.setText(QCoreApplication.translate("RBDS", u":", None))
                self.label_15.setText(QCoreApplication.translate("RBDS", u"Resist Tone ", None))
                self.radioTP.setText(QCoreApplication.translate("RBDS", u"Positive", None))
                self.radioTN.setText(QCoreApplication.translate("RBDS", u"Negative", None))
                self.pushImage.setText(QCoreApplication.translate("RBDS", u"Image File", None))
                #if QT_CONFIG(tooltip)
                self.pushImport.setToolTip(QCoreApplication.translate("RBDS", u"Load configuration file (Ctrl+I)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushImport.setText(QCoreApplication.translate("RBDS", u"IMPORT", None))
                #if QT_CONFIG(tooltip)
                self.pushInspect.setToolTip(QCoreApplication.translate("RBDS", u"Inspect configuration before launching (Ctrl+N)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushInspect.setText(QCoreApplication.translate("RBDS", u"INSPECT", None))
                #if QT_CONFIG(tooltip)
                self.pushRun.setToolTip(QCoreApplication.translate("RBDS", u"Launch jobs (Ctrl+R)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushRun.setText(QCoreApplication.translate("RBDS", u"RUN", None))
                #if QT_CONFIG(tooltip)
                self.pushAbort.setToolTip(QCoreApplication.translate("RBDS", u"Kill a job (Ctrl+K)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushAbort.setText(QCoreApplication.translate("RBDS", u"ABORT", None))
                #if QT_CONFIG(tooltip)
                self.pushQuit.setToolTip(QCoreApplication.translate("RBDS", u"Kill all jobs (Ctrl+Q)", None))
                #endif // QT_CONFIG(tooltip)
                self.pushQuit.setText(QCoreApplication.translate("RBDS", u"QUIT", None))
        # retranslateUi

