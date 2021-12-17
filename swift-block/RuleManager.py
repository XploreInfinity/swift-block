from PyQt6 import QtWidgets,QtGui,QtCore,uic
import os,sys,Parser
class RuleManager(QtWidgets.QWidget):
    def __init__(self,scriptPath):
        super().__init__()
        #*load the ui file
        uic.loadUi(scriptPath+'/ui/filters.ui',self)
        self.setWindowTitle("Rule Manager- Swiftblock")
        #*GLOBAL VARIABLES DECLARATION:
        self.scriptPath=scriptPath #*The path from which the app(or script) was executed
        self.SignalSlotConfig()
        self.sourceBlocked=[] #*Stores hostnames blocked by hosts file sources
        self.blocked=[] #*Stores hostnames blocked by user
        self.redirected=[] #*Stores rules that redirect a hostname
        self.allowed=[]  #*Stores hostnames allowed by user
        self.sourceRedirectedFormEnabled=False#*Flag to indicate whether the form in the source defined tab is enabled
        self.editMode=True #*Flag to indicate whether the form in the user redirected tab is in editMode or addMode
        self.redirectedIPv4=''#*Stores the initial IPv4 of the redirected rule that is currently being edited by the user
        self.redirectedHostname=''#*Stores the initial hostname of the redirected rule that is currently being edited by the user
        


        #*init the library for interacting with host sources,etc...
        #!WARNING:This changes the current directory
        self.parser=Parser.Parser()
        self.loadHosts()
        self.show()
        self.reconf_ui()

    def reconf_ui(self):
        #*Apply icons to the home button on each tab:
        #*For sourceDefine_tab:
        self.sourceBlockedHome_btn.setIcon(QtGui.QIcon(self.scriptPath+"/assets/home.svg"))
        self.sourceBlockedHome_btn.setIconSize(QtCore.QSize(30,20))
        #*For userBlocked_tab:
        self.blockedHome_btn.setIcon(QtGui.QIcon(self.scriptPath+"/assets/home.svg"))
        self.blockedHome_btn.setIconSize(QtCore.QSize(30,20))
        #*For Redirected_tab:
        self.redirectedHome_btn.setIcon(QtGui.QIcon(self.scriptPath+"/assets/home.svg"))
        self.redirectedHome_btn.setIconSize(QtCore.QSize(30,20))
        #*For userAllowed tab:
        self.allowedHome_btn.setIcon(QtGui.QIcon(self.scriptPath+"/assets/home.svg"))
        self.allowedHome_btn.setIconSize(QtCore.QSize(30,20))

        #*Hide all the status labels and ApplyConfig buttons:
        #*For sourceDefined_tab:
        self.sourceBlockedStatus_lbl.hide()
        self.sourceDefinedApplyConfig_btn.hide()
        #*For userBlocked_tab:
        self.blockedStatus_lbl.hide()
        self.blockedApplyConfig_btn.hide()
        #*For Redirected_tab:
        self.redirectedStatus_lbl.hide()
        self.redirectedApplyConfig_btn.hide()
        #*For userAllowed_tab:
        self.allowedStatus_lbl.hide()
        self.allowedApplyConfig_btn.hide()

        #*Disable or hide a few elements of the sourceDefined tab:
        self.allowSourceBlocked_btn.setDisabled(True)
        self.redirectSourceBlocked_btn.setDisabled(True)
        self.mainSourceDefinedStatus_lbl.hide()
        self.sourceBlockedHostname_lbl.hide()
        self.redirectSourceBlockedHost_tf.hide()
        self.redirectSourceBlockedHost_btn.hide()
        self.cancelRedirectSourceBlockedHost_btn.hide()

        #*Disable or hide a few elements of the userBlocked tab:
        self.deleteBlockedHost_btn.setDisabled(True)
        self.blockedHostname_lbl.show()
        self.blockedHostname_lbl.hide()
        self.addBlockedHost_tf.hide()
        self.addAddBlockedHost_btn.hide()
        self.cancelAddBlockedHost_btn.hide()
        self.mainBlockedStatus_lbl.hide()

        #*Disable or hide a few elements of the Redirected tab:
        self.editMode_lbl.hide()
        self.mainRedirectedStatus_lbl.hide()
        self.groupBox.setDisabled(True)
        self.mainRedirectedStatus_lbl.hide()
        self.deleteRedirectedHost_btn.setDisabled(True)

        #*Disable or hide a few elements of the userAllowed tab:
        self.deleteAllowedHost_btn.setDisabled(True)
        self.allowedHostname_lbl.show()
        self.allowedHostname_lbl.hide()
        self.addAllowedHost_tf.hide()
        self.addAddAllowedHost_btn.hide()
        self.cancelAddAllowedHost_btn.hide()
        self.mainAllowedStatus_lbl.hide()

    #*Several Utility functions:
    #*loads redirected host rules into redirectedTable
    def loadHosts(self):
        #*Fetch updates values from the Parser's getHosts() and update all the lists:
        self.sourceBlocked,self.blocked,self.redirected,self.allowed=self.parser.getHosts()
        #*Clear the GUI lists and tables if they already have any values:
        self.sourceDefinedList.clear()
        self.blockedList.clear()
        self.redirectedTable.setRowCount(0)
        self.allowedList.clear()
        #*Now load the new values:
        for i in self.sourceBlocked:
            self.sourceDefinedList.addItem(i)
        for i in self.blocked:
            self.blockedList.addItem(i)
        for i in self.allowed:
            self.allowedList.addItem(i)
        for i in range(len(self.redirected)):
            self.redirectedTable.setRowCount(len(self.redirected))
            ip,hostname=self.redirected[i].split()
            self.redirectedTable.setItem(i,0,QtWidgets.QTableWidgetItem(ip))
            self.redirectedTable.setItem(i,1,QtWidgets.QTableWidgetItem(hostname))
        '''If any are enabled,disable delete buttons of allowed and user blocked tabs, disable unblock and redirect buttons and hide the form of
        source blocked tab(because lists lose their selection on reloading data,and working with any of these components when nothing is
         selected will result in a crash):'''
        #*for source blocked tab:
        self.cancelRedirectSourceBlockedHostClicked()
        self.allowSourceBlocked_btn.setDisabled(True)
        self.redirectSourceBlocked_btn.setDisabled(True)
        #*For user blocked tab:
        self.deleteBlockedHost_btn.setDisabled(True)
        #*for allowed tab:
        self.deleteAllowedHost_btn.setDisabled(True)
    
    #*Displayes/Hides status labels informing the users of config changes:
    def showConfigChanged(self,showMessage=True):
        if showMessage:
            #*For sourceDefined tab:
            self.sourceBlockedStatus_lbl.setText("Configuration changed!")    
            self.sourceBlockedStatus_lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
            self.sourceBlockedStatus_lbl.show()
            self.sourceDefinedApplyConfig_btn.show()
            #*For userBlocked tab:
            self.blockedStatus_lbl.setText("Configuration changed!")    
            self.blockedStatus_lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
            self.blockedStatus_lbl.show()
            self.blockedApplyConfig_btn.show()
            #*For Redirected tab:
            self.redirectedStatus_lbl.setText("Configuration changed!")    
            self.redirectedStatus_lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
            self.redirectedStatus_lbl.show()
            self.redirectedApplyConfig_btn.show()
            #*For userAllowed tab:
            self.allowedStatus_lbl.setText("Configuration changed!")    
            self.allowedStatus_lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
            self.allowedStatus_lbl.show()
            self.allowedApplyConfig_btn.show()
            
        else:
            #*For sourcesDefined tab:
            self.sourceBlockedStatus_lbl.hide()
            self.sourceDefinedApplyConfig_btn.hide()
            #*For userBlocked tab:
            self.blockedStatus_lbl.hide()
            self.blockedApplyConfig_btn.hide()
            #*For Redirected tab:
            self.redirectedStatus_lbl.hide()
            self.redirectedApplyConfig_btn.hide()
            #*For userAllowed tab:
            self.allowedStatus_lbl.hide()
            self.allowedApplyConfig_btn.hide()
    
    #*Displays a success/error message on the label passed as an argument:
    def showStatus_lbl(self,message,lbl,success=False):
        if success:
            lbl.setStyleSheet("color:black;background-color:limegreen;font-weight:bold")
        else:
            lbl.setStyleSheet("color:white;background-color:crimson;font-weight:bold")
        lbl.setText(message)
        lbl.show()

    #*Adds the specified hostname to the userlist(thus blocking it):
    def blockHostname(self,hostname):
        #*Append the new hostname to the blocked list(sanitize it first by strip()-ing it)
        self.blocked.append(hostname.strip())
        #*(Possibly Redundant): Rid the list of any duplicate values(the fastest way to do so is to convert it to a set and back):
        self.blocked=list(set(self.blocked))
        #*Initialise a list to store all the rules we'll write to the userlist file:
        userlist=[]
        #*If the hostname is already present in a rule in the redirected list,ignore said rule.
        #*Add the redirected rules that don't have the hostname we're supposed to be blocking:
        for i in self.redirected:
            if hostname!=i.split()[1]:
                    userlist.append(i)
        #*Finally,add the contents of blocked list(as rules) to the userlist:
        for i in self.blocked:
            userlist.append('127.0.0.1 '+i)
        #*Sort the list to ensure the list isn't all jumbled up:
        userlist.sort()
        #*Finally,write the changes to the userlist file:
        userlist_file=open('userlist','w')
        for i in userlist:
            userlist_file.write(i+'\n')
        userlist_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()

    #*Deletes the specifed hostname from the blockedlst: 
    def deleteBlockedHostname(self,hostname):
        #*Remove the hostname from the blocked list:
        self.blocked.remove(hostname.strip())
        #*Generate a list of rules to write to the userlist file:
        userlist=[]
        for i in self.blocked:
            userlist.append('127.0.0.1 '+i)
        for i in self.redirected:
            userlist.append(i)
        #*Sort the list to ensure alphabetical order:
        userlist.sort()
        #*Now,write the changes to the userlist file:
        userlist_file=open('userlist','w')
        for i in userlist:
            userlist_file.write(i+'\n')
        userlist_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()

    #*Adds the specified hostname and ip as a rule to the userlist(thus redirecting said hostname to said IP):
    def redirectHostname(self,hostname,ip):
        #*If modifying an existing rule,remove the old version of the rule:
        if self.editMode:
            self.redirected.remove(self.redirectedIPv4+' '+self.redirectedHostname)
        
        #*Rid the list of any rules that already contain the hostname we wish to redirect:
        for i in self.redirected:
            if i.split()[1]==hostname:
                self.redirected.remove(i)
        #*Append the new hostname and IP(as a rule) to the redirected list
        self.redirected.append(ip+' '+hostname)
        #*This should remove any already existent duplicate values present in the list:
        self.redirected=list(set(self.redirected))
        #*Initialise a list to store all the rules we'll write to the userlist file:
        userlist=[]
        #*If the hostname is already present in the blocked list,we will still redirect it and remove the blocked-restrictions.
        #*Add the blocked list hostnames(as rules) that don't have the hostname we're supposed to be redirecting:
        for i in self.blocked:
            if hostname!=i:
                    userlist.append('127.0.0.1 '+i)
        #*Finally,add the contents of redirected list to the userlist:
        for i in self.redirected:
            userlist.append(i)
        #*Sort the list to ensure the list isn't all jumbled up:
        userlist.sort()
        #*Finally,write the changes to the userlist file:
        userlist_file=open('userlist','w')
        for i in userlist:
            userlist_file.write(i+'\n')
        userlist_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()

    #*Deletes the specifed hostname and IP rule from the redirected lst:
    def deleteRedirectedHostname(self,hostname,ip):
        #*Remove the hostname and IP rule from the redirected list:
        self.redirected.remove(ip+' '+hostname)
        #*Generate a list of rules to write to the userlist file:
        userlist=[]
        for i in self.blocked:
            userlist.append('127.0.0.1 '+i)
        for i in self.redirected:
            userlist.append(i)
        #*Sort the list to ensure alphabetical order:
        userlist.sort()
        #*Now,write the changes to the userlist file:
        userlist_file=open('userlist','w')
        for i in userlist:
            userlist_file.write(i+'\n')
        userlist_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()

    #*Adds the specifed hostname to the allowedlst:    
    def allowHostname(self,hostname):
        #*Append the new hostname to the allowed list(sanitize it first by strip()-ing it)
        self.allowed.append(hostname.strip())
        #*(Possibly Redundant): Rid the list of any duplicate values(the fastest way to do so is to convert it to a set and back):
        self.allowed=list(set(self.allowed))
        #*Ensure alphabetical order- sort the allowed list:
        self.allowed.sort()
        #*Finally,write the changes to the allowlst file:
        allowed_file=open('allowlst','w')
        for i in self.allowed:
            allowed_file.write(i+'\n')
        allowed_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()

    #*Deletes the specifed hostname from the allowedlst: 
    def deleteAllowedHostname(self,hostname):
        #*Remove the hostname from the allowed list:
        self.allowed.remove(hostname.strip())
        #*Now,write the changes to the allowlst file:
        allowed_file=open('allowlst','w')
        for i in self.allowed:
            allowed_file.write(i+'\n')
        allowed_file.close()
        #*We need to refresh the lists displayed on the GUI:
        self.loadHosts()
        #*Inform the user that their configuration changed(also display a button which allows them to apply the configuration):
        self.showConfigChanged()


    #*Applies the new configuration(the main hosts file will be regenerated and applied)
    def applyConfig(self):
        msg=QtWidgets.QMessageBox()
        msg.setStandardButtons(QtWidgets.QMessageBox.StandardButton.Ok)
        try:
            self.parser.regen_hosts()
            self.showConfigChanged(False)
            msg.setWindowTitle("Success")
            msg.setText("Configuration updated successfully!")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Information)
            msg.exec()
        except Exception as err:
            msg.setWindowTitle("Error")
            msg.setIcon(QtWidgets.QMessageBox.Icon.Critical)
            msg.setText("Oops! An error occurred. Additional info is provided below")
            msg.setDetailedText(str(err))
            msg.exec()
    

    #*Opens the home(main) window:
    def openHome(self):
        #*Change dir to the script path temporarily for the Ui class to load its ui file(it will automatically chdir back to the swiftblock directory):
        os.chdir(self.scriptPath)
        self.hide()
        self.parser.close_db()
        from main import Ui
        self.home=Ui()
        

    #*Maps each Signal to its Slot function:
    def SignalSlotConfig(self):
        self.sourceDefinedApplyConfig_btn.clicked.connect(self.applyConfig)
        self.blockedApplyConfig_btn.clicked.connect(self.applyConfig)
        self.redirectedApplyConfig_btn.clicked.connect(self.applyConfig)
        self.allowedApplyConfig_btn.clicked.connect(self.applyConfig)

        self.sourceBlockedHome_btn.clicked.connect(self.openHome)
        self.blockedHome_btn.clicked.connect(self.openHome)
        self.redirectedHome_btn.clicked.connect(self.openHome)
        self.allowedHome_btn.clicked.connect(self.openHome)

        #*Config for sourceDefined_tab:
        self.allowSourceBlocked_btn.clicked.connect(self.allowSourceBlockedRule)
        self.redirectSourceBlocked_btn.clicked.connect(self.redirectSourceBlockedClicked)
        self.redirectSourceBlockedHost_btn.clicked.connect(self.redirectSourceBlockedHostClicked)
        self.cancelRedirectSourceBlockedHost_btn.clicked.connect(self.cancelRedirectSourceBlockedHostClicked)
        self.sourceDefinedList.selectionModel().currentChanged.connect(self.sourceDefinedHostSelected)

        #*Config for userBlocked_tab:
        self.blockedList.selectionModel().currentChanged.connect(self.blockedHostSelected)
        self.deleteBlockedHost_btn.clicked.connect(self.deleteBlockedHostClicked)
        self.addBlockedHost_btn.clicked.connect(self.addBlockedHostClicked)
        self.addAddBlockedHost_btn.clicked.connect(self.addAddBlockedHostClicked)
        self.cancelAddBlockedHost_btn.clicked.connect(self.cancelAddBlockedHostClicked)

        #*Config for Redirected_tab:
        self.redirectedTable.selectionModel().currentChanged.connect(self.redirectedHostSelected)
        self.addRedirectedHost_btn.clicked.connect(self.addRedirectedHostClicked)
        self.deleteRedirectedHost_btn.clicked.connect(self.deleteRedirectedHostClicked)
        self.saveRedirectedHost_btn.clicked.connect(self.saveRedirectedHostClicked)
        self.cancelRedirectedHost_btn.clicked.connect(self.cancelRedirectedHostClicked)

        #*Config for userAllowed_tab:
        self.allowedList.selectionModel().currentChanged.connect(self.allowedHostSelected)
        self.deleteAllowedHost_btn.clicked.connect(self.deleteAllowedHostClicked)
        self.addAllowedHost_btn.clicked.connect(self.addAllowedHostClicked)
        self.addAddAllowedHost_btn.clicked.connect(self.addAddAllowedHostClicked)
        self.cancelAddAllowedHost_btn.clicked.connect(self.cancelAddAllowedHostClicked)

    #*SLOTS FOR EACH SIGNAL BELOW:
    #*Slots for SourceBlocked tab:
    #*Enables the allow and redirect buttons when an item from sourceDefinedList is selected: 
    def sourceDefinedHostSelected(self):
        self.allowSourceBlocked_btn.setDisabled(False)
        #*Only enable the redirect button if the form isnt enabled yet:(Otherwise it gets enabled every time user selects another item from the list)
        if not self.sourceRedirectedFormEnabled:
            self.redirectSourceBlocked_btn.setDisabled(False)
    
    #*Shows the form that allows user-selected source-blocked hostname to be redirected to a user defined IP:
    def redirectSourceBlockedClicked(self):
        #*Show the components of the form:
        self.sourceBlockedHostname_lbl.show()
        self.redirectSourceBlockedHost_btn.show()
        self.cancelRedirectSourceBlockedHost_btn.show()
        self.redirectSourceBlockedHost_tf.show()
        #*Set the flag which indicates whether form is enabled to True:
        self.sourceRedirectedFormEnabled=True
        #*Hide the main status label to clear any previous messages:
        self.mainSourceDefinedStatus_lbl.hide()
        #*And disable this button.It will be re-enabled if the user decides to cancel the process:
        self.redirectSourceBlocked_btn.setDisabled(True)

    #*Redirects user-selected hostname to a user-defined IP:
    def redirectSourceBlockedHostClicked(self):
        #*Get the IPv4 from the textfield:
        IPv4=self.redirectSourceBlockedHost_tf.text()
        #*Ensure the tf isn't empty and the IPv4 entered is valid:
        if IPv4!="" and self.parser.is_valid_ipv4(IPv4):
            #*Get the hostname selected by the user from the sourceBlocked list:
            hostname=self.sourceDefinedList.currentItem().text()
            #*Set the mode of the redirect-tab form to read mode temporarily(because we're adding this rule):
            mode=self.editMode
            self.editMode=False
            #*Add the user-selected hostname and IPv4 as a rule to the redirected list:
            self.redirectHostname(hostname,IPv4)
            #*Now,restore the mode to its original value:
            self.editMode=mode
            #*To hide all the controls,call the Slot of Cancel button:
            self.cancelRedirectSourceBlockedHostClicked()
            #*Also disable the redirect and unblock buttons(because nothing is selected currently):
            self.allowSourceBlocked_btn.setDisabled(True)
            self.redirectSourceBlocked_btn.setDisabled(True)
            #*Display success message to the user via status label:
            self.showStatus_lbl("Redirected the hostname successfully!",self.mainSourceDefinedStatus_lbl,success=True)
        else:
            self.showStatus_lbl("Please enter a valid IPv4!",self.mainSourceDefinedStatus_lbl)
    
    #*Hides the form that allows user to redirect selected hostname and does other cleanup:
    def cancelRedirectSourceBlockedHostClicked(self):
        #*Set the flag which indicates whether form is enabled to False:
        self.sourceRedirectedFormEnabled=False
        #*Clear any generated status messages:
        self.mainAllowedStatus_lbl.hide()
        #*Hide the form components:
        self.sourceBlockedHostname_lbl.hide()
        self.redirectSourceBlockedHost_btn.hide()
        self.cancelRedirectSourceBlockedHost_btn.hide()
        self.redirectSourceBlockedHost_tf.hide()
        #*Also clear the text of the textfield:
        self.redirectSourceBlockedHost_tf.setText("")
        #*Re-enable the main redirectSourceBlocked_btn:
        self.redirectSourceBlocked_btn.setDisabled(False)

    #*Adds the hostname to the allowed list(effectively unblocking it)
    def allowSourceBlockedRule(self):
        #*Hide the main status label to clear any previous messages:
        self.mainSourceDefinedStatus_lbl.hide()
        #*Get the selected hostname from the sourceDefinedList:
        hostname=self.sourceDefinedList.currentItem().text()
        #*Add the hostname to the allowed list:
        self.allowHostname(hostname)
        #*Disable Allow and Redirect buttons(since the list updated and no items are selected)
        self.allowSourceBlocked_btn.setDisabled(True)
        self.redirectSourceBlocked_btn.setDisabled(True)
        #*Display success message to the user via status label:
        self.showStatus_lbl("Added to allow-list successfully! ",self.mainSourceDefinedStatus_lbl,success=True)
    

    #*Slots for UserBlocked tab:
    #*Enables the delete button when an item from blockedList is selected:
    def blockedHostSelected(self):
        self.deleteBlockedHost_btn.setDisabled(False)

    #*Displays the controls to add a new hostname to blocked list:
    def addBlockedHostClicked(self):
        #*Display all the elements required to add a new hostname:
        self.blockedHostname_lbl.show()
        self.addBlockedHost_tf.show()
        self.addAddBlockedHost_btn.show()
        self.cancelAddBlockedHost_btn.show()
        #*Hide the main status label to clear any previous messages:
        self.mainBlockedStatus_lbl.hide()
        #*And disable this button.It will be re-enabled if the user decides to cancel the process:
        self.addBlockedHost_btn.setDisabled(True)
        #*Also disable the delete button:
        self.deleteBlockedHost_btn.setDisabled(True)
    
    #*Delete(remove) a hostname from the blocklist:
    def deleteBlockedHostClicked(self):
        #*Hide the main status label to clear any previous messages:
        self.mainBlockedStatus_lbl.hide()
        #*Display a prompt asking the user for confirmation:
        question=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question,"Please Confirm","Are you sure you want to remove this hostname from the blocklist?",(QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No))
        confirm=question.exec()
        if confirm==QtWidgets.QMessageBox.StandardButton.Yes:
            hostname=self.blockedList.currentItem().text()
            #*Remove the hostname from the blocked list:
            self.deleteBlockedHostname(hostname)
            #*Disable Delete button(since the list updated and no items are selected)
            self.deleteBlockedHost_btn.setDisabled(True)
            #*Display success message to the user via status label:
            self.showStatus_lbl("Deleted the hostname successfully!",self.mainBlockedStatus_lbl,success=True)
    
    #*Adds user-defined hostname to the blockedlst:
    def addAddBlockedHostClicked(self):
        #*Get the hostname from the hostname textfield:
        hostname=self.addBlockedHost_tf.text()
        #*Ensure the tf isn't empty and the hostname entered is valid:
        if hostname!="" and self.parser.is_valid_hostname(hostname.strip()):
            #*Also ensure it that it isn't already blocked by one of the sources(because blocking it once again will be redundant):
            alreadyBlocked=False
            for i in self.sourceBlocked:
                if hostname==i:
                    alreadyBlocked=True
                    break    
            if alreadyBlocked:
                self.showStatus_lbl("Hostname already blocked by a source!",self.mainBlockedStatus_lbl)
            else:
                self.blockHostname(hostname)
                #*To hide all the controls,call the Slot of Cancel button:
                self.cancelAddBlockedHostClicked()
                #*Display success message to the user via status label:
                self.showStatus_lbl("Added the hostname successfully!",self.mainBlockedStatus_lbl,success=True)
        else:
            self.showStatus_lbl("Please enter a valid hostname!",self.mainBlockedStatus_lbl)
    
    #*Cancel adding the hostname to blocked list(reset the form and other components):
    def cancelAddBlockedHostClicked(self):
        #*Clear the text in addBlockedHost_tf:
        self.addBlockedHost_tf.setText("")
        #*Hide all the elements required to add a new hostname:
        self.blockedHostname_lbl.hide()
        self.addBlockedHost_tf.hide()
        self.addAddBlockedHost_btn.hide()
        self.cancelAddBlockedHost_btn.hide()
        #*And enable the main Add button(addBlockedHost_btn):
        self.addBlockedHost_btn.setDisabled(False)
        #*No need to re-enable the delete button,it will enabled automatically when user selects a hostname from the blocked list
        #*Infact,we will have to disable it again,in case the user selected a hostname from the blocked list BEFORE clicking on the addAddBlockedHost_btn:
        self.deleteBlockedHost_btn.setDisabled(True)
        #*Hide the status label(since if user makes an error,but then clicks on cancel button the status label needs to be hidden):
        self.mainBlockedStatus_lbl.hide()




    #*Slots for Redirected_tab:
    #*Enables a form and some other components when a row from redirectedTable is selected:
    def redirectedHostSelected(self):
        row_idx=self.redirectedTable.currentRow()
        #*Everytime loadHosts() is called,the table briefly loses all its rows and considers it to be a change in the current row(so check to ensure the table isn't empty):
        if row_idx>-1:
            #*Enable the addRedirectedHost_btn:
            self.addRedirectedHost_btn.setDisabled(False)
            #*Also enable the delete button(in case the user wants to delete the selected rule):
            self.deleteRedirectedHost_btn.setDisabled(False)
            #*Enable the form components for editing the rule:
            self.groupBox.setDisabled(False)
            #*Set the mode to editMode:
            self.editMode=True
            self.editMode_lbl.setText("Editing a rule:")
            self.editMode_lbl.show()
            #*Display the hostname and IP of the rule to edit in the form textfields:
            self.redirectedIP_tf.setText(self.redirectedTable.item(row_idx,0).text())
            self.redirectedHostname_tf.setText(self.redirectedTable.item(row_idx,1).text())
            #*Also store the initial hostname and IP of the rule in global variables to help replace the intial version of the rule from the list after saving:
            self.redirectedIPv4=self.redirectedTable.item(row_idx,0).text()
            self.redirectedHostname=self.redirectedTable.item(row_idx,1).text()
            #*Remove any old error/success messages:
            self.mainRedirectedStatus_lbl.hide()
        else:
            #*If loadHosts() was called,no row is selected. So clear the form if it was in editMode:
            if self.editMode:
                #*Call slot of cancelRedirectedHost_btn to reset the form:
                self.cancelRedirectedHostClicked()
            #*Disable the deleteRedirectedHost_btn as no row is selected:
            self.deleteRedirectedHost_btn.setDisabled(True)     

    #*Adds a user-defined hostname that redirects to a user-defined IP:    
    def addRedirectedHostClicked(self):
        #*Make editMode=False(which means add mode):
        self.editMode=False
        #*Enable the form components and disable this button:
        self.editMode_lbl.setText("Adding a new rule:")
        self.editMode_lbl.show()
        self.groupBox.setDisabled(False)
        self.redirectedIP_tf.setText("")
        self.redirectedHostname_tf.setText("")
        self.addRedirectedHost_btn.setDisabled(True)

    #*Removes user selected rule from the redirected list:    
    def deleteRedirectedHostClicked(self):
        #*Display a prompt asking the user for confirmation:
        question=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question,"Please Confirm","Are you sure remove this hostname from the allowed list?",(QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No))
        confirm=question.exec()
        if confirm==QtWidgets.QMessageBox.StandardButton.Yes:
            #*Get the hostname and IP  from redirectedTable:
            row_idx=self.redirectedTable.currentRow()
            ip=self.redirectedTable.item(row_idx,0).text()
            hostname=self.redirectedTable.item(row_idx,1).text()
            self.deleteRedirectedHostname(hostname,ip)

    def saveRedirectedHostClicked(self):
        #*Get the hostname and IP  from the textfields:
        ip=self.redirectedIP_tf.text().strip()
        hostname=self.redirectedHostname_tf.text().strip()

        #*Ensure the tfs aren't empty and the hostname and IP entered is valid:
        if ip!="" and hostname!="":
            if self.parser.is_valid_ipv4(ip):
                if self.parser.is_valid_hostname(hostname):
                    if self.editMode:
                        self.redirectHostname(hostname,ip)
                        #*To hide all the controls,call the Slot of Cancel button:
                        self.cancelRedirectedHostClicked()
                        #*Display success message to the user via status label:
                        self.showStatus_lbl("Edited the rule successfully!",self.mainRedirectedStatus_lbl,success=True)
                    else:
                        self.redirectHostname(hostname,ip)
                        #*To hide all the controls,call the Slot of Cancel button:
                        self.cancelRedirectedHostClicked()
                        #*Re-enable the addRedirectedHost_btn:
                        self.addRedirectedHost_btn.setDisabled(False)
                        #*Display success message to the user via status label:
                        self.showStatus_lbl("Added the rule successfully!",self.mainRedirectedStatus_lbl,success=True)
                else:
                    self.showStatus_lbl("Please enter a valid hostname!",self.mainRedirectedStatus_lbl)
            else:
                self.showStatus_lbl("Please enter a valid IPv4!",self.mainRedirectedStatus_lbl)
        else:
            self.showStatus_lbl("Please fill all the fields!",self.mainRedirectedStatus_lbl)
    
    #*Cancel adding/editing the hostname to redirected list(reset the form):
    def cancelRedirectedHostClicked(self):
        self.redirectedIP_tf.setText("")
        self.redirectedHostname_tf.setText("")
        self.groupBox.setDisabled(True)
        self.editMode_lbl.hide()
        #*Hide any previously generated error/success messages:
        self.mainRedirectedStatus_lbl.hide()
        if not self.editMode:
            self.addRedirectedHost_btn.setDisabled(False)
            self.editMode=True



    #*Slots for UserAllowed tab:
    #*Enables the delete button when an item from allowedList is selected: 
    def allowedHostSelected(self):
        self.deleteAllowedHost_btn.setDisabled(False)

    
    #*Displays the controls to add a new hostname to allowlst:
    def addAllowedHostClicked(self):
        #*Display all the elements required to add a new hostname:
        self.allowedHostname_lbl.show()
        self.addAllowedHost_tf.show()
        self.addAddAllowedHost_btn.show()
        self.cancelAddAllowedHost_btn.show()
        #*Hide the main status label to clear any previous messages:
        self.mainAllowedStatus_lbl.hide()
        #*And disable this button.It will be re-enabled if the user decides to cancel the process:
        self.addAllowedHost_btn.setDisabled(True)
        #*Also disable the delete button:
        self.deleteAllowedHost_btn.setDisabled(True)
        
    #*Deletes the selected Hostname from the allowlst:
    def deleteAllowedHostClicked(self):
        #*Hide the main status label to clear any previous messages:
        self.mainAllowedStatus_lbl.hide()
        #*Display a prompt asking the user for confirmation:
        question=QtWidgets.QMessageBox(QtWidgets.QMessageBox.Icon.Question,"Please Confirm","Are you sure remove this hostname from the allowed list?",(QtWidgets.QMessageBox.StandardButton.Yes|QtWidgets.QMessageBox.StandardButton.No))
        confirm=question.exec()
        if confirm==QtWidgets.QMessageBox.StandardButton.Yes:
            hostname=self.allowedList.currentItem().text()
            #*Remove the hostname from the allowed list:
            self.deleteAllowedHostname(hostname)
            #*Disable Delete button(since the list updated and no items are selected)
            self.deleteAllowedHost_btn.setDisabled(True)
            #*Display success message to the user via status label:
            self.showStatus_lbl("Deleted the hostname successfully!",self.mainAllowedStatus_lbl,success=True)

    
    #*Adds user-defined hostname to the allowedlst:
    def addAddAllowedHostClicked(self):
        #*Get the selected hostname from the hostname textfield:
        hostname=self.addAllowedHost_tf.text()
        #*Ensure the tf isn't empty and the hostname entered is valid:
        if hostname!="" and self.parser.is_valid_hostname(hostname):
            #*Add the hostname to the allowed list:
            self.allowHostname(hostname)
            #*To hide all the controls,call the Slot of Cancel button:
            self.cancelAddAllowedHostClicked()
            #*Display success message to the user via status label:
            self.showStatus_lbl("Added the hostname successfully!",self.mainAllowedStatus_lbl,success=True)
        else:
            self.showStatus_lbl("Please enter a valid hostname!",self.mainAllowedStatus_lbl)

    #*Cancel adding the hostname to allowed list(reset the form and other components):
    def cancelAddAllowedHostClicked(self):
        #*Clear the text in addAllowedHost_tf:
        self.addAllowedHost_tf.setText("")
        #*Hide all the elements required to add a new hostname:
        self.allowedHostname_lbl.hide()
        self.addAllowedHost_tf.hide()
        self.addAddAllowedHost_btn.hide()
        self.cancelAddAllowedHost_btn.hide()
        #*And enable the main Add button(addAllowedHost_btn):
        self.addAllowedHost_btn.setDisabled(False)
        #*No need to re-enable the delete button,it will enabled automatically when user selects a hostname from the allowed list
        #*Infact,we will have to disable it again,in case the user selected a hostname from the allowed list BEFORE clicking on the addAddAllowedHost_btn:
        self.deleteAllowedHost_btn.setDisabled(True)
        #*Hide the status label(since if user makes an error,but then clicks on cancel button the status label needs to be hidden):
        self.mainAllowedStatus_lbl.hide()