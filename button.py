#!/bin/env/ python3
import pygame
from constants import *
import image

class Button():
    def __init__(self, left, top, width, height, color = (0, 0, 0, 0), OutlineColor = BLACK, OutlineSize = -1, message = "", TextColor = BLACK, font = None, TextPosition:str = "center", TextePaddingTop:int = 0, TextePaddingLeft:int = 0):
        self.left = left
        self.top = top
        self.width = width
        self.height = height
        self.color = color
        self.OutlineColor = OutlineColor
        self.OutlineSize = OutlineSize

        self.images = []

        self.message = message
        self.TextColor = TextColor
        self.font = font
        self.TextPosition = TextPosition
        self.TextePaddingTop = TextePaddingTop
        self.TextePaddingLeft = TextePaddingLeft

        self.rect = pygame.Rect(left, top, width, height)
        if font :
            self.text = self.font.render(message, True, TextColor)
        else :
            self.text = None

        self.Overlay = False
        self.OverlayColor = color
        self.OverlayOutlineColor = OutlineColor
        self.OverlayOutlineSize = OutlineSize
        self.OverlayTextColor = TextColor

    def SetOverlay(self, Overlay:bool, OverlayColor=None, OutlineColor=None, OutlineSize=None, TextColor=None):
        self.Overlay = Overlay
        if not self.Overlay:
            return
        if OverlayColor:
            self.OverlayColor = OverlayColor
        if OutlineColor:
            self.OverlayOutlineColor = OutlineColor
        if OutlineSize:
            self.OverlayOutlineSize = OutlineSize
        if TextColor:
            self.OverlayTextColor = TextColor 

    def AddImages(self, path, id, paddingtop:int = 0, paddingleft:int=0, width:int = -1, height:int = -1):
        self.images.append(image.Image(self.left + paddingleft, self.top + paddingtop, path, id, width, height))

    def Draw(self, surface, IgnoreOvelay:bool = False, DrawAllImages:bool = False, DrawImagebyId:list = []):

        def GetPosText(self):
            match self.TextPosition:
                case "center":
                    return self.text.get_rect(center=(self.left + (self.width / 2) + self.TextePaddingLeft, self.top + (self.height / 2) + self.TextePaddingTop))
                case "over" :
                    return self.text.get_rect(center=(self.left + (self.width / 2) + self.TextePaddingLeft, self.top + self.TextePaddingTop))
                case "under" :
                    return self.text.get_rect(center=(self.left + (self.width / 2) + self.TextePaddingLeft, self.top + self.height + self.TextePaddingTop))

        if self.rect.collidepoint(pygame.mouse.get_pos()) and self.Overlay and not IgnoreOvelay :
            pygame.draw.rect(surface, self.OverlayColor, self.rect)
            if self.OutlineSize > 0 :
                pygame.draw.rect(surface, self.OverlayOutlineColor, self.rect, self.OverlayOutlineSize)
            if DrawAllImages:
                for img in self.images:
                    img.Draw(surface) 
            else :
                for img in self.images:
                    if img.id in DrawImagebyId:
                        img.Draw(surface)
            if self.text :
                self.text = self.font.render(self.message, True, self.OverlayTextColor)
                surface.blit(self.text, GetPosText(self))
        else :
            pygame.draw.rect(surface, self.color, self.rect)
            if self.OutlineSize > 0 :
                pygame.draw.rect(surface, self.OutlineColor, self.rect, self.OutlineSize)
            if DrawAllImages:
                for img in self.images:
                    img.Draw(surface) 
            else :
                for img in self.images:
                    if img.id in DrawImagebyId:
                        img.Draw(surface)
            if self.text :
                self.text = self.font.render(self.message, True, self.TextColor)
                surface.blit(self.text, GetPosText(self))

    def PointIsIn(self, x:int, y:int):
        if self.rect.collidepoint(x, y) :
            return True
        else :
            return False

    def Moov(self, left:int, top:int):
        left_moov = left - self.left
        top_moov = top - self.top
        self.left = left
        self.top = top
        self.rect = pygame.Rect(left, top, self.width, self.height)
        for img in self.images:
            img.Moov((left_moov, top_moov))
        if self.font :
            self.text = self.font.render(self.message, True, self.TextColor)
        else :
            self.text = None

    def NewText(self, message:str, NewFont = None ,NewTextColor = None, NewTextPosition:str = None, TextePaddingTop:int = None, TextePaddingLeft:int = None):
        self.message = message
        if NewTextColor:
            self.TextColor = NewTextColor
        if NewFont:
            self.font = NewFont
        if  NewTextPosition:
            self.TextPosition = NewTextPosition
        if TextePaddingTop:
            self.TextePaddingTop = TextePaddingTop
        if TextePaddingLeft:
            self.TextePaddingLeft = TextePaddingLeft

        if self.font:
            self.text = self.font.render(message, True, self.TextColor)

    def GetCenter(self):
        return(self.left + (self.width / 2), self.top + (self.height / 2))

    def GetGlobalBounds(self):
        return (self.left, self.top, self.width, self.height)
    
    def SetOutlineColor(self, NewOutlineColre):
        self.OutlineColor = NewOutlineColre

    def SetColor(self, NewColor):
        self.color = NewColor

    def GetTextPosition(self):
         match self.TextPosition:
            case "center":
                return self.left + (self.width / 2) + self.TextePaddingLeft, self.top + (self.height / 2) + self.TextePaddingTop
            case "over" :
                return self.left + (self.width / 2) + self.TextePaddingLeft, self.top + self.TextePaddingTop
            case "under" :
                return self.left + (self.width / 2) + self.TextePaddingLeft, self.top + self.height + self.TextePaddingTop
    
    def GetTextRelativePosition(self):
        return self.TextPosition