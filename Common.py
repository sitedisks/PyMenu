
import pygame, sys, Configuration
import os, subprocess, platform
from threading import Thread


CLOCKSPEED = 628 #default clockspeed
imageCache = {}
gameList = {}
isLoaded = False


def loadGameListAsync():
    thread = Thread(target = loadGameList, args = ())
    thread.start()   

def loadGameList():
    global gameList
    global isLoaded

    if(isLoaded):
        return

    isLoaded = True
    try:
        print("Loading game list")
        with open("config/gamelist.txt") as f:
            lines = f.readlines() 
            for line in lines:
                try:
                    res = line.split("|")
                    gameList[res[1].strip() + ".zip"] = res[3].strip()    
                except Exception as ex:
                     print("Error adding game to list: " + line)               

       
    except Exception as ex:
        print("could not loa game list")
    
def clearLastPlayed():
    try:
        lastPlayed = json.load(open("config/lastPlayedData.json"))
        del lastPlayed["data"][:]
        with open('config/lastPlayedData.json', 'w') as fp: 
            json.dump(lastPlayed, fp,sort_keys=True, indent=4)
    except Exception as ex:
        print("Exception " + str(ex))
            
def getGameName(romName):
    global gameList
    if(romName in gameList and gameList[romName] != None):
        return gameList[romName]
    else:
        return romName


def loadImage(path): 

    if(path != None and os.path.exists(path)):
        try:
            return pygame.image.load(path)
        except Exception:
            print("Could not load image " + str(path) + " " + str(Exception))
            return  pygame.Surface((1,1),pygame.SRCALPHA)
      
    else:
        print("File not found " + str(path))

    return  pygame.Surface((1,1),pygame.SRCALPHA)

def getFPS():
    if(Configuration.isRS97() or platform.processor() == ""):
       return 30
    else:
       return 20



def loadCachedImage(path):
    global imageCache
    if(path in imageCache):
        return imageCache[path]
    else:
        image = loadImage(path)
        imageCache[path] = image
        return image

def aspect_scale(img, bx,by ):      
    ix,iy = img.get_size()
    if ix > iy:
        # fit to width
        scale_factor = bx/float(ix)
        sy = scale_factor * iy
        if sy > by:
            scale_factor = by/float(iy)
            sx = scale_factor * ix
            sy = by
        else:
            sx = bx
    else:
        # fit to height
        scale_factor = by/float(iy)
        sx = scale_factor * ix
        if sx > bx:
            scale_factor = bx/float(ix)
            sx = bx
            sy = scale_factor * iy
        else:
            sy = by

    return pygame.transform.scale(img, (int(sx),int(sy)) )

def mountSD(ext):
    pass

def umountSD(ext):
    pass

def mountUSB():
    if(platform.processor() != ""):
        return


    try:     
        fileName = "run"  
        file = open("/tmp/" + fileName,"w")
        file.write("#!/bin/sh\n")
        file.write("/etc/init.d/S99recovery storage on\n")       
        sys.exit()

    except Exception as ex:
        print("mount exception " + str(ex))

def gmenu2x():
    try:     
        fileName = "run"  
        file = open("/tmp/" + fileName,"w")
        file.write("#!/bin/sh\n")
        file.write("cd /home/retrofw/apps/gmenu2x\n")     
        file.write("./gmenu2x\n")     

        sys.exit()

    except Exception as ex:
        print("mount exception " + str(ex))

def blitMultilineText(surface, text, pos, font, color=pygame.Color('black')):
    words = [word.split(' ') for word in text.splitlines()]  # 2D array where each row is a list of words.
    space = font.size(' ')[0]  # The width of a space.
    max_width, max_height = surface.get_size()
    x, y = pos
    for line in words:
        for word in line:
            word_surface = font.render(word, 0, color)
            word_width, word_height = word_surface.get_size()
            if x + word_width >= max_width:
                x = pos[0]  # Reset the x.
                y += word_height  # Start on new row.
            surface.blit(word_surface, (x, y))
            x += word_width + space
        x = pos[0]  # Reset the x.
        y += word_height  # Start on new row.

def quick_sort(items):
        """ Implementation of quick sort """
        if len(items) > 1:
                pivot_index = int(len(items) / 2)
                smaller_items = []
                larger_items = []
 
                for i, val in enumerate(items):
                        if i != pivot_index:
                                if val < items[pivot_index]:
                                        smaller_items.append(val)
                                else:
                                        larger_items.append(val)
 
                quick_sort(smaller_items)
                quick_sort(larger_items)
                items[:] = smaller_items + [items[pivot_index]] + larger_items
