import cv2
import mediapipe as mp
import time
import math


def findPercents(inp, mi, ma,v):
    va = ((inp - mi) * 100 / (ma - mi))
    if v == 100:
        va = v - va
    if va > 100:
        return 100
    elif va < 0:
        return 0
    else:
        return int(va)


cap = cv2.VideoCapture(0)
mpHande = mp.solutions.hands
hands = mpHande.Hands()
mpDraw = mp.solutions.drawing_utils

pTime = 0
cTime = 0

while True:
    success, img = cap.read()

    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)
    li = []
    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for id, lm in enumerate(handLms.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x*w), int(lm.y*h)
                li.append([cx, cy])
            # this below line for the 21 dots and connection between them
            # mpDraw.draw_landmarks(img,handLms,mpHande.HAND_CONNECTIONS)
    Rlen = [0,0]
    Glen = [0,0]
    Blen = [0,0]
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
        print(f'{Rlen}::{Glen}::{Blen}')

    #rgb progress bar
    cv2.rectangle(img,(0,10),(100,20),(0,0,255),2)
    cv2.rectangle(img,(102,10),(202,20),(0,255,0),2)
    cv2.rectangle(img,(204,10),(304,20),(2505,0,0),2)
    cv2.rectangle(img,(0,10),(Rlen[0],20),(0,0,255),cv2.FILLED)
    cv2.rectangle(img,(102,10),(Glen[0]+102,20),(0,255,0),cv2.FILLED)
    cv2.rectangle(img,(204,10),(Blen[0]+204,20),(255,0,0),cv2.FILLED)

    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    cv2.putText(img, str(int(fps)), (10, 70),
                cv2.FONT_HERSHEY_PLAIN, 3, (255, 0, 255), 3)

    cv2.imshow("Image", img)
    cv2.waitKey(1)
