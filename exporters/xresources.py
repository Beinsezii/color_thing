NAME="X11 Resources"
FORMAT=".Xresources"

def EXPORT(*args):
    return bytes(f"exporting .Xresources ... {args}", encoding="UTF-8")

