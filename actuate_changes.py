import os,sys
from elevate import elevate
class actuate:
    def __init__(self):
        elevate()
    def main(self):
        print('I like fortnite,I am',os.getuid())

    #*Writes new changes to the the system hosts file[the purge flag,when True will erase existing swiftblock ruleset and replace it with nothing]:
    def write_changes(self,hosts,purge=False):
        file_path=''#*Stores the path to the hosts file[this is platform-dependent]
        #*Determine what platform the app is running on:
        if sys.platform.startswith('linux') or sys.platform.startswith('darwin') or sys.platform.startswith('freebsd'):
            file_path='/etc/hosts'
        elif sys.platform.startswith('win32'):
            file_path='C:\Windows\System32\drivers\etc\hosts'
        else:
            print('Unsupported platform!!')
            sys.exit()
        print(file_path)

        system_hosts=open('/home/mint/noob.txt','r')
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
        print(foreign_contents)
        
        #*Write the changes to the swiftblock ruleset, but first, write contents that were present in the file outside of the swiftblock ruleset:
        system_hosts=open('/home/mint/noob.txt','w')
        for i in foreign_contents:
            system_hosts.write(i+'\n')
        #*If the purge flag is set to false,add the swiftblock ruleset,otherwise,do nothing:
        if not purge:
            #*Write the line that marks the beginning of the swiftblock-ruleset:
            system_hosts.write("# SWIFTBLOCK RULESET BEGINS"+'\n')
            #*Write all the rules:
            for i in hosts:
                system_hosts.write(i+'\n')
            #*Write the line that marks the ending of the swiftblock-ruleset:
            system_hosts.write("# SWIFTBLOCK RULESET ENDS"+'\n')
        system_hosts.close()


#!TESTING:
f=open('/home/mint/.adblock/hosts','r')
hosts=[i.strip() for i in f.readlines()]
actuate().write_changes(hosts)