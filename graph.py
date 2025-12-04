import math
import button
import image
from constants import *
from bdd import askbdd

class Node():
    def __init__(self, button: button.Button, ip:str, mac:str, hostname:str, reliability:int = 0, debit:float = 0.0, ndiv:int = 0, nb_ping:int = 0, Onlinestatus: bool = True):
        self.button = button
        self.ip = ip
        self.mac = mac
        self.hostname = hostname
        self.debit = debit
        self.ndiv = ndiv
        self.nb_ping = nb_ping
        self.reliability = reliability
        self.OnlineStatus = Onlinestatus
        self.nb_error = 0
        self.button.AddImages(ConnextionFaildImage(), "0", 20, 20, 25, 20)
        self.total_error = 0
        self.total_ping = 0
        self.constructeur, self.adresse = askbdd.rechercher_constructeur(mac.replace(":", "-"))
        if not self.constructeur:
            self.constructeur = "???"
        if not self.adresse:
            self.adresse = "???"


        txt = [
        "Hostname : " + str(self.hostname),
        "IP : " + str(self.ip),
        "Mac : " + str(self.mac),
        "Debit : " + str(self.debit),
        "reliability : " + str(self.reliability),
        "failed : " + "XXX" + " / success : " + "XXX" + " / total : " + "XXX",
        "Constructeur : " + str(self.constructeur),
        "Adresse Constructeur : ",
        str(self.adresse),
        ]

        self.Midtxt = len(max(txt, key=len))

    def UpdatePing(self, debit, nb_div, error):
        if error:
            if self.nb_error > 3:
                self.OnlineStatus = False
                self.total_error += 1
                self.total_ping += 1
                return
            color = GetColorbyConnextion(self.debit)
            self.button.SetColor(color)
            self.button.SetOverlay(True, color)
            self.reliability = round(((((self.reliability / 100) * self.nb_ping) + 0) / (self.nb_ping + 1)) * 100)
            self.nb_ping += 1
            self.nb_error += 1
            self.total_error += 1
            self.total_ping += 1
            return
        self.nb_error = 0
        self.OnlineStatus = True
        self.reliability = round(((((self.reliability / 100) * self.nb_ping) + 1) / (self.nb_ping + 1)) * 100)
        self.nb_ping += 1
        self.debit = debit
        self.ndiv = nb_div
        self.total_ping += 1
        color = GetColorbyConnextion(self.debit)
        self.button.SetColor(color)
        self.button.SetOverlay(True, color)

    def MooveNode(self, indice, total, center, radius):
        left, top, axe = GetPos(indice, total, center=center, radius=radius)
        self.button.Moov(left=left, top=top)

def ConnextionFaildImage ():
    return image.LoadAssets.path + "/sigle/connextion_lost.png"

def GetColorbyConnextion (debit:float): # B/ms
    if not debit:
        return LIGHT_GREY
    debit *= 1000
    if debit < 1000000:
        green = 255/1000000
        return (255, int(debit * green), 5)
    else:
        if debit > 10000000:
            return (127, 255, 77)
        debit /= 1000000
        red = 255 - ((255 / 10) * debit)
        return (int(red), 255, 5)

def GetPos(current_node:int, total_node:int, radius:int = 400, center:tuple[int, int] = (0, 0)): #-> left:int, top:int
    x = math.cos(current_node * ((2 * math.pi) / total_node) - (math.pi / 2))
    y = math.sin(current_node * ((2 * math.pi) / total_node) - (math.pi / 2))
    if (total_node > 10) :
        if (current_node % 2 == 0):
            return int(x * radius) + center[0], int(y * radius) + center[1], y
        else:
            return int((x * radius) // 2) + center[0], int((y * radius) // 2) + center[1], y
    else:
        return int(x * radius) + center[0], int(y * radius) + center[1], y