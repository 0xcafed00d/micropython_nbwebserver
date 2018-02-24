import usocket

ls = usocket.socket()
ls.setblocking(False)
ls.bind(('0.0.0.0', 80))
ls.listen(1)

s, addr = None, None

while True:
    try:
        print(".", end='')
        s, addr = ls.accept()
        break
    except OSError:
        pass


print(s, addr)

s.close()
