import socket
import sys

print(len(sys.argv))

if len(sys.argv) < 3:
    print("add input argumaens [host] [port]")
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("listening...")
        c,addr = s.accept()
        with c:
            print(f"Connection established: {addr}")
            print(f"{c.recv(1024).decode()}")
            while 1:
                val = input("RGB:")
                c.send(val.encode())
                if val == "exit":
                    break
except KeyboardInterrupt:
    s.close()
    print("\nExit...")