import sys


def checker(checkThis, var):
    for i in var:
        checkThis = checkThis[i]
    if checkThis is None or checkThis == "":
        print("'" + i + "' is a required property")
        sys.exit(1)

def logger(text, sym):
    size = 61  # longest msg on code
    frame = sym * (size + 6)
    blank = sym+"  "+ " " * size + "  " + sym
    print("")
    print(frame)
    print(blank)
    if isinstance(text, list):
        for i in range(len(text)):
            textLine = text[i].strip()
            print(sym + "  " + textLine + " " * (size - len(textLine)) + "  " + sym)
    else:
        text = text.strip()
        print(sym + "  " + text + " " * (size - len(text)) + "  " + sym)
    print(blank)
    print(frame)
    print("")
