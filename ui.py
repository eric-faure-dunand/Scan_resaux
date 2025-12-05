#!/bin/env python3
import pygame
from constants import *
from button import Button
import scan
import graph
import threading
import math

def draw_txt(surface, font, text, color, x, y):
    txt = font.render(text, True, color)
    surface.blit(txt, txt.get_rect(center=(x, y)))
    

def GetColorByReliability(reliability: int):
    if not reliability:
        return (220, 0, 0) # 1.16 * 220 = 225
    if reliability < 50:
        return (220, int((110 / 50) * reliability), 0)
    if  reliability < 75:
        return (220, int((220 / 75) * reliability), 0)
    else:
        return (int(220 - (220 / 100) * reliability), 220, 0)

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Scan reseau")
    clock = pygame.time.Clock()
    cmpt_tick = 0

    font = pygame.font.SysFont(None, 32)
    small_font = pygame.font.SysFont(None, 25)

    state = "menu"
    want_quite = False

    ScanThread = threading.Thread(target=scan.main, args=())
    scaning = False
    PingThread = None
    pinging = False
    ping_evry = 60
    device_tab =[]
    shaw_ghost = False

    radius = 400
    PaddingLeft = 0
    PaddingTop = 0

    show_debit = True
    Button_ShowDebit = Button(5, 5, WIDTH / 15, HEIGHT / 20, LIGHT_GREY, OutlineSize=1, message="debit : ON", font=small_font)
    Button_ShowDebit.SetOverlay(Overlay=True, OutlineColor=WHITE, TextColor=WHITE)
    show_ipv4 = False
    Button_ShowIpv4 = Button(5, 5 * 2 + HEIGHT / 20, WIDTH / 15, HEIGHT / 20, MID_DARK_GREY, OutlineSize=1, message="IPv4 : OFF", font=small_font)
    Button_ShowIpv4.SetOverlay(Overlay=True, OutlineColor=WHITE, TextColor=WHITE)
    show_Mac = False
    Button_ShowMac = Button(5, 5 * 3 + (HEIGHT / 20) * 2, WIDTH / 15, HEIGHT / 20, MID_DARK_GREY, OutlineSize=1, message="Mac : OFF", font=small_font)
    Button_ShowMac.SetOverlay(Overlay=True, OutlineColor=WHITE, TextColor=WHITE)
    show_reliability = False
    Button_ShoweReliability = Button(5, 5 * 4 + (HEIGHT / 20) * 3, WIDTH / 12, HEIGHT / 20, MID_DARK_GREY, OutlineSize=1, message="Fiabilité : OFF", font=small_font)
    Button_ShoweReliability.SetOverlay(Overlay=True, OutlineColor=WHITE, TextColor=WHITE)

    Button_PingEveryPLus = Button(170, HEIGHT - 20, 15, 15, DARK_GREY, OutlineSize=1, message="+", font=small_font)
    Button_PingEveryPLus.SetOverlay(True, LIGHT_GREY, BLACK, 2, BLACK)
    Button_PingEveryMoins = Button(215, HEIGHT - 20, 15, 15, DARK_GREY, OutlineSize=1, message="-", font=small_font)
    Button_PingEveryMoins.SetOverlay(True, LIGHT_GREY, BLACK, 2, BLACK)

    EscapeRect = Button((WIDTH / 2) - ((WIDTH / 20) + WIDTH / 10), (HEIGHT / 2) - ((HEIGHT / 20) - HEIGHT / 10), WIDTH / 10, HEIGHT / 10, GREY, message="Cancel [ESCAPE]", font=small_font, OutlineSize=2)
    EscapeRect.SetOverlay(True, GREEN, OutlineSize=1)
    EnterRect = Button((WIDTH / 2) - ((WIDTH / 20) - (WIDTH / 10)), (HEIGHT / 2) - ((HEIGHT / 20) - HEIGHT / 10), WIDTH / 10, HEIGHT / 10, GREY, message="Quit [ENTER]", font=small_font, OutlineSize=2)
    EnterRect.SetOverlay(True, RED, OutlineSize=1)
    ScanButton = Button((WIDTH / 2) - (WIDTH / 10) / 2, (HEIGHT / 2) - (HEIGHT / 10) / 2, WIDTH / 10, HEIGHT / 10, MID_DARK_GREY, OutlineSize=2, message="Scan", font=font)
    ScanButton.SetOverlay(True,LIGHT_GREY, WHITE, 1)

    ShawllAllStats = False
    CloseAllStats = Button((WIDTH - 25), HEIGHT - 190, 20, 20, RED, BLACK, 1, "X", DARK_GREY, small_font)
    CloseAllStats.SetOverlay(True, OutlineSize=2, TextColor=BLACK)
    mactoshaw = None

    while True:
        screen.fill(WHITE)
        mx, my = pygame.mouse.get_pos()

        for event in pygame.event.get():
            keys = pygame.key.get_pressed()

            if event.type == pygame.QUIT and not ScanThread.is_alive():
                pygame.quit()
                exit(0)
            if want_quite == True and not ScanThread.is_alive():
                if (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN) or (EnterRect.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    pygame.quit()
                    exit(0)
                if (EscapeRect.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    want_quite = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not ScanThread.is_alive():
                if want_quite == True:
                    want_quite = False
                else:
                    want_quite = True
            
            if state == "menu" and not want_quite :
                if (ScanButton.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1) or (event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN):
                    state = "scaning"
                    scaning = True
                    ScanThread.start()

            if state == "graph":
                if (ScanButton.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1) and not ScanThread.is_alive():
                    ScanThread = threading.Thread(target=scan.main, args=())
                    scaning = True
                    ScanButton.NewText("Scanning ...", font)
                    ScanButton.SetColor(GREY)
                    ScanThread.start()
                
                if event.type == pygame.MOUSEWHEEL :
                    radius += event.y * 15
                    if radius < 200:
                        radius = 200
                    elif radius > 600:
                        radius = 600
                    MoovDeviceGraph()

                if event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    radius = 400
                    PaddingLeft = 0
                    PaddingTop = 0
                    MoovDeviceGraph()

                if (Button_ShowDebit.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    show_debit = False if show_debit else True
                    if show_debit:
                        Button_ShowDebit.SetColor(LIGHT_GREY)
                        Button_ShowDebit.NewText("Debit : ON")
                        Button_ShowDebit.SetOverlay(True, OverlayColor=LIGHT_GREY)
                    else :
                        Button_ShowDebit.SetColor(MID_DARK_GREY)
                        Button_ShowDebit.NewText("Debit : OFF")
                        Button_ShowDebit.SetOverlay(True, OverlayColor=MID_DARK_GREY)

                if (Button_ShowIpv4.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    show_ipv4 = False if show_ipv4 else True
                    if show_ipv4:
                        Button_ShowIpv4.SetColor(LIGHT_GREY)
                        Button_ShowIpv4.NewText("IPv4 : ON")
                        Button_ShowIpv4.SetOverlay(True, OverlayColor=LIGHT_GREY)
                    else :
                        Button_ShowIpv4.SetColor(MID_DARK_GREY)
                        Button_ShowIpv4.NewText("IPv4 : OFF")
                        Button_ShowIpv4.SetOverlay(True, OverlayColor=MID_DARK_GREY)

                if (Button_ShowMac.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    show_Mac = False if show_Mac else True
                    if show_Mac:
                        Button_ShowMac.SetColor(LIGHT_GREY)
                        Button_ShowMac.NewText("Mac : ON")
                        Button_ShowMac.SetOverlay(True, OverlayColor=LIGHT_GREY)
                    else :
                        Button_ShowMac.SetColor(MID_DARK_GREY)
                        Button_ShowMac.NewText("Mac : OFF")
                        Button_ShowMac.SetOverlay(True, OverlayColor=MID_DARK_GREY)
                
                if (Button_ShoweReliability.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1):
                    show_reliability = False if show_reliability else True
                    if show_reliability:
                        Button_ShoweReliability.SetColor(LIGHT_GREY)
                        Button_ShoweReliability.NewText("Fiabilité : ON")
                        Button_ShoweReliability.SetOverlay(True, OverlayColor=LIGHT_GREY)
                    else :
                        Button_ShoweReliability.SetColor(MID_DARK_GREY)
                        Button_ShoweReliability.NewText("Fiabilité : OFF")
                        Button_ShoweReliability.SetOverlay(True, OverlayColor=MID_DARK_GREY)
                
                if Button_PingEveryPLus.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    ping_evry += 10 if ping_evry < 120 else 0
                if Button_PingEveryMoins.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    ping_evry -= 10 if ping_evry > 10 else 0

                if CloseAllStats.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                    ShawllAllStats = False

                for node in device_tab:
                   if node.button.PointIsIn(mx, my) and event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                       ShawllAllStats = True
                       mactoshaw = node.mac

        if state == "scaning" :
            if ScanThread.is_alive() :
                scaning = True
                pass
            else :
                ScanThread.join()
                scaning = False
                device_tab.clear()
                CreateDeviceGraph()
                ScanButton.Moov(left= WIDTH - (WIDTH / 10), top=0)
                state = "graph"
        
        if ScanThread.is_alive() :
            pass
        elif scaning :
            ScanThread.join()
            scaning = False
            ScanButton.NewText("Scan", font)
            ScanButton.SetColor(MID_DARK_GREY)
            CreateDeviceGraph()

        if state == "graph" and not want_quite:
            cmpt_tick += 1
        if (cmpt_tick % (ping_evry * 60) == 0) and state == "graph" and not pinging: # cmpt_tick == seconde * 60fps
            PingThread = threading.Thread(target=Pingdebit)
            print("ping")
            PingThread.start()
            pinging = True
            
        if PingThread and not PingThread.is_alive() and pinging:
            PingThread.join()
            pinging = False
            cmpt_tick = 0


        if state == "graph":
            keys = pygame.key.get_pressed()
            if keys[pygame.K_RIGHT]:
                PaddingLeft -= 12 if PaddingLeft > -300 else 0
                MoovDeviceGraph()
            if keys[pygame.K_LEFT]:
                PaddingLeft += 12 if PaddingLeft < 300 else 0
                MoovDeviceGraph()
            
            if keys[pygame.K_DOWN]:
                PaddingTop -= 12 if PaddingTop > -300 else 0
                MoovDeviceGraph()
            if keys[pygame.K_UP]:
                PaddingTop += 12 if PaddingTop < 300 else 0
                MoovDeviceGraph()


        match state:
            case "menu" :
                screen.fill(DARK_GREY)

                ScanButton.Draw(screen, IgnoreOvelay=want_quite)

            case "scaning":
                screen.fill(GREY)
                draw_txt(screen, font, "Chargement ...", BLACK, WIDTH /2, HEIGHT /2)

            case "graph" :
                screen.fill(GREY)
                padding_debit = 15
                padding_ip4 = 30 if show_debit else 15 
                padding_ip6 = (45 if show_debit and show_ipv4 else (30 if show_ipv4 or show_debit else 15))
                for device in device_tab:
                    device.button.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False, DrawImagebyId= ["0"] if not device.OnlineStatus else [])
                    on = device.button.PointIsIn(mx, my)
                    pos = device.button.GetTextPosition()
                    relativ_pos = device.button.GetTextRelativePosition()
                    if show_reliability:
                        color = GetColorByReliability(device.reliability)
                        on_color = (int(color[0] * 1.16), int(color[1] * 1.16), 0)
                        GlobalBounds = device.button.GetGlobalBounds()
                        match relativ_pos:
                            case "over":
                                draw_txt(screen, small_font, f"{device.reliability}%", on_color if on and not want_quite else color, GlobalBounds[0] + (GlobalBounds[2] / 2), GlobalBounds[1] + GlobalBounds[3] + padding_debit)
                            case "under":
                                draw_txt(screen, small_font, f"{device.reliability}%", on_color if on and not want_quite else color, GlobalBounds[0] + (GlobalBounds[2] / 2), GlobalBounds[1] - padding_debit)
                    if show_debit:
                        match relativ_pos:
                            case "over":
                                draw_txt(screen, small_font, (f"{(device.debit/ 1000):.3} MB/s") if device.debit else "connextion error", BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] - padding_debit)
                            case "under":
                                draw_txt(screen, small_font, (f"{(device.debit/ 1000):.3} MB/s") if device.debit else "connextion error", BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] + padding_debit)
                    if show_ipv4:
                        match relativ_pos:
                            case "over":
                                draw_txt(screen, small_font, device.ip, BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] - padding_ip4)
                            case "under":
                                draw_txt(screen, small_font, device.ip, BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] + padding_ip4)
                    if show_Mac:
                        match relativ_pos:
                            case "over":
                                draw_txt(screen, small_font, device.mac, BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] - padding_ip6)
                            case "under":
                                draw_txt(screen, small_font, device.mac, BLACK if on and not want_quite else DARK_GREY, pos[0], pos[1] + padding_ip6)

                if ShawllAllStats:
                    CloseAllStats.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                    height = HEIGHT - 150
                    node = next((n for n in device_tab if n.mac == mactoshaw), None)
                    width = WIDTH - ((node.Midtxt / 2) * 10) - 5
                    if node :
                        draw_txt(screen, small_font, "Hostname : " + str(node.hostname), BLACK, width, height)
                        draw_txt(screen, small_font, "IP : " + str(node.ip), BLACK, width, height + 15)
                        draw_txt(screen, small_font, "Mac : " + str(node.mac), BLACK, width, height + 30)
                        draw_txt(screen, small_font, "Debit : " + (f"{(node.debit/ 1000):.3} MB/s"), BLACK, width, height + 45)
                        draw_txt(screen, small_font, "reliability : " + str(node.reliability) + "%", BLACK, width, height + 60)
                        draw_txt(screen, small_font, "Ping : ", BLACK, width, height + 75) 
                        draw_txt(screen, small_font, "failed : " + str(node.total_error) + " / success : " + str(node.total_ping - node.total_error) + " / total : " + str(node.total_ping), BLACK, width, height + 90)
                        draw_txt(screen, small_font, "Constructeur : " + str(node.constructeur), BLACK, width, height + 105)
                        draw_txt(screen, small_font, "Adresse Constructeur : ", BLACK, width, height + 120) 
                        draw_txt(screen, small_font, str(node.adresse), BLACK, width, height + 135)


                ScanButton.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                Button_ShowDebit.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                Button_ShowIpv4.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                Button_ShowMac.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                Button_ShoweReliability.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                
                Button_PingEveryPLus.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                Button_PingEveryMoins.Draw(screen, IgnoreOvelay= True if ScanThread.is_alive() else False)
                draw_txt(screen, small_font, f"Update debit every      {ping_evry}      secondes", BLACK, 160, HEIGHT - 10)
                
            case _:
                screen.fill(GREY)
                draw_txt(screen, font, "ERROR : THIS SCREEN IS NOT ABEL TO BE SHAW. PLEASE CLOSE AND RE-OPEN \'SCAN RESEAU\'", BLACK, WIDTH /2, HEIGHT /2)

        if want_quite:
            #pygame.draw.rect(screen, "#FFFFFF50", pygame.Rect(0, 0, WIDTH, HEIGHT))
            pygame.draw.rect(screen, LIGHT_GREY, pygame.Rect((WIDTH / 2) - (WIDTH / 5), (HEIGHT / 2) - (HEIGHT / 5), WIDTH / 2.5, HEIGHT / 2.5))
            pygame.draw.rect(screen, BLACK, pygame.Rect((WIDTH / 2) - (WIDTH / 5), (HEIGHT / 2) - (HEIGHT / 5), WIDTH / 2.5, HEIGHT / 2.5), 2)
            draw_txt(screen, font, "Are you sure you want to quit Scan Reseau", BLACK, (WIDTH / 2), (HEIGHT / 2) - (HEIGHT / 10))

            EnterRect.Draw(screen)
            EscapeRect.Draw(screen)

        def CreateDeviceGraph():
            scan_devices = scan.park + (scan.ghost if shaw_ghost else [])
            nb_node = len(scan_devices)
            for i in range (0, len(scan_devices)):
                if all(scan_devices[i]["name"] != d.hostname for d in device_tab) :
                    left, top, axe = graph.GetPos(i, nb_node, center=(WIDTH / 2 + PaddingLeft, HEIGHT / 2 + PaddingTop), radius= radius)
                    new_device = Button(left=left, top=top, width=30, height=30, OutlineColor=DARK_GREY, color=LIGHT_GREY, OutlineSize=1, message=scan_devices[i]["name"].replace(".home", ""), TextColor=DARK_GREY, font=small_font,TextPosition="under" if axe > 0 else "over", TextePaddingTop= 7 if axe > 0 else -7)
                    new_device.SetOverlay(True, OutlineSize=2, OutlineColor=WHITE,TextColor=BLACK)
                    device_tab.append(graph.Node(new_device, scan_devices[i]["ip"], scan_devices[i]["mac"], scan_devices[i]["name"]))

            device_tab.sort(key=lambda x: x.hostname)
            PingThread = threading.Thread(target=Pingdebit)
            PingThread.start()
            pinging = True
            MoovDeviceGraph()

        def MoovDeviceGraph():
            nb_node = len(device_tab)
            for i, device in enumerate(device_tab):
                device.MooveNode(i, nb_node, (WIDTH / 2 + PaddingLeft, HEIGHT / 2 + PaddingTop), radius)

        def Pingdebit():
            for d in device_tab:
                debit, nbdiv, error = scan.AdjustMoyenneDebit(d.ip, d.debit, d.ndiv)
                d.UpdatePing(debit, nbdiv, error)


        pygame.display.flip()
        clock.tick(60)