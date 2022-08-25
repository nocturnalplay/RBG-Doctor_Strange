import socket
import sys
import cv2
import mediapipe as mp
import time
import json

# get host and port for the server as argument if not throught error
if len(sys.argv) < 3:
    print("add input argumaens [host] [port]")
    sys.exit()

host = sys.argv[1]
port = int(sys.argv[2])

# videocapture initialization
Wcam, Hcam = 640, 480
pTime = 0
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
                            li.append({"id": id, "x": cx, "y": cy})
                            if id == 4:
                                cv2.circle(img,(cx,cy),8,(0,0,255),cv2.FILLED)
                            elif id == 8:
                                cv2.circle(img,(cx,cy),8,(0,255,0),cv2.FILLED)
                            elif id == 12:
                                cv2.circle(img,(cx,cy),8,(255,0,0),cv2.FILLED)
                        mpDraw.draw_landmarks(
                            img, handLms, mpHande.HAND_CONNECTIONS)

                rgb = [100,100,100]
                if len(li):
                    count = 0
                    for i in range(len(li)):
                        if i == 4:
                            if li[i]['x'] > li[i-1]['x']:
                                count += 1
                                rgb[0] = 50
                        elif i == 8:
                             if li[i]['y'] < li[i-1]['y']:
                                count += 1
                                rgb[1] = 50
                        elif i == 12:
                            if li[i]['y'] < li[i-1]['y']:
                                count += 1
                                rgb[2] = 50

                    print(f'count:{count}')
                    cv2.putText(
                        img, f'count:{count}', (0, 50), cv2.FONT_HERSHEY_PLAIN, 4, (255, 0, 255), 3)

                # To calculate the frames per second
                cTime = time.time()
                fps = 1/(cTime-pTime)
                pTime = cTime

                # cv2.putText(img,f'FPS:{int(fps)}',(400,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
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
