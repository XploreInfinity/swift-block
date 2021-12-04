from PyQt6 import QtWidgets,uic
import sys
import ipaddress
class RuleEdit(QtWidgets.QWidget):
    def __init__(self,scriptPath,title,mode):
        super().__init__()
        uic.loadUi(scriptPath+'/ui/ruleEdit.ui',self)
        self.ruleEditTitle_lbl.setText(title)
        self.ruleEditTitle_lbl.setStyleSheet("font-weight:bold;")
        self.setWindowTitle(title)
        self.UInBehaviourConfig(mode)
        self.show()
    
    def showStatus_lbl(self,message,lbl,success=False):
        if success:
            lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
        else:
            lbl.setStyleSheet("color:white;background-color:crimson;font-weight:bold")
        lbl.setText(message)
        lbl.show()

    def UInBehaviourConfig(self,mode):
        if mode=="add":
            self.saveRule_btn.clicked.connect(self.addRuleBtnClicked)

    def addRuleBtnClicked(self):
        ip=self.ip_tf.text()
        hostname=self.hostname_tf.text()
        if ip=="" or hostname=="":
            self.showStatus_lbl("Please fill both the fields!",self.status_lbl)
        else:
            try:
                ip=ipaddress.ip_address(ip)
    
            except ValueError:
                self.showStatus_lbl("IPv4 is invalid!",self.status_lbl)
    def editRuleBtnClicked(self):
        pass
    def cancelBtnClicked(self):
        self=None
