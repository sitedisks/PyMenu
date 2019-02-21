import json, subprocess, os, copy,shutil, platform, pygame, Common
from ast import literal_eval as make_tuple
from pprint import pprint


configuration = None
theme = json.load(open('theme/theme.json'))
listeners = []
types = ["RS97", "RS07", "K3P"]

def getConfiguration():   
    if(configuration == None):      
        reloadConfiguration()

    return configuration

def reloadConfiguration(): 
    global configuration
    configuration = json.load(open('config/config.json'))
    if("version" not in configuration):
        configuration["version"] = "0"

    if("type" not in configuration["options"] or configuration["options"]["type"] not in types):
        print("forcing type to RS97")
        configuration["options"]["type"] = "RS97"

    if("themeName" not in configuration["options"]):
        configuration["options"]["themeName"] = "default"


    configuration["mainMenu"] = []  
    setResolution()


    if os.path.exists(os.path.dirname("config/main/")):
        fileList = os.listdir("config/main/")
        Common.quick_sort(fileList)       
        for name in fileList:
            try:         
                if(os.path.isdir("config/main/" + name )):       
                    entry = json.load(open("config/main/" + name + "/config.json"))
                    entry["source"] = name


                    if( configuration["options"]["showAll"] or entry["type"] == "native"):                        
                        entry["data"] = []
                        try:
                            itemlist = os.listdir( entry["linkPath"])                          
                            Common.quick_sort(itemlist) 
                        
                            for itemName in itemlist:                                
                                item = createNativeItem(entry["linkPath"] + "/" + itemName)   
                                appendTheme(item)
                                entry["data"].append(item)

                            appendTheme(entry)
                            configuration["mainMenu"].append(entry)
                                
                        except Exception as ex:
                            print("Error loading item:" + str(ex))
                       

                    elif(hasConfig(entry["system"]) or configuration["options"]["showAll"] ):

                        appendTheme(entry)
                        appendEmuLinks(entry)
                        configuration["mainMenu"].append(entry)                       
                       
                

            except Exception as ex:
                print(str(ex)) 


def hasConfig(system):
    global configuration
    found = False   
    for (dirpath, dirnames, filenames) in os.walk(configuration["linkPath"]):
        for name in filenames:         
            if(name.lower().startswith(system.lower() + ".") or
            name.lower() == system.lower()):
                found = True
                break

    return found


def createNativeItem(item):
    data = parseLink(item)
    
    entry = {}
    entry["name"] = data["title"]
    entry["cmd"] = data["exec"]
    entry["description"] = data["description"]

    if("clock" in data):
        entry["overclock"] = data["clock"]
    
    entry["workingDir"] = os.path.abspath(os.path.join(data["exec"], os.pardir))


    if("selectordir" in data):
        entry["selector"] = True
        entry["selectionPath"] = data["selectordir"]

        if("selectorfilter" in data):           
            filter = data["selectorfilter"].split(",")                  
            entry["fileFilter"] = list(set(filter))

    return entry

def appendEmuLinks(entry):
    global configuration
    system = entry["system"]

    entry["emu"] = [] #clear emus
    entry["useSelection"] = False
  
    for (dirpath, dirnames, filenames) in os.walk(configuration["linkPath"]):
        for name in filenames:
            if(name.lower().startswith(system.lower() + "." ) or
            name.lower() == system.lower()):
                data = parseLink(dirpath + "/" + name)         
                emuEntry = {}
                emuEntry["name"] = data["description"]
                emuEntry["cmd"] = data["exec"]
                emuEntry["workingDir"] = os.path.abspath(os.path.join(data["exec"], os.pardir))
                entry["emu"].append(emuEntry)
                if("selectorfilter" in data and "useFileFilter" in entry and entry["useFileFilter"]):           
                    filter = data["selectorfilter"].split(",")
                    if("fileFilter" in entry):
                        filter.extend(entry["fileFilter"])
                    #make unique
                    entry["fileFilter"] = list(set(filter))

                if("selectordir" in data):
                    entry["useSelection"] = True




def parseLink(linkFile):
    f = open(linkFile, "r")
    data = {}
    file_as_list = f.readlines()

    for line in file_as_list:       
        params = line.split("=", 1)
        if(len(params) == 2):
            data[params[0]] = params[1].rstrip()
 
    return data


def deleteMainEntry(source):
    try:
        shutil.rmtree("config/main/" + source)

    except Exception as ex:
        print(str(ex))
  
