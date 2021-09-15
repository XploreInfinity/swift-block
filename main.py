from PyQt6 import QtWidgets,uic
import sys,get_hosts
class Ui(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        #*load the ui file
        uic.loadUi('adblock.ui',self)
        #*init the library for interacting with host sources,etc...
        #!WARNING:This changes the current directory
        self.parser=get_hosts.Parser()

        #*GLOBAL VARIABLES DECLARATION:
        self.editMode=True #*controls whether the source editing form is set to edit source mode or add source mode
        self.selectedSource=''#*Will store QListWidgetItem that is currently selected by the user
        self.customLst=''#*stores contents of user's custom list
        self.allowLst=''#*stores contents of user's allow list
        self.SignalSlotConfig()
        self.show()

        self.reconf_ui()

    def reconf_ui(self):
        #*Reconfig for the sources tab:
        self.loadSrcData()
        self.sourcesForm_widget.setDisabled(True)
        self.sourceDelete_btn.setDisabled(True)
        self.editMode_lbl.hide()
        self.formStatus_lbl.hide()
        self.sourceName_tf.setPlaceholderText("Unqiue nickname for the source")
        self.sourceURL_tf.setPlaceholderText("Unique URL of the source")

        #*Reconfig for the custom list tab:
        self.loadCustomLst()
        self.customSave_btn.setDisabled(True)
        self.customCancel_btn.setDisabled(True)
        self.customStatus_lbl.hide()

        #*Reconfig for the allow list tab:
        self.loadAllowLst()
        self.allowSave_btn.setDisabled(True)
        self.allowCancel_btn.setDisabled(True)
        self.allowStatus_lbl.hide()
    #*Several utility functions that prevent code repetition:
    def err_msg(self,err):
        msg=QtWidgets.QMessageBox()
        msg.setWindowTitle("Error")
        msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        msg.setText("Oops! An error occurred. Additional info is provided below")
        msg.setDetailedText(str(err))
        msg.exec()

    def showStatus_lbl(self,message,lbl,success=False):
        if success:
            lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
        else:
            lbl.setStyleSheet("color:white;background-color:crimson;font-weight:bold")
        lbl.setText(message)
        lbl.show()

    #*fetches and shows user's host sources on the sourcesList:
    def loadSrcData(self):
        self.sourcesList.clear()
        self.selectedSource=None
        sources=self.parser.fetch_sources()
        self.sourceDct={}
        for source in sources:
            self.sourcesList.addItem(source[0])
            self.sourceDct[source[0]]=source[1]
        #*Reset the form and disable said form and the delete btn:
        self.sourceName_tf.setText('')
        self.sourceURL_tf.setText('')
        self.sourcesForm_widget.setDisabled(True)  
        self.sourceDelete_btn.setDisabled(True)

    def loadCustomLst(self):
        self.customLst=self.parser.customlst("customlst")
        self.customLst_edit.setPlainText(self.customLst)
    
    def loadAllowLst(self):
        self.allowLst=self.parser.customlst("allowlst")
        self.allowLst_edit.setPlainText(self.allowLst)
    
    #*A vital function that assigns all widgets handlers(slots) for specific events(signals):
    def SignalSlotConfig(self):
        #*for events occurring in sources tab:
        self.sourcesList.selectionModel().currentChanged.connect(self.sourceSelected)
        self.sourceAdd_btn.clicked.connect(self.addBtnClicked)
        self.sourceDelete_btn.clicked.connect(self.deleteBtnClicked)
        self.sourceSave_btn.clicked.connect(self.sourceSaveBtnClicked)

        #*for events occurring in custom list tab:
        self.customLst_edit.textChanged.connect(self.customLstTextChanged)
        self.customSave_btn.clicked.connect(self.customSaveBtnClicked)
        self.customCancel_btn.clicked.connect(self.customCancelBtnClicked)

        #*for events occurring in allow list tab:
        self.allowLst_edit.textChanged.connect(self.allowLstTextChanged)
        self.allowSave_btn.clicked.connect(self.allowSaveBtnClicked)
        self.allowCancel_btn.clicked.connect(self.allowCancelBtnClicked)
        
    
    #*SLOTS FOR EACH SIGNAL BELOW:
    #*slots for the sources tab:
    def sourceSelected(self,current):
        #*Make sure the list isnt empty(which makes selected item None type)
        if self.sourcesList.currentItem():
            item=self.sourcesList.currentItem().text()
            #*update the value of the selectedSource global var:
            self.selectedSource=item
            self.sourceName_tf.setText(item)
            self.sourceURL_tf.setText(self.sourceDct[item])
            #*Activate the form and show the user that they're now editing a source:
            self.sourcesForm_widget.setDisabled(False)
            self.editMode=True
            self.editMode_lbl.setText("Editing an existing source:")
            self.editMode_lbl.show()
            #*also hide previous status messages and enable the delete btn:
            self.formStatus_lbl.hide()
            self.sourceDelete_btn.setDisabled(False)

    def addBtnClicked(self):
        #*Clear(and enable if disabled) the form and change the editMode to add mode:
        self.sourcesForm_widget.setDisabled(False)
        self.editMode_lbl.show()
        self.sourceName_tf.setText('')
        self.sourceURL_tf.setText('')
        self.editMode=False
        self.editMode_lbl.setText("Adding a new source:")

    def deleteBtnClicked(self):
        #*ensure that a source from the list is selected,warn the user otherwise:    
        if not self.selectedSource:
            self.showStatus_lbl("Select a source from the list first!",self.formStatus_lbl)
        else:
            #*Ask the user if they really want to delete the source
            question=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question,"Please Confirm","Are you sure you want to delete this source?",(QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No))
            confirm=question.exec()
            if confirm==QtWidgets.QMessageBox.StandardButton.Yes:
                self.sourceDelete_btn.setDisabled(True)
                try:
                    self.parser.del_source(self.selectedSource)
                    self.loadSrcData()
                    self.showStatus_lbl("Deleted source successfully!",self.formStatus_lbl,True)
                except Exception as err:
                    self.err_msg(err)
                    self.showStatus_lbl("Oops! An error occurred",self.formStatus_lbl)
                self.sourceDelete_btn.setDisabled(True)
    
    def sourceSaveBtnClicked(self):
        srcName=self.sourceName_tf.text()
        srcURL=self.sourceURL_tf.text()
        if(srcName=="" or srcURL==""):
            self.formStatus_lbl.setStyleSheet("color:white;background-color:crimson;font-weight:bold")
            self.formStatus_lbl.setText("Fields can't be empty!")
            self.formStatus_lbl.show()
        #*ensure that a source from the list is selected,warn the user otherwise:    
        elif not self.selectedSource and self.editMode:
            self.showStatus_lbl("Select a source from the list first!",self.formStatus_lbl)
        else:
            #*Save button disabled to prevent multiple save attempts at once
            self.sourceSave_btn.setDisabled(True)
            
            if self.editMode:
                
                try:
                    self.parser.edit_source(self.selectedSource,srcName,srcURL)
                    self.loadSrcData()
                    self.showStatus_lbl("Edited source successfully!",self.formStatus_lbl,True)
                except Exception as err:
                    self.err_msg(err)
                    self.showStatus_lbl("Oops! An error occurred",self.formStatus_lbl)
                    #*calling this here incase the editing of the source succeeded but something else failed:(which would effectively make existing sourceList entries old and obsolete) 
                    self.loadSrcData()
                
            
            else:
                try:
                    self.parser.add_source(srcName,srcURL)
                    self.loadSrcData()
                    self.showStatus_lbl("Added source successfully!",self.formStatus_lbl,True)
                except Exception as err:
                    self.err_msg(err)
                    self.showStatus_lbl("Oops! An error occurred",self.formStatus_lbl)
                    #*calling this here incase the adding of the source succeeded but something else failed:(which would effectively make existing sourceList entries old and obsolete) 
                    self.loadSrcData()
                
            #*re-enable the save btn
            self.sourceSave_btn.setDisabled(False)
    

    #*Slots for custom list tab:
    def customLstTextChanged(self):
        self.customSave_btn.setDisabled(False)
        self.customCancel_btn.setDisabled(False)

    def customSaveBtnClicked(self):
        self.customSave_btn.setDisabled(True)
        try:
            self.parser.customlst("customlst",self.customLst_edit.toPlainText())
            self.loadCustomLst()
            self.showStatus_lbl("Saved and applied successfully!",self.customStatus_lbl,True)
            self.customSave_btn.setDisabled(True)
            self.customCancel_btn.setDisabled(True)
        except Exception as err:
            self.err_msg(err)
            self.showStatus_lbl("Oops! An error occurred",self.customStatus_lbl)
            self.customSave_btn.setDisabled(False)
            
    def customCancelBtnClicked(self):
        print("This:",self.customLst)
        self.customLst_edit.setPlainText(self.customLst)
        self.customSave_btn.setDisabled(False)
        self.customCancel_btn.setDisabled(True)


    #*Slots for the allow list tab:
    def allowLstTextChanged(self):
        self.allowSave_btn.setDisabled(False)
        self.allowCancel_btn.setDisabled(False)

    def allowSaveBtnClicked(self):
        self.allowSave_btn.setDisabled(True)
        try:
            self.parser.customlst("allowlst",self.allowLst_edit.toPlainText())
            self.loadAllowLst()
            self.showStatus_lbl("Saved and applied successfully!",self.allowStatus_lbl,True)
            self.allowSave_btn.setDisabled(True)
            self.allowCancel_btn.setDisabled(True)
        except Exception as err:
            self.err_msg(err)
            self.showStatus_lbl("Oops! An error occurred",self.allowStatus_lbl)
            self.allowSave_btn.setDisabled(False)
            
    def allowCancelBtnClicked(self):
        print("This:",self.allowLst)
        self.allowLst_edit.setPlainText(self.allowLst)
        self.allowSave_btn.setDisabled(True)
        self.allowCancel_btn.setDisabled(True)

app=QtWidgets.QApplication(sys.argv)
ui=Ui()
sys.exit(app.exec())