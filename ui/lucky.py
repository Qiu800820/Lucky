# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'lucky.ui'
#
# Created by: PyQt5 UI code generator 5.10
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_Lucky(object):
    def setupUi(self, Lucky):
        Lucky.setObjectName("Lucky")
        Lucky.resize(800, 800)
        Lucky.setMinimumSize(QtCore.QSize(800, 600))
        Lucky.setMaximumSize(QtCore.QSize(800, 800))
        self.centralwidget = QtWidgets.QWidget(Lucky)
        self.centralwidget.setObjectName("centralwidget")
        self.answer_table = QtWidgets.QTableWidget(self.centralwidget)
        self.answer_table.setGeometry(QtCore.QRect(5, 5, 230, 790))
        self.answer_table.setMinimumSize(QtCore.QSize(230, 590))
        self.answer_table.setMaximumSize(QtCore.QSize(230, 790))
        self.answer_table.setObjectName("answer_table")
        self.answer_table.setColumnCount(2)
        self.answer_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        item.setText("期号")
        item.setBackground(QtGui.QColor(240, 229, 189))
        brush = QtGui.QBrush(QtGui.QColor(0, 0, 0))
        brush.setStyle(QtCore.Qt.SolidPattern)
        item.setForeground(brush)
        self.answer_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.answer_table.setHorizontalHeaderItem(1, item)
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(250, 180, 531, 31))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.refresh = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.refresh.setObjectName("refresh")
        self.horizontalLayout.addWidget(self.refresh)
        self.statistics = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        self.statistics.setObjectName("statistics")
        self.horizontalLayout.addWidget(self.statistics)
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(250, 240, 54, 12))
        self.label.setObjectName("label")
        self.result_table = QtWidgets.QTableWidget(self.centralwidget)
        self.result_table.setGeometry(QtCore.QRect(250, 270, 531, 211))
        self.result_table.setObjectName("result_table")
        self.result_table.setColumnCount(4)
        self.result_table.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.result_table.setHorizontalHeaderItem(3, item)
        self.lucky = QtWidgets.QPushButton(self.centralwidget)
        self.lucky.setGeometry(QtCore.QRect(260, 500, 511, 23))
        self.lucky.setObjectName("lucky")
        self.result_edit = QtWidgets.QTextEdit(self.centralwidget)
        self.result_edit.setGeometry(QtCore.QRect(250, 540, 531, 201))
        self.result_edit.setObjectName("result_edit")
        self.count = QtWidgets.QLabel(self.centralwidget)
        self.count.setGeometry(QtCore.QRect(370, 240, 54, 12))
        self.count.setObjectName("count")
        self.label_3 = QtWidgets.QLabel(self.centralwidget)
        self.label_3.setGeometry(QtCore.QRect(310, 240, 54, 12))
        self.label_3.setObjectName("label_3")
        self.label_4 = QtWidgets.QLabel(self.centralwidget)
        self.label_4.setGeometry(QtCore.QRect(260, 30, 54, 12))
        self.label_4.setObjectName("label_4")
        self.layoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget.setGeometry(QtCore.QRect(330, 20, 381, 18))
        self.layoutWidget.setObjectName("layoutWidget")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.layoutWidget)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.checkBox = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox.setChecked(True)
        self.checkBox.setObjectName("checkBox")
        self.horizontalLayout_2.addWidget(self.checkBox)
        self.checkBox_2 = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.horizontalLayout_2.addWidget(self.checkBox_2)
        self.checkBox_3 = QtWidgets.QCheckBox(self.layoutWidget)
        self.checkBox_3.setObjectName("checkBox_3")
        self.horizontalLayout_2.addWidget(self.checkBox_3)
        self.layoutWidget1 = QtWidgets.QWidget(self.centralwidget)
        self.layoutWidget1.setGeometry(QtCore.QRect(330, 50, 381, 18))
        self.layoutWidget1.setObjectName("layoutWidget1")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.layoutWidget1)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.checkBox_6 = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_6.setObjectName("checkBox_6")
        self.horizontalLayout_3.addWidget(self.checkBox_6)
        self.checkBox_7 = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_7.setObjectName("checkBox_7")
        self.horizontalLayout_3.addWidget(self.checkBox_7)
        self.checkBox_8 = QtWidgets.QCheckBox(self.layoutWidget1)
        self.checkBox_8.setChecked(False)
        self.checkBox_8.setObjectName("checkBox_8")
        self.horizontalLayout_3.addWidget(self.checkBox_8)
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(260, 92, 54, 20))
        self.label_2.setObjectName("label_2")
        self.spinBox = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox.setGeometry(QtCore.QRect(320, 90, 42, 22))
        self.spinBox.setMinimum(1)
        self.spinBox.setMaximum(200)
        self.spinBox.setProperty("value", 120)
        self.spinBox.setObjectName("spinBox")
        self.label_5 = QtWidgets.QLabel(self.centralwidget)
        self.label_5.setGeometry(QtCore.QRect(390, 92, 54, 20))
        self.label_5.setObjectName("label_5")
        self.spinBox_2 = QtWidgets.QSpinBox(self.centralwidget)
        self.spinBox_2.setGeometry(QtCore.QRect(430, 90, 42, 22))
        self.spinBox_2.setMinimum(1)
        self.spinBox_2.setMaximum(1000)
        self.spinBox_2.setProperty("value", 100)
        self.spinBox_2.setObjectName("spinBox_2")
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(260, 140, 54, 21))
        self.label_6.setObjectName("label_6")
        self.horizontalSlider = QtWidgets.QSlider(self.centralwidget)
        self.horizontalSlider.setGeometry(QtCore.QRect(310, 140, 160, 22))
        self.horizontalSlider.setMinimum(30)
        self.horizontalSlider.setMaximum(80)
        self.horizontalSlider.setOrientation(QtCore.Qt.Horizontal)
        self.horizontalSlider.setObjectName("horizontalSlider")
        self.lcdNumber = QtWidgets.QLCDNumber(self.centralwidget)
        self.lcdNumber.setGeometry(QtCore.QRect(480, 140, 64, 21))
        self.lcdNumber.setSegmentStyle(QtWidgets.QLCDNumber.Flat)
        self.lcdNumber.setProperty("value", 30.0)
        self.lcdNumber.setObjectName("lcdNumber")
        self.lucky_2 = QtWidgets.QPushButton(self.centralwidget)
        self.lucky_2.setGeometry(QtCore.QRect(260, 760, 511, 23))
        self.lucky_2.setObjectName("lucky_2")
        Lucky.setCentralWidget(self.centralwidget)

        self.retranslateUi(Lucky)
        QtCore.QMetaObject.connectSlotsByName(Lucky)

    def retranslateUi(self, Lucky):
        _translate = QtCore.QCoreApplication.translate
        Lucky.setWindowTitle(_translate("Lucky", "Lucky"))
        item = self.answer_table.horizontalHeaderItem(1)
        item.setText(_translate("Lucky", "开奖号码"))
        self.refresh.setText(_translate("Lucky", "刷新开奖结果"))
        self.statistics.setText(_translate("Lucky", "重新计算"))
        self.label.setText(_translate("Lucky", "计算结果："))
        item = self.result_table.horizontalHeaderItem(0)
        item.setText(_translate("Lucky", "位置"))
        item = self.result_table.horizontalHeaderItem(1)
        item.setText(_translate("Lucky", "组合数"))
        item = self.result_table.horizontalHeaderItem(2)
        item.setText(_translate("Lucky", "组合偏差下降数"))
        item = self.result_table.horizontalHeaderItem(3)
        item.setText(_translate("Lucky", "组合偏差下降率"))
        self.lucky.setText(_translate("Lucky", "生成数据"))
        self.count.setText(_translate("Lucky", "条数据"))
        self.label_3.setText(_translate("Lucky", "0"))
        self.label_4.setText(_translate("Lucky", "组合位置："))
        self.checkBox.setText(_translate("Lucky", "12XX"))
        self.checkBox_2.setText(_translate("Lucky", "1X3X"))
        self.checkBox_3.setText(_translate("Lucky", "1XX4"))
        self.checkBox_6.setText(_translate("Lucky", "X2X4"))
        self.checkBox_7.setText(_translate("Lucky", "X23X"))
        self.checkBox_8.setText(_translate("Lucky", "XX34"))
        self.label_2.setText(_translate("Lucky", "周期大小"))
        self.label_5.setText(_translate("Lucky", "周期数"))
        self.label_6.setText(_translate("Lucky", "组合数"))
        self.lucky_2.setText(_translate("Lucky", "模拟盈利结果"))