def changeThemeName(name):
    allConfig = copy.deepcopy(configuration)
    allConfig["options"]["themeName"] = name
    del allConfig["mainMenu"]

    with open('config/config.json', 'w') as fp: 
        json.dump(allConfig, fp,sort_keys=True, indent=4)

def appendTheme(entry):
    typeName = configuration["options"]["type"]
    themeName = configuration["options"]["themeName"]
    entryName = entry["name"]

    

    try:
        if os.path.exists("theme/" + typeName+ "/" + themeName + "/" + entryName + ".json"):
            themeConfig = json.load(open("theme/" + typeName+ "/" + themeName + "/" + entryName + ".json")) 
            entry.update(themeConfig)
        else:
            print("loaded default config for " + entryName)
            if("type" in entry):
                #if it hast type param, its a main menu entry
               
                themeConfig = json.load(open("theme/default.json")) 
                entry.update(themeConfig)

            
    except Exception as ex:
        print(str(ex))

def saveTheme(entry):
    typeName = configuration["options"]["type"]
    themeName = configuration["options"]["themeName"]
    entryName = entry["name"]
    try:
        theme = {}
        if "folderIcon" in entry:
            theme["folderIcon"] = entry["folderIcon"]
            del entry["folderIcon"]
        if "icon" in entry: 
            theme["icon"] = entry["icon"]
            del entry["icon"]
        if "background" in entry: 
            theme["background"] = entry["background"]
            del entry["background"]
        if "preview" in entry: 
            theme["preview"] = entry["preview"]
            del entry["preview"]


        #create theme folder
        if not os.path.exists("theme/" + typeName+ "/" + themeName):
           os.makedirs("theme/" + typeName+ "/" + themeName)


        if os.path.exists("theme/" + typeName+ "/" + themeName + "/" + entryName + ".json"):
            #print("Duplicate name! " + str(entryName) )
            pass
        

        with open("theme/" + typeName+ "/" + themeName + "/" + entryName + ".json", 'w') as fp: 
            json.dump(theme, fp,sort_keys=True, indent=4) 


    except Exception as ex:
        print(str(ex))

   


def setResolution():
    global configuration
   
    if(isRS97()):
        configuration["screenWidth"] = 320
        configuration["screenHeight"] = 240
    
    #RS07 & K3P
    else:
        configuration["screenWidth"] = 480
        configuration["screenHeight"] = 272
    
    #windows platform or mac
    if(platform.processor() != ""):
        configuration["screenWidth"] = 320
        configuration["screenHeight"] = 240


def saveConfiguration():
        

    print("saving")
    try:
        subprocess.Popen(["sync"])
    except Exception:
        pass
         
    
    allConfig = copy.deepcopy(configuration)
    main = allConfig["mainMenu"]
    allConfig.pop('mainMenu', None)

    with open('config/config.json', 'w') as fp: 
        json.dump(allConfig, fp,sort_keys=True, indent=4)

    for index, item in enumerate(main):
        if( "source" not in item):
            fileName = "config/main/" + str(index).zfill(3) + " " +  item["name"] + "/config.json" 
        else:
            fileName = "config/main/" + item["source"] + "/config.json"

        if(item["type"] == "native"):
            data = item["data"]
            item.pop('data', None)
            for dataIndex, dataItem in enumerate(data):             
                saveTheme(dataItem)          

        if(item["type"] != "lastPlayed"):
            if "source" in item: del item["source"]
            if "emu" in item: del item["emu"]
            if "fileFilter" in item: del item["fileFilter"]



            saveTheme(item)
            storeConfigPart(fileName, item)
        elif(item["type"] == "lastPlayed"):
            dataName = "config/" + "main" + "/lastPlayed.json"
            if("data" in item): del item["data"]
            saveTheme(item)
            storeConfigPart(dataName, item)

       
    for l in listeners:
        l()

    print("Save finished")
       


def storeConfigPart(fileName, item):
    if not os.path.exists(os.path.dirname(fileName)):
        try:
            os.makedirs(os.path.dirname(fileName))
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise

    with open(fileName, 'w') as fp: 
        json.dump(item, fp,sort_keys=True, indent=4)

        

def getTheme():
    return theme

def toColor(input):
    return make_tuple(input)

def isRS97():
    return "type" in configuration["options"] and configuration["options"]["type"] == "RS97"

def addConfigChangedCallback(listener):
    listeners.append(listener)


def getPathData(path, data = None):
    if(data == None):
        data = configuration

    if path and data:
        args = path.split("/")
        element  = args[0]
        if element:
            newPath = '/'.join(args[1:])
            value = data.get(element)
            return value if len(args) == 1 else getPathData(value, newPath)

