#! /bin/python3
import platform
import subprocess

if __name__ == "__main__" :
    import sys
    
    if (len(sys.argv) > 1):
        if (len(sys.argv) == 2 and (sys.argv[1] == "-h" or sys.argv[1] == "-help")) :
            print("Scan reseaux don't take any arguments\n\nTRY :\n\t./main.py\n\nEnjoy")
            exit(0)
        print("Arguments error : To many arguments")
        exit(1)
    
    if (platform.system() == "Linux"):
        try :
            subprocess.run(["sudo", "ip", "neigh", "flush", "all"])
        except Exception:
            pass
    import image
    image.LoadAssets()

    import ui

    ui.main()