import socket
import sys
import cv2
import mediapipe as mp
import time
import json
import math

# find the percentage of the inbetween value of min and max values 
def findPercents(inp, mi, ma, v):
    va = (inp - mi) * 100 / (ma - mi)
    if v == 100:
        va = v - va
    if va > 100:
        return 100
    elif va < 0:
        return 0
    else:
        return int(va)

# get host and port for the server as argument if not throught error
if len(sys.argv) < 3:
    print("add input argumaens [host] [port]")
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

# videocapture initialization
Wcam, Hcam = 640, 480
pTime = 0
cTime = 0
cap = cv2.VideoCapture(0)
mpHande = mp.solutions.hands
hands = mpHande.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

cap.set(3, Wcam)
cap.set(4, Hcam)

# first try to initialization the socket server
try:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen(1)
        print("waiting for connection...")
        client, addr = s.accept()
        with client:
            # when client connects to the server videocapture start
            print(f"Connection established: {addr}")
            print(f"{client.recv(1024).decode()}")
            while 1:
                success, img = cap.read()
                imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                result = hands.process(imgRGB)
                li = []

                # find the hand and position with its 20 points
                if result.multi_hand_landmarks:
                    for handLms in result.multi_hand_landmarks:
                        for id, lm in enumerate(handLms.landmark):
                            h, w, c = img.shape
                            cx, cy = int(lm.x*w), int(lm.y*h)
                            # Id, x, y axis of the point
                            li.append([cx, cy])
                        # this below line for the 21 dots and connection between them
                        # mpDraw.draw_landmarks(
                        #     img, handLms, mpHande.HAND_CONNECTIONS)
                rgb = [100,100,100]
                Rlen = Glen = Blen = [0,0]
    
                if li:
                    # rgb x and y axis point
                    x0, y0 = li[0][0], li[0][1]
                    rx, ry = li[4][0], li[4][1]
                    gx, gy = li[8][0], li[8][1]
                    bx, by = li[12][0], li[12][1]
                    # circle shape x and y axis point
                    cv2.circle(img, (rx, ry), 8, (0, 0, 255), cv2.FILLED)
                    cv2.circle(img, (gx, gy), 8, (0, 255, 0), cv2.FILLED)
                    cv2.circle(img, (bx, by), 8, (255, 0, 0), cv2.FILLED)
                    # lines for the eache shape in rgb
                    cv2.line(img, (x0, y0), (rx, ry), (0, 0, 255), 2)
                    cv2.line(img, (x0, y0), (gx, gy), (0, 255, 0), 2)
                    cv2.line(img, (x0, y0), (bx, by), (255, 0, 0), 2)
                    # connect in bellow bottom point of index 0
                    cv2.circle(img, (x0, y0), 8, (255, 255, 255), cv2.FILLED)

                    # canculate the length between the bottom to the each point
                    Rlen = [findPercents(math.hypot(rx - x0, ry - y0), 155, 185,0),findPercents(math.hypot(rx - x0, ry - y0), 155, 185,100)]
                    Glen = [findPercents(math.hypot(gx - x0, gy - y0), 140, 240,0),findPercents(math.hypot(gx - x0, gy - y0), 140, 240,100)]
                    Blen = [findPercents(math.hypot(bx - x0, by - y0), 120, 260,0),findPercents(math.hypot(bx - x0, by - y0), 120, 260,100)]
                    
                    # add the rgb percent values to the list
                    rgb=[Rlen[1],Glen[1],Blen[1]]
                #rgb progress bar
                cv2.rectangle(img,(102,10),(202,20),(0,255,0),2)
                cv2.rectangle(img,(0,10),(100,20),(0,0,255),2)
                cv2.rectangle(img,(204,10),(304,20),(2505,0,0),2)
                cv2.rectangle(img,(0,10),(Rlen[0],20),(0,0,255),cv2.FILLED)
                cv2.rectangle(img,(102,10),(Glen[0]+102,20),(0,255,0),cv2.FILLED)
                cv2.rectangle(img,(204,10),(Blen[0]+204,20),(255,0,0),cv2.FILLED)
                # To calculate the frames per second
                cTime = time.time()
                fps = 1/(cTime-pTime)
                pTime = cTime

                cv2.putText(img,f'FPS:{int(fps)}',(400,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
                cv2.imshow("Images", img)
                cv2.waitKey(1)
                #val = input("RGB:")
                # send the rgb values to the client who connected
                client.send(str(f'{rgb[0]} {rgb[1]} {rgb[2]}').encode('utf-8'))
                # if val == "exit":
                #     break
except KeyboardInterrupt:
    s.close()
    print("\nExit...")
