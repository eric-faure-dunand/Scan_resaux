#! bin/python3
import socket
import threading
import subprocess, time
import platform
import re
import os

park = []
ghost = []

def get_mac_from_arp_table_Windows(ip :str):
    try:
        hostname, alias, addressliste = socket.gethostbyaddr(ip)
    except Exception:
        hostname = None
    try:
        out = subprocess.check_output(["arp", "-a"], text=True)
        for line in out.splitlines():
            if ip in line:
                m = re.search(r"([0-9A-Fa-f\-]{17})", line)
                if m:
                    return m.group(1).replace("-", ":").lower(), hostname
    except Exception:
        pass
    return None, hostname

def get_mac_from_arp_table_linux(ip : str):
    try:
        hostname, alias, addressliste = socket.gethostbyaddr(ip)
    except Exception:
        hostname = None
    try:
        out = subprocess.check_output(["ip", "neigh", "show", ip], text=True)
        m = re.search(r"lladdr\s+([0-9a-f:]{17})", out)
        if m:
            return m.group(1), hostname
    except Exception:
        pass
    try:
        out = subprocess.check_output(["arp", "-n", ip], text=True)
        m = re.search(r"([0-9a-f:]{17})", out)
        if m:
            return m.group(1), hostname
    except Exception:
        pass
    return None, hostname

def get_mac(ip: str):
    if (platform.system() == "Windows"):
        try:
            result = subprocess.run(["ping", "-n", "1", ip], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(str(e))
            return None, None
        if result.returncode != 0 or "Impossible de joindre" in str(result.stdout) or "Request timed out" in str(result.stdout):
            print("error return or destination host unreachable, ip = ", ip)
            return None, None
        time.sleep(0.5)
        return get_mac_from_arp_table_Windows(ip)
    elif (platform.system() == "Linux"):
        try:
            result = subprocess.run(["ping", "-c", "1", ip], check=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except Exception as e:
            print(str(e))
            return None, None
        if result.returncode != 0:
            print("error return", result.returncode)
            return None, None
        time.sleep(0.5)
        return get_mac_from_arp_table_linux(ip)
    else :
        print("OS not supported, run \'Scan Reseau\' on another device")
        return None, None

def ping_range (host : str, x : int, y : int):
    for ping in range(x, y):
        address = host + str(ping)
        socket.setdefaulttimeout(2)
        mac, hostname = get_mac(address)
        if mac and hostname:
            park.append({"ip": address, "mac" : mac, "name" : hostname})
        elif mac or hostname :
            ghost.append({"ip": address, "mac" : mac if mac else "", "name" : hostname if hostname else ""})

def create_ping_thread(nb_tread:int, host:str, start:int=0, end:int=254):
    if nb_tread > 254 :
        nb_tread = 254
    ratio = 254 // nb_tread
    tread_tab = [threading.Thread(target=ping_range, args=(host, (ratio * i), (ratio * (i + 1)))) for i in range (0, nb_tread)]
    if (255 - (ratio * (nb_tread))>= 1):
        tread_tab.append(threading.Thread(target=ping_range, args=(host, ratio * nb_tread, 255)))
    return tread_tab

def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip = (s.getsockname()[0])
    s.close()
    return ip

def AdjustMoyenneDebit(ip, moyenne, nombremoyenne):
    if not moyenne:
        moyenne = 0
        nombremoyenne = 0
    moyenne *= nombremoyenne
    match platform.system():
        case "Linux":
            try:
                result = subprocess.check_output(["ping", "-c", "1", "-s", "10000", ip], text=True)
            except Exception as e: 
                print(str(e))
                return moyenne, nombremoyenne, 1
            for line in result.splitlines():
                if " bytes" in line:
                    bytes = re.search(r"(\d+) bytes", line)
                if "time=" in line:
                    time = re.search(r"time=(\d+\.\d+) ms", line)
                    if not time:
                        time = re.search(r"time=(\d+) ms", line)
            if not bytes or not time:
                return moyenne, nombremoyenne, 1
            else:
                try:
                    debit = int(bytes.group(1)) / float(time.group(1))
                except Exception:
                    return moyenne, nombremoyenne, 1
                moyenne += debit
                return moyenne / (nombremoyenne + 1), nombremoyenne + 1, 0
        case "Windows":
            try:
                result = subprocess.check_output(["ping", "-n", "1", "-l", "10000", ip], text=True)
            except Exception as e:
                print(str(e))
                return moyenne, nombremoyenne, 1
            bytes = None
            time = None
            for line in result.splitlines():
                if "octets=" in line:
                    bytes = re.search(r"octets=(\d+)", line)
                if "temps=" in line:
                    time = re.search(r"temps=(\d+) ms", line)
            if not bytes or not time:
                return moyenne, nombremoyenne, 1
            else:
                try:
                    debit = int(bytes.group(1)) / float(time.group(1))
                except Exception:
                    return moyenne, nombremoyenne, 1
                moyenne += debit
                return moyenne / (nombremoyenne + 1), nombremoyenne + 1, 0
        case _ :
            print("Your device is not able to know the debit connextion")
            return moyenne, nombremoyenne, 1
    

def main():
    global park
    global ghost
    park.clear()
    ghost.clear()
    host = (get_ip()).rsplit('.', 1)[0] + "."
    path = os.path.dirname(os.path.abspath(__file__)) + "/log/logscan.txt"
    log = open(path, "w")
    if not log:
        log = open(path, "x")
    treads_array = create_ping_thread(254, host)

    for i in range(len(treads_array)):
        treads_array[i].start()
        print("tread ", i, " started", file=log)

    print("----JOINS----", file=log)
    for i in range(len(treads_array)):
        treads_array[i].join()
        print("tread ", i, " closed", file=log)

    for r in sorted(park, key=lambda x: tuple(int(p) for p in x["ip"].split("."))):
        print(r["ip"].ljust(16), r["mac"].ljust(18), (r["name"] or "-")[:34].ljust(35), file=log)
    print("\n\nGHOST\n", file=log)
    for r in sorted(ghost, key=lambda x: tuple(int(p) for p in x["ip"].split("."))):
        print(r["ip"].ljust(16), r["mac"].ljust(18), (r["name"] or "-")[:34].ljust(35), file=log)
    log.close()
    park.sort(key=lambda x: x["name"])
    ghost.sort(key=lambda x: x["name"])
    exit(0)