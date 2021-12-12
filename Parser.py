import os,requests,re,sqlite3,ipaddress
from elevate import elevate
class Parser:
    def __init__(self):

        #*remove these records from the sources:
        self.obsolete=[r'^127\.0\.0\.1( +)localhost$',
        r'^127\.0\.0\.1( +)localhost\.localdomain$',
        r'^127\.0\.0\.1( +)local$',
        r'^255\.255\.255\.255( +)broadcasthost$',
        r'^0.0.0.0( +)0.0.0.0$']
        try:
            os.chdir(os.path.expanduser("~/.adblock"))
        except FileNotFoundError:
            print("Adblock directory not found.Creating it...")
            os.mkdir(os.path.expanduser("~/.adblock"))
            os.chdir(os.path.expanduser("~/.adblock"))
        self.init_db()


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

    #*Fetches all the details of source files from the sources table in the DB
    def fetch_sources(self):
        query="SELECT * FROM sources;"
        result=self.cursor.execute(query)
        return result.fetchall()
    
    #*This generates a basic hosts file consisting of rules compiled from various sources present in the DB
    def generateSourceRules(self):
        #*Clear the sourceslist file to remove old rules:
        sources_file=open('sourceslist','w')
        sources_file.close()
        #*Get names of the sources from DB:
        sources_lst=self.fetch_sources()
        #*One by one, merge each source into the sourceslist file:
        for i in sources_lst:
                name=i[0]
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
        '''
        #*finally,also include user's custom hosts list:
        self.download_source("custom","customlst",True)
        #*Remove entries within the main host files that are mentioned in allow list:
        #*TODO:CLEAN UP THIS MESS
        source_file=open('hosts','r')
        file_contents={i.strip() for i in source_file.readlines()}
        source_file.close()
        #allowlst_contents=self.customlst("allowlst")
        #diff=file_contents-allowlst_contents
        #print(diff)
        source_file=open('hosts','w')
        source_file.write('\n'.join(list(file_contents)))
        '''
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
                            #TODO:REMOVE THIS DEBUG OUTPUT LATER
                            print('Rid it:',i,' Identifying with:',dup)
                            clean=False
                            break
                    if clean:
                        
                        #*Replace 0.0.0.0(or any other source specified ip) with 127.0.0.1 for safety reasons.
                        #!Do this only for remote sources.User's custom list isn't affected.
                        if not offline:
                            replace_pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                            i=re.sub(replace_pattern,"127.0.0.1",i)
                        hosts.append(i)
                        '''
                        STANDBY FOR MORE INTEL<waiting on adaway issue,weebs havent responded yet>
                        #*remove www. prefixes from all hostnames and Ensure all hostnames are valid:
                        hostname=i.split()[1]
                        hostname=re.sub(r'^www\.',"",hostname)

                        if self.is_valid_hostname(hostname):
                            #*if the hostname is valid, add its rule to the hosts list:
                            i=i.split()[0]+' '+hostname
                            
                        else:
                            print(hostname)'''  
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

    def dontlookatme(self,name,url,offline=False):

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
                            #TODO:REMOVE THIS DEBUG OUTPUT LATER
                            print('Rid it:',i,' Identifying with:',dup)
                            clean=False
                            break
                    if clean:
                        #*Replace 0.0.0.0(or any other source specified ip) with 127.0.0.1 for safety reasons.
                        #!Do this only for remote sources.User's custom list isn't affected.
                        if offline:
                            hosts.append(i)
                        else:
                            replace_pattern=r"^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}"
                            hosts.append(re.sub(replace_pattern,"127.0.0.1",i))

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

        #*Merge the new file with the main hosts file
        file_lst=set(hosts)
        main_hosts=open('hosts','r')
        #*We're using readlines() because its generally recommended and we wont have blank '' that are returned by read() when it reaches EOF
        main_lst=set([i.strip() for i in main_hosts.readlines()])
        #*Find hosts that arent in the main_hosts file
        diff=file_lst-main_lst
        main_lst.update(diff)
        main_lst=list(main_lst)
        main_lst.sort()
        #*Finally write the merged list to the main hosts file:
        main_hosts=open('hosts','w')
        for i in main_lst:
            main_hosts.write(i+'\n')

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

    def del_source(self,name):
        query="DELETE FROM sources WHERE name='"+name+"'"

        self.cursor.execute(query)
        self.conn.commit()
        #*Since we deleted the source from the db,remove the file as well:
        if os.path.exists(name+'.txt'):
            os.remove(name+'.txt')
        #*regenerate the main hosry)
        self.conn.commit()
        #*download the new source and merge with the main hosts file:
        self.download_source(name,url)

        sources_file=open('sources','r')
        temp_lst=sources_file.read().split("\n")
        temp_lst.remove('')
        sources_lst=[]
        for i in temp_lst:
            sources_lst.append(i.split(","))
        return sources_lst
      
    #*this function writes reads user's custom allow/deny list
    def customlst(self,url,hosts=None):
        #!The check is done because python thinks ""==None :(
        if hosts!=None:
            source_file=open(url,'w')
            source_file.write(hosts)
            source_file.close()
            #*Update the main hosts file since the custom list changed:
            self.regen_hosts()
        else:
            try:
                source_file=open(url,'r')
                file_contents=[i.strip() for i in source_file.readlines()]
                source_file.close()
                customLst='\n'.join(file_contents)
                return customLst
            except FileNotFoundError:
                #*The customlst file doesnt exist so recreate it:
                source_file=open(url,'w')
                source_file.close()
                print("Custom-list file is non-existent or corrupted. Recreating...")
                return 

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
        allowed = re.compile(r"(?!-)[A-Z\d-]{1,63}(?<!-)$", re.IGNORECASE)
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
            return len(blocked),len(redirected),len(allowed)
            #*TODO: check whether blocker is active
        
        else:
            return None,None,None
            
'''
h=Parser()
h.download_source('Adaway','https://adaway.org/hosts.txt')
h.download_source('Pete','https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext')
'''
'''
h=Parser()
if h.del_source('petelowe'):print('Yes it worked')
if h.add_source('adaway','https://adaway.org/hosts.txt') :print('Added adaway')
if h.add_source('steven','https://raw.githubusercontent.com/StevenBlack/hosts/master/hosts'): print('Added steven')
if h.add_source('pete','https://pgl.yoyo.org/adservers/serverlist.php?hostformat=hosts&showintro=0&mimetype=plaintext'): print('Added Pete')
print(h.fetch_sources())

'''