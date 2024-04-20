import cv2
import os
import pickle
import face_recognition
import numpy as np
import firebase_admin
from firebase_admin import storage
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://biometricsattendance-ac92c-default-rtdb.asia-southeast1.firebasedatabase.app/",
    "storageBucket": "biometricsattendance-ac92c.appspot.com"
})

bucket = storage.bucket()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

imgBackground = cv2.imread("Resources/background.png")

#Importing the mode images into a List
folderModePath = "Resources\Modes"
modePathList = os.listdir(folderModePath)
imgModeList = []
for path in modePathList:
    imgModeList.append(cv2.imread(os.path.join(folderModePath, path)))
    # print(len(imgModeList))

#Load the encoding file
print('Loading Encode File...')
file = open('EncodeFile.p','rb')
encodeListKnownWithIds = pickle.load(file)
file.close()
encodeListKnown, voterIds = encodeListKnownWithIds
#print(voterIds)
print('Encode File Loaded...')

modeType = 0
counter = 0
imgUser = []

while True:
    success, img = cap.read()

    imgS = cv2.resize(img, (0,0), None, 0.25, 0.25)
    imgS = cv2.cvtColor(imgS, cv2.COLOR_BGR2RGB)

    faceCurFrame = face_recognition.face_locations(imgS)
    encodeCurFrame = face_recognition.face_encodings(imgS, faceCurFrame)

    imgBackground[162:162+480,55:55+640] = img
    imgBackground[44:44+633,808:808+414] = imgModeList[modeType]

    for encodeFace, faceLoc in zip(encodeCurFrame, faceCurFrame):
        matches = face_recognition.compare_faces(encodeListKnown, encodeFace)
        faceDis = face_recognition.face_distance(encodeListKnown, encodeFace)
        # print("matches", matches)
        # print("FaceDis", faceDis)

        matchIndex = np.argmin(faceDis)
        # print("Match Index", matchIndex)

        if matches[matchIndex]:
            # print("Known Face Detected")
            # print(voterIds[matchIndex])
            import cv2
            y1, x2, y2, x1 = faceLoc
            y1, x2, y2, x1 = y1*4, x2*4, y2*4, x1*4
            bbox = (55 + x1, 162 + y1, x2 - x1, y2 - y1)
            imgBackground = cv2.rectangle(imgBackground, (bbox[0], bbox[1]), (bbox[0] + bbox[2], bbox[1] + bbox[3]), (0, 255, 0), 2)
            
            id = voterIds[matchIndex]
            if counter == 0:
                counter = 1
                modeType = 1
        
        if counter != 0:
           
           if counter == 1:
                # Get the data
                voterInfo = db.reference(f'Voters/{id}').get()
                print(voterInfo)
                # Get the image from the storage
                blob = bucket.get_blob(f'Images/{id}.jpg')
                array = np.frombuffer(blob.download_as_string(), np.uint8)
                imgUser = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)

        if 10<counter<20:
            modeType = 2
            imgBackground[44:44 + 633, 808:808 + 414] = imgModeList[modeType]

        if counter <=10:
                cv2.putText(imgBackground, str(voterInfo['registration_status']),(1050,623),
                         cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                cv2.putText(imgBackground, str(id),(1030,400),
                         cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                cv2.putText(imgBackground, str(voterInfo['barangay']),(1060,566),
                         cv2.FONT_HERSHEY_COMPLEX,0.5,(0,0,0),1)
                cv2.putText(imgBackground, str(voterInfo['address']),(880,493),
                         cv2.FONT_HERSHEY_COMPLEX,0.40,(0,0,0),1)
                
                
                (w,h), _ = cv2.getTextSize(voterInfo['name'], cv2.FONT_HERSHEY_COMPLEX,1,1)
                offset = (414-w)//2
                cv2.putText(imgBackground, str(voterInfo['name']),(808+offset,340),
                         cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)

                # imgBackground[175:175+216,909:909+216] = imgUser

        counter= counter + 1

        if counter>=20:
            counter = 0
            modeType = 0
            voterInfo = []
            imgUser = []
            imgBackground[44:44+633,808:808+414] = imgModeList[modeType]
            



    # cv2.imshow("Webcam", img)
    cv2.imshow("Biometrics Attendance", imgBackground)
    cv2.waitKey(1)
