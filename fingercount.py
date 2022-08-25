import cv2
import mediapipe as mp
import time
import os

Wcam,Hcam = 640,480
pTime = 0
cap = cv2.VideoCapture(0)
mpHande = mp.solutions.hands
hands = mpHande.Hands(max_num_hands=1)
mpDraw = mp.solutions.drawing_utils

cap.set(3,Wcam)
cap.set(4,Hcam)

while True:
    success,img = cap.read()
    imgRGB = cv2.cvtColor(img,cv2.COLOR_BGR2RGB)
    result = hands.process(imgRGB)
    li = []

    if result.multi_hand_landmarks:
        for handLms in result.multi_hand_landmarks:
            for id,lm in enumerate(handLms.landmark):
                h,w,c = img.shape
                cx,cy = int(lm.x*w),int(lm.y*h)
                li.append({"id": id,"x":cx,"y":cy})

            mpDraw.draw_landmarks(img,handLms,mpHande.HAND_CONNECTIONS)

    if len(li):
        count = 0
        for i in range(len(li)):
            if i == 4:
                if li[i]['x'] > li[i-1]['x']:
                    count += 1
            elif i%4==0 and i != 0:
                if li[i]['y'] < li[i-1]['y']:
                   count += 1
        print(f'count:{count}')
        cv2.putText(img,f'count:{count}',(0,50),cv2.FONT_HERSHEY_PLAIN,4,(255,0,255),3)
        
    cTime = time.time()
    fps = 1/(cTime-pTime)
    pTime = cTime

    #cv2.putText(img,f'FPS:{int(fps)}',(400,70),cv2.FONT_HERSHEY_PLAIN,3,(255,0,0),3)
    cv2.imshow("Images",img)
    cv2.waitKey(1)