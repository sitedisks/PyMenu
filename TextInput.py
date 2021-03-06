# -*- coding: utf-8 -*-
import RenderObject, Configuration, Footer
import os, Keys, RenderControl, TaskHandler
import pygame, sys


class TextInput(RenderObject.RenderObject):
    config = Configuration.getConfiguration()
    theme = Configuration.getTheme()
    pygame.font.init()
    footer = None
    background = None
    textFont = pygame.font.Font('theme/NotoSans-Regular.ttf', 20)


    buttonFont = pygame.font.Font('theme/NotoSans-Regular.ttf', int(config["screenWidth"] * 0.03))

    fontCache = {}

    buttonSurface = None

    selectedChar = "1"
    currentRow = 0
    currentCol = 0


    buttonWidth = config["screenWidth"] * 0.0625 #30px at 480px wide
    buttonHeight = buttonWidth
    buttonSpace = config["screenWidth"] * 0.02 #30px at 480px wide

    chars = []

    upperChars = []
    lowChars = []
    special = []
    lowChars.append(["1","2","3","4","5","6","7","8","9","0"])
    lowChars.append(["a","b","c","d","e","f","g","h","i","j"])
    lowChars.append(["k","l","m","n","o","p","q","r","s","t"])
    lowChars.append([u"\u2191",u"\u2026" , "u","v","w","x","y","z",  u"\u033A", "OK"])

    upperChars.append(["!","\"","§","$","%","&","/","(",")","="])
    upperChars.append(["A","B","C","D","E","F","G","H","I","J"])
    upperChars.append(["K","L","M","N","O","P","Q","R","S","T"])
    upperChars.append([u"\u2191",u"\u2026", "U","V","W","X","Y","Z",  u"\u033A", "OK"])

    special.append(["","","","","","","","","","?"])
    special.append(["°","^","","","","","","","+","*"])
    special.append(["<",">","","","","","","\\","'","#"])
    special.append(["",u"\u2026", ",",";",".",":","-","_", "", "OK"])

    chars = lowChars
   
    def initBackground(self):
        self.background = pygame.Surface((self.config["screenWidth"],self.config["screenHeight"]))
        self.background.fill((131,139,139))

        self.buttonSurface =  pygame.Surface((self.buttonWidth, self.buttonHeight))
        self.buttonSurface.fill((190,190,190))

        self.buttonSelectSurface =  pygame.Surface((self.buttonWidth, self.buttonHeight))
        self.buttonSelectSurface.fill((255,255,255))
    
    def renderTextField(self, screen):
        field = pygame.Surface((self.config["screenWidth"] - (self.config["screenWidth"] * 0.2) ,30))
        field.fill((255,255,255))

        textSurface = self.textFont.render(self.currentText, True, (0,0,0))
        field.blit(textSurface, (0, (field.get_height() - textSurface.get_height()) / 2))

        pygame.draw.line(field, (131,139,139), (textSurface.get_width(), 25),  (textSurface.get_width() + 10, 25), 2)

        textX = (self.config["screenWidth"] - field.get_width()) /2
        screen.blit(field, (textX,20))

    def renderButtons(self, screen):
        leftOffset = (self.config["screenWidth"] - 10* self.buttonWidth - 9 * self.buttonSpace) / 2

        yOffset = 80
        self.renderButtonLine(screen, self.chars[0],0, leftOffset, yOffset)
        yOffset+=self.buttonHeight+self.buttonSpace
        self.renderButtonLine(screen, self.chars[1],1, leftOffset, yOffset)
        yOffset+=self.buttonHeight+self.buttonSpace
        self.renderButtonLine(screen, self.chars[2],2, leftOffset, yOffset)
        yOffset+=self.buttonHeight+self.buttonSpace
        self.renderButtonLine(screen, self.chars[3],3, leftOffset, yOffset)

    def setFooter(self, footer):
        self.footer = footer

    def updateFooterPos(self, start, target, current, finished):
        if(not finished):
            self.footer.setYPosition(current)
        else:
            self.footer.setEnabled(False)
        
        RenderControl.setDirty()   

    def renderButtonLine(self, screen, line,row, xOffset, yOffset):
        offset = xOffset

        for i, char in enumerate(line):
            charSurface = self.fontCache.get(char)
            if(charSurface == None):
               charSurface = self.buttonFont.render(char, True, (0,0,0))
               self.fontCache[char] =  charSurface

            if(self.selectedChar == char and i == self.currentCol and row == self.currentRow):
                screen.blit(self.buttonSelectSurface, (offset, yOffset))
            else:
                screen.blit(self.buttonSurface, (offset, yOffset))

            charXOffset = (self.buttonWidth - charSurface.get_width()) / 2
            charYOffset = (self.buttonHeight - charSurface.get_height()) / 2
            screen.blit(charSurface, (offset + charXOffset, yOffset + charYOffset))
            offset = offset + self.buttonWidth + self.buttonSpace
    
    def setSelctedChar(self):
        if(self.currentRow < 0):
            self.currentRow = len(self.chars) - 1
        if(self.currentRow > len(self.chars) -1):
            self.currentRow = 0

        if(self.currentCol < 0):
            self.currentCol = len(self.chars[self.currentRow]) -1
        if(self.currentCol > len(self.chars[self.currentRow]) -1):
            self.currentCol = 0

        self.selectedChar = self.chars[self.currentRow][self.currentCol]

    def selectChar(self):

        #shif
        if(self.selectedChar == u"\u2191"):
            if(self.chars == self.lowChars):
                self.chars = self.upperChars
            else:
                self.chars = self.lowChars
            return

        #dots
        if(self.selectedChar == u"\u2026"):
            if(self.chars != self.special):
                self.chars = self.special
            else:
                self.chars = self.lowChars
            return

        #space
        if(self.selectedChar == u"\u033A"):
            self.currentText =  self.currentText + " "
            return

        #enter
        if(self.selectedChar == "OK" ):
            if(self.callback != None):
               self.callback(self.currentText)
            return
        
       
        self.currentText =  self.currentText + self.selectedChar
  

    def render(self, screen):
        screen.blit(self.background, (0,0))
        self.renderTextField(screen)
        self.renderButtons(screen)
        self.footer.render(screen)

    def handleEvents(self, events):
        for event in events:    
            if event.type == pygame.KEYDOWN:         
                if event.key == Keys.DINGOO_BUTTON_UP:
                    self.currentRow = self.currentRow - 1
                    self.setSelctedChar()
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_DOWN:
                    self.currentRow = self.currentRow + 1
                    self.setSelctedChar()
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_LEFT:
                    self.currentCol = self.currentCol - 1
                    self.setSelctedChar()
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_RIGHT:
                    self.currentCol = self.currentCol + 1
                    self.setSelctedChar()
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_A:
                    self.selectChar()
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_Y:
                    self.currentText = self.currentText[:-1] 
                    RenderControl.setDirty()
                if event.key == Keys.DINGOO_BUTTON_B:
                    if(self.callback != None):
                        self.callback(self.initialText)
                        RenderControl.setDirty()
            if event.type == pygame.KEYUP:
                if event.key == Keys.DINGOO_BUTTON_START:
                    if(self.callback != None):
                        self.callback(self.currentText)
                        RenderControl.setDirty()                   


    def __init__(self, screen, initialText, callback):
        self.screen = screen
        self.initialText = initialText
        self.currentText = str(initialText)
        self.callback = callback
        self.initBackground()
        self.setFooter(Footer.Footer([],[],(255,255,255)))
        TaskHandler.addAnimation(self.config["screenHeight"] - self.footer.getHeight(), self.config["screenHeight"], 600, self.updateFooterPos, 1000) 
     