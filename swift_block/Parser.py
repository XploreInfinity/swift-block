'''
Copyright (C) 2021 xploreinfinity

This program is free software: you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, version 3.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program. If not, see <https://www.gnu.org/licenses/>. 
'''

import os,requests,re,sqlite3,ipaddress,sys,inspect,subprocess
class Parser:
    def __init__(self):

        #*Global variable,stores records that need to be removed from the sources:
        self.obsolete=[r'^127\.0\.0\.1( +)localhost$',
        r'^127\.0\.0\.1( +)localhost\.localdomain$',
        r'^127\.0\.0\.1( +)local$',
        r'^255\.255\.255\.255( +)broadcasthost$',
        r'^0.0.0.0( +)0.0.0.0$']

        #*Perform a few pre-run checks:
        self.prerun_checks()

    #*Checks whether the menu launcher and swiftblock user directory are created. If not, it regenerates them:
    def prerun_checks(self):
        #*TODO: ADD SUPPORT FOR MACOS LAUNCHER
        #*Ensure a launcher shortcut is present,if not,regenerate:
        try:
            scriptPath=os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda:0))).replace('\\','/')
            if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
                install_path=''
                #*Generally,.desktop files are stored in either of these two locations, so we will place our .desktop file in any one of these locations.
                #*If any of the locations don't exist, don't create a .desktop file
                if os.path.exists('/usr/share/applications'):
                    install_path='/usr/share/applications'
                elif os.path.exists('/usr/local/share/applications'):
                    install_path='/usr/local/share/applications'
                if install_path and not os.path.exists(install_path+'/SwiftBlock.desktop'):
                    os.chdir(install_path)
                    desktopFile = open('SwiftBlock.desktop','w')
                    desktopFile.write(
                    """
                        [Desktop Entry]
                        Name=Swift Block
                        Comment= Block ads, trackers and malware swiftly
                        Exec=swift-block
                        Icon=%s/assets/app_icon.svg
                        Terminal=false
                        Type=Application
                        Categories=Qt;System;
                    """%scriptPath
                    )
                    desktopFile.close()
            elif sys.platform.startswith('win32'):
                import winshell
                programData = os.getenv('ProgramData')
                #*If programData exists and the swift block start shortcut doesn't, create it:
                if programData and not os.path.exists(programData+'\\Microsoft\\Windows\\Start Menu\\Programs\\Swift-Block.lnk'):
                    os.chdir(programData+'\\Microsoft\\Windows\\Start Menu\\Programs\\')
                    with winshell.shortcut(programData+'\\Microsoft\\Windows\\Start Menu\\Programs\\'+'Swift-Block.lnk') as lnk:
                        lnk.path = 'swift-block'
                        lnk.description = 'Block ads, trackers and malware swiftly'
            else:
                print('Cant create a menu launcher(Platform not supported). Skipping... :(')
        #*If an error occurs, warn the user, but proceed anyway since failing to create a launcher doesn't deter swift-block's functionality:
        except Exception as err:
            print('Oops! An error occurred while creating a menu launcher. Proceeding anyway.Error Details:\n',str(err))

        #*Ensure the swiftblock user directory and its components are present,if not, regenerate:
        try:
            os.chdir(os.path.expanduser("~/.swiftblock"))
            if not os.path.exists("userlist"):
                print('User-defined rule list file not found.Creating a new empty one.')
                userlist=open('userlist','w')
                userlist.close()
            if not os.path.exists("allowlst"):
                print('User-defined allow list file not found.Creating a new empty one.')
                allowlst=open('allowlst','w')
                allowlst.close()
            #*initialise the database:
            self.init_db()

        except FileNotFoundError:
            print("This appears to be a first run. Welcome to Swiftblock!! :)")
            print("Swiftblock directory not found.Creating it...")
            os.mkdir(os.path.expanduser("~/.swiftblock"))
            os.chdir(os.path.expanduser("~/.swiftblock"))

            print('User-defined rule list file not found.Creating a new empty one.')
            userlist=open('userlist','w')
            userlist.close()

            print('User-defined allow list file not found.Creating a new empty one.')
            allowlst=open('allowlst','w')
            allowlst.close()

            #*initialise the database:
            self.init_db()

            print('Generating the first hosts file...')
            self.regen_hosts()
            print('All done :)')

    #*Initialises the DB and regenerates it,if DB file is found missing or corrupt:
    def init_db(self):
        try:
            self.conn=sqlite3.connect('sources.db')
            self.cursor=self.conn.cursor()
            self.cursor.execute("SELECT * FROM sources")
        except:
            print('DB File corrupted or previously deleted.Regenerating...')
            self.cursor.execute("CREATE TABLE sources(name varchar(50) PRIMARY KEY,url varchar(500) UNIQUE);")
            self.cursor.execute("INSERT INTO sources values('Adaway','https://adaway.org/hosts.txt');")
            self.cursor.execute("INSERT INTO sources values('StevenBlack','https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts');")
            self.cursor.execute("INSERT INTO sources values('Pete','https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext');")
            self.conn.commit()

    #*Closes connection to the DB(required to remove DB lock which might occur while switching between different app windows):
    def close_db(self):
        try:
            if self.cursor:
                self.cursor.close()

            if self.conn:
                self.conn.close()
        except:
            print('close_db: Connection to the DB is already closed')

    #*Fetches all the details of source files from the sources table in the DB
    def fetch_sources(self):
        query="SELECT * FROM sources;"
        result=self.cursor.execute(query)
        return result.fetchall()

    #*This generates a basic hosts file consisting of rules compiled from various sources present in the DB
    def generateSourceRules(self,updateSources=False):
        #*Clear the sourceslist file to remove old rules:
        sources_file=open('sourceslist','w')
        sources_file.close()
        #*Get names of the sources from DB:
        sources_lst=self.fetch_sources()
        #*One by one, merge each source into the sourceslist file:
        for i in sources_lst:
                name=i[0]
                url=i[1]
                source_file=None
                #*If we simply regenerating sources without updating the source file and if the file exists on the disk,use it:
                if os.path.exists(name+".txt") and not updateSources:
                    source_file=open(name+".txt",'r')
                #*Else if the source file was deleted,or we are updating the source files by fetching a fresh version,re-download it:
                else:
                    self.download_source(name, url)
                    source_file=open(name+".txt",'r')
                #*We're using readlines() because its generally recommended and we wont have blank '' that are returned by read() when it reaches EOF
                file_lst=set([i.strip() for i in source_file.readlines()])
                main_sources=open('sourceslist','r')
                main_lst=set([i.strip() for i in main_sources.readlines()])
                main_sources.close()
                #*Find rules present in the current source file that arent in the main_sources file and then add those
                diff=file_lst-main_lst
                main_lst.update(diff)
                main_lst=list(main_lst)
                main_lst.sort()
                #*Finally write the merged list to the main sources file:
                main_sources=open('sourceslist','w')
                for i in main_lst:
                    main_sources.write(i+'\n')
                main_sources.close()

    #*This method will regenerate the hosts file with the various hosts sources
    def regen_hosts(self):
        #*Clean the hosts file to remove old rules
        main_hosts=open('hosts','w')
        #*First generate a basic hosts file from various sources(specified in the DB):
        self.generateSourceRules()
        #*Copy the contents of sourceslist(containing rules from the sources)
        main_sources=open('sourceslist','r')
        main_hosts.write(main_sources.read())
        main_hosts.close()

        #*Next, add the user defined rules to the hosts file:
        user_hosts=open('userlist','r')
        user_list=[i.strip() for i in user_hosts.readlines()]
        user_hosts.close()
        main_hosts=open('hosts','r')
        main_lst=[i.strip() for i in main_hosts.readlines()]
        main_hosts.close()

        #*Now,replace source defined rules with /add rules defined by the user
        compiled_list=[]
        user_rules=[]#*stores user defined rules that replaced a source defined rule, we will still need to include user defined rules other than these in the main hosts
        for i in main_lst:
            replaced=False #*This flag informs whether a source defined rule got replaced by a user defined one
            for j in user_list:
                #*The IP and hostname in each rule is separated by spaces.Split the rule and extract only the hostname
                if i.split()[1]==j.split()[1]:
                    compiled_list.append(j)
                    replaced=True
                    user_rules.append(j)
            if not replaced:
                compiled_list.append(i)
        #*Now add other user defined rules which didn't replace any host defined rules:
        for i in user_list:
            if i not in user_rules:
                compiled_list.append(i)
        compiled_list.sort()
        #*Now write the compiled rules to the main hosts file:
        main_hosts=open('hosts','w')
        for i in compiled_list:
            main_hosts.write(i+'\n')
        main_hosts.close()
        #*Lastly remove any rules from the hosts file containing hostnames which the user has allowed:
        #*We already have the contents of the main hosts file in compiled_list
        allow_lst=open('allowlst','r')
        allowed_rules=[i.strip() for i in allow_lst.readlines()]
        final_lst=[]
        for i in compiled_list:
            in_allowed=False
            for j in allowed_rules:
                #*Check whether any hostname in the main hosts file is equal to a hostname that the user has allowed:
                if i.split()[1]==j:
                    in_allowed=True
            #*Since the hostname doesn't match with any hostnames allowed by the user,add it to the final hosts-list:
            if not in_allowed:
                final_lst.append(i)
        #*Write the changes to the main hosts file:
        main_hosts=open('hosts','w')
        for i in final_lst:
            main_hosts.write(i+'\n')
        main_hosts.close()

        blockerStatus=self.getStatus()[3]
        #*Write these changes to the system hosts file[only if swiftblock is active]:
        if blockerStatus:
            self.write_changes()

    #*Downloads hosts files from remote sources(can also get files from filesystem-but this feature is currently unused):
    def download_source(self,name,url,offline=False):
        #*get the url corresponding to the source name:
        match=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}( +)(.[^ ]*)$"

        file_contents=[]
        if offline:
            #*the file is on disk.The url param acts as a file path:
            source_file=open(url,'r')
            file_contents=[i.strip() for i in source_file.readlines()]
            source_file.close()
        else:
            response=requests.get(url,allow_redirects=True)
            file_contents=response.text.split('\n')
        #*split the recieved text into a list separated by \n
        hosts=[]
        for i in file_contents:
            #*Ensure that the line is not empty/badly formatted and is not a comment.
            if re.search(match,i.strip()):
                    #*remove generic entries that identify with the local machine or network:
                    clean=True
                    for dup in self.obsolete:
                        if re.search(dup,i):
                            clean=False
                            break
                    if clean:

                        #*Replace 0.0.0.0(or any other source specified ip) with 127.0.0.1 for safety reasons.
                        #!Do this only for remote sources.User's custom list isn't affected.
                        if not offline:
                            replace_pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                            i=re.sub(replace_pattern,"127.0.0.1",i)
                        hosts.append(i)
                        #*Ensure the hostname is valid:
                        hostname=i.split()[1]
                        if self.is_valid_hostname(hostname):
                            #*if the hostname is valid, add its rule to the hosts list:
                            i=i.split()[0]+' '+hostname
        hosts.sort()
        host_file=None
        if offline:
            host_file=open(url,'w')
        else:
            host_file=open(name+'.txt','w')
        #*write the newly fetched remote hosts to file;offline files need to be rewritten with the cleaned hosts entries as well:
        for line in hosts:
            host_file.write(line+'\n')#*line breaks were removed earlier,add them again between each line.
        host_file.close()

    def add_source(self,name,url):
        query="INSERT INTO sources VALUES('"+name+"','"+url+"')"

        self.cursor.execute(query)
        self.conn.commit()
        #*download the new source and merge with the main hosts file:
        self.download_source(name,url)


    def edit_source(self,oldname,newname,oldurl,newurl):
        query="UPDATE sources SET name='"+newname+"',url='"+newurl+"' WHERE name='"+oldname+"'"
        self.cursor.execute(query)
        self.conn.commit()
        if oldname!=newname and oldurl==newurl:
            #*rename the old source file to its new name if it exists:
            if os.path.exists(oldname+'.txt'):
                os.rename(oldname+'.txt',newname+'.txt')
            else:
                #*the file doesn't exist,download it:
                self.download_source(newname,newurl)
        else:
            #*remove the old source file if it exists:
            if os.path.exists(oldname+'.txt'):
                os.remove(oldname+'.txt')
            #*Download the new source[from the new URL] and regenerate the main hosts file:
            self.download_source(newname,newurl)
            self.regen_hosts()

    #*Deletes a source from the sources.db and removes its contents from the hosts file:
    def del_source(self,name):
        query="DELETE FROM sources WHERE name='"+name+"'"
        self.cursor.execute(query)
        self.conn.commit()
        #*Since we deleted the source from the db,remove the file as well:
        if os.path.exists(name+'.txt'):
            os.remove(name+'.txt')
        #*regenerate the main hosts:
        self.regen_hosts()

    #*Retrieves hosts to display in RuleManager:
    def getHosts(self):
        match=r"^127\.0\.0\.1( +)(.[^ ]*)$"
        sources_hosts=open('sourceslist','r')
        user_hosts=open('userlist','r')
        allowed_hosts=open('allowlst','r')
        hosts=[i.strip() for i in user_hosts.readlines()]
        blocked=[]
        redirected=[]
        #*Looks Kinda complex: we're just reading the sources file but only taking the hostnames from the rules on each line
        sourceBlocked=set([i.strip().split()[1] for i in sources_hosts.readlines()])
        allowed=[i.strip() for i in allowed_hosts.readlines()]
        for rule in hosts:
            if re.search(match,rule):
                blocked.append(rule.split()[1])
            else:
                redirected.append(rule)
        #*Remove any rules from the sourceBlocked list that are present in the userdefined lists
        sourceBlocked=sourceBlocked-set(blocked)
        sourceBlocked=sourceBlocked-set([i.split()[1] for i in redirected])
        sourceBlocked=list(sourceBlocked-set(allowed))
        #*Sets jumble their contents,so,after conversion we need to sort the list
        sourceBlocked.sort()
        return sourceBlocked,blocked,redirected,allowed

    #*Checks if the given hostname is valid:
    def is_valid_hostname(self,hostname):
        if len(hostname) > 255:
            return False
        if hostname[-1] == ".":
            hostname = hostname[:-1] #*strip exactly one dot from the right, if present
        allowed = re.compile(r"^(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
        return all(allowed.match(x) for x in hostname.split("."))

    #*Checks if given IPv4 is valid:
    def is_valid_ipv4(self,ipv4):
        try:
                ipaddress.IPv4Address(ipv4)
                return True
        except ValueError:
               return False

    #*Returns the status of the adblocker(whether active,no. of hosts blocked/redirected/allowed):
    def getStatus(self):
        #*Check whether swiftblock is active(i.e whether swiftblock's rules are loaded in the system hosts file):
        file_path=''#*Stores the path to the hosts file[this is platform-dependent]
        #*Determine what platform the app is running on:
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin') or sys.platform.startswith('freebsd'):
            file_path='/etc/hosts'
        elif sys.platform.startswith('win32'):
            systemroot = os.getenv('SystemRoot')
            file_path=systemroot+'\\System32\\drivers\\etc\\hosts'
        else:
            print('Unsupported platform!!')
            sys.exit()
        #*Open the system hosts file to check for swiftblock rules
        system_hosts=open(file_path,'r')
        file_contents=[i.strip() for i in system_hosts.readlines()]
        inRuleSet=False#*A flag which tracks the section of the list we are currently within(i.e whether outside swiftblock ruleset or inside it)
        foundRuleSet=False
        for i in file_contents:
            if i=="# SWIFTBLOCK RULESET BEGINS":
                foundRuleSet=True

        #*Get the statistics(no. of hosts blocked/redirected/allowed) from hosts file in swiftblock's user directory
        if os.path.exists('hosts'):
            main_hosts=open('hosts','r')
            main_lst=[i.strip() for i in main_hosts.readlines()]
            blocked,redirected,allowed=[],[],[]
            for i in main_lst:
                if i.split()[0]=='127.0.0.1':
                    blocked.append(i)
                else:
                    redirected.append(i)
            if os.path.exists('allowlst'):
                allowed_file=open('allowlst','r')
                allowed_list=[i.strip() for i in allowed_file.readlines()]
                for i in allowed_list:
                    allowed.append(i)
            return len(blocked),len(redirected),len(allowed),foundRuleSet
        else:
            return None,None,None,foundRuleSet

    #*Writes new changes to the the system hosts file[the purge flag,when True will erase existing swiftblock ruleset and replace it with nothing]:
    def write_changes(self,purge=False):
        file_path=''#*Stores the path to the hosts file[this is platform-dependent]
        #*Determine what platform the app is running on:
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin') or sys.platform.startswith('freebsd'):
            file_path='/etc/hosts'
        elif sys.platform.startswith('win32'):
            systemroot = os.getenv('SystemRoot')
            file_path=systemroot+'//System32//drivers//etc//hosts'
        else:
            print('Unsupported platform!!')
            sys.exit()

        system_hosts=open(file_path,'r')
        file_contents=[i.strip() for i in system_hosts.readlines()]
        system_hosts.close()
        foreign_contents=[] #*Temporarily stores other contents of the system hosts file,i.e,user added/default stuff(stuff outside our swiftblock ruleset)
        withinRuleset=False #*A flag which tracks the section of the list we are currently within(i.e whether outside swiftblock ruleset or inside it)
        #*Create a list of the lines outside the swiftblock ruleset:
        for i in file_contents:
            if i!="# SWIFTBLOCK RULESET BEGINS" and withinRuleset==False:
                foreign_contents.append(i)
            else:
                if i=="# SWIFTBLOCK RULESET ENDS":
                    withinRuleset=False
                else:
                    withinRuleset=True

        #*Write the changes to the swiftblock ruleset, but first, write contents that were present in the file outside of the swiftblock ruleset:
        system_hosts=open(file_path,'w')
        for i in foreign_contents:
            system_hosts.write(i+'\n')
        #*If the purge flag is set to false,add the swiftblock ruleset,otherwise,do nothing:
        if not purge:
            #*Get the rules from the hosts file in swiftblock user directory:
            main_hosts=open('hosts','r')
            hosts=[i.strip() for i in main_hosts.readlines()]
            #*Write the line that marks the beginning of the swiftblock-ruleset:
            system_hosts.write("# SWIFTBLOCK RULESET BEGINS"+'\n')
            #*Write all the rules:
            for i in hosts:
                system_hosts.write(i+'\n')
            #*Write the line that marks the ending of the swiftblock-ruleset:
            system_hosts.write("# SWIFTBLOCK RULESET ENDS"+'\n')
        system_hosts.close()

    #*Uninstalls swiftblock and removes the menu launcher (but not the swiftblock user directory):
    def uninstall(self):
        #*Remove the menu launcher:
        scriptPath=os.path.abspath(os.path.dirname(inspect.getsourcefile(lambda:0))).replace('\\','/')
        if sys.platform.startswith('linux') or sys.platform.startswith('freebsd'):
            file_path=''
            #*Our .desktop file is stored in either of these two locations. If neither locations exist,then we know we didn't create a .desktop file
            if os.path.exists('/usr/share/applications'):
                file_path='/usr/share/applications'
            elif os.path.exists('/usr/local/share/applications'):
                file_path='/usr/local/share/applications'
            if file_path and os.path.exists(file_path+'/SwiftBlock.desktop'):
                    os.unlink(file_path+'/SwiftBlock.desktop')
        elif sys.platform.startswith('win32'):
            programData = os.getenv('ProgramData')
            #*If programData and the swift block start menu shortcut exist,delete the swiftblock start menu shortcut:
            if programData and os.path.exists(programData+'\\Microsoft\\Windows\\Start Menu\\Programs\\Swift-Block.lnk'):
                os.unlink(programData+'\\Microsoft\\Windows\\Start Menu\\Programs\\Swift-Block.lnk')

        #*Uninstall the swift_block package:
        subprocess.check_call([sys.executable] + ' -m pip uninstall swift_block -y'.split())
        #*Now exit swift-block:
        exit()
