NAME="GIMP Palette"
FORMAT=".gpl"

def EXPORT(*args):
    return bytes(f"exporting GIMP palette... {args}", encoding="UTF-8")
