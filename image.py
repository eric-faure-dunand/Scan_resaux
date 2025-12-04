import pygame
import os

class Image:
    def __init__(self, left:int, top:int, path:str, id:str, width:int = -1, height:int = -1):
        self.left = left
        self.top = top 
        self.path = path
        self.id = id

        if os.path.exists(path):
            self.img = pygame.image.load(path)
            w, h = self.img.get_size()
            if height > 0:
                self.height = height
            else:
                self.height = h
            if width > 0:
                self.width = width
            else:
                self.width = w
            if self.width != w or self.height != h :
                self.img = pygame.transform.scale(self.img, (self.width, self.height))
        else :
            print("File not found : ", path, " doesn't exist")
            self.img = None

    def Draw(self, surface):
        if not self.img:
            return
        surface.blit(self.img, (self.left, self.top))

    def SetPosition(self, newleft:int, newtop:int):
        self.left = newleft
        self.top = newtop

    def Moov(self, Vector:tuple):
        self.left += Vector[0]
        self.top += Vector[1]

    def SetScale(self, Width, height):
        self.width = Width
        self.height = height
        self.img = pygame.transform.scale(self.img, (self.width, self.height))

def LoadAssets():
    if not hasattr(LoadAssets, "path") :
        LoadAssets.path =  os.path.dirname(os.path.abspath(__file__)) + "/assets"