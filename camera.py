import tkinter as tk
from tkinter import Message ,Text
import cv2,os
import shutil
import csv
import numpy as np
from PIL import Image, ImageTk
import pandas as pd
import datetime
import time
import tkinter.ttk as ttk
import tkinter.font as font
import add_gui
import attendance_gui as agui
import edit_gui as egui

import sqlite3 as sql


window = tk.Tk()
window.title("PSBB ATTENDANCE MANAGEMENT SYSTEM using FACIAL RECOGNITION")

dialog_title = 'QUIT'
 
window.geometry('1600x900')

window.attributes('-fullscreen', True)


window.grid_rowconfigure(0, weight=1)
window.grid_columnconfigure(0, weight=1)


message = tk.Label(window, text="PSBB ATTENDANCE MANAGEMENT SYSTEM USING FACIAL RECOGNITION" ,font=('Bahnschrift', 34, 'bold underline')) 

message.place(x=35, y=20)

#------------------------------------------------------------------------------------------------------------------------------------------

lbl = tk.Label(window, text="Enter RollNo : ",font=('Bahnschrift SemiBold', 15,"bold")) 
lbl.place(x=10, y=200)
txt= tk.Entry(window,width=20 ,font=('Bahnschrift Light', 15))
txt.place(x=150, y=200)

#------------------------------------------------------------------------------------------------------------------------------------------

lb2 = tk.Label(window, text="Enter Name : ",font=('Bahnschrift SemiBold', 15,"bold")) 
lb2.place(x=10, y=300)
txt2 = tk.Entry(window,width=20,font=('Bahnschrift Light', 15))
txt2.place(x=150, y=300)

#------------------------------------------------------------------------------------------------------------------------------------------

lbl3 = tk.Label(window, text="Status : ",font=('Bahnschrift SemiBold', 15,"bold")) 
lbl3.place(x=10, y=400)
message = tk.Label(window, text="" ,bg="white"  ,fg="black"  ,width=38  ,height=2, activebackground = "white" ,font=('Bahnschrift', 15)) 
message.place(x=150, y=400)

#------------------------------------------------------------------------------------------------------------------------------------------

lbl3= tk.Label(window, text="Attendance : ",font=('Bahnschrift SemiBold', 15,"bold")) 
lbl3.place(x=400, y=650)
message2 = tk.Label(window, text="" ,bg="white"  ,fg="black"  ,width=45  ,height=3, activebackground = "white" ,font=('Bahnschrift', 15)) 
message2.place(x=550, y=650)


#------------------------------------------------------------------------------------------------------------------------------------------
def clear():
    txt.delete(0, 'end')
    txt2.delete(0, 'end')
    res = ""
    add_gui.message.configure(text= res)
  
def is_number(s):
    try:
        float(s)
        return True
    except ValueError:
        pass
 
    try:
        import unicodedata
        unicodedata.numeric(s)
        return True
    except (TypeError, ValueError):
        pass
 
    return False
rns=[]
def TakeImages():
    Id=(agui.txt.get())
    rns.append(Id)
    name=(agui.txt2.get())
    if(is_number(Id) and name.isalpha()):
        cam = cv2.VideoCapture(0)
        harcascadePath = "haarcascade_frontalface_default.xml"
        detector=cv2.CascadeClassifier(harcascadePath)
        sampleNum=0
        while True:
            ret, img = cam.read()
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(gray, 1.3, 5)
            for (x,y,w,h) in faces:
                cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)        
               
                sampleNum=sampleNum+1
                
                cv2.imwrite("TrainingImage\ "+name+"."+Id+'.'+str(sampleNum)+".jpg", gray[y:y+h,x:x+w])
                
                cv2.imshow('frame',img)
           
            if cv2.waitKey(100) & 0xFF == ord('q'):
                break
            
            elif sampleNum>60:
                break
        
        '''
        ("TrainingImage\ "+name+"."+Id+'.'+str(sampleNum)+".jpg", gray[y:y+h,x:x+w])'''
        cam.release()
        cv2.destroyAllWindows() 
        res = "Images Saved for RollNo : " + Id +" Name : "+ name
        row = [Id , name]
        
        if(Id not in 'StudentDetails\StudentDetails.csv'):
            with open('StudentDetails\StudentDetails.csv','a+') as csvFile:
                writer = csv.writer(csvFile)

                writer.writerow(row)
            csvFile.close()
            message.configure(text= res)
        elif(Id in 'StudentDetails\StudentDetails.csv',"r"):
            res = "RollNo Already Exists"
            message.configure(text= res)
                        
    else:
        if(name.isalpha()):
            res = "Enter Numeric Id"
            message.configure(text= res)
    
def TrainImages():
    recognizer = cv2.face_LBPHFaceRecognizer.create()
    harcascadePath = "haarcascade_frontalface_default.xml"
    detector =cv2.CascadeClassifier(harcascadePath)
    faces,Id = getImagesAndLabels("TrainingImage")
    recognizer.train(faces, np.array(Id))
    recognizer.save("train.yml")
    res = "Image Trained"
    message.configure(text= res)
import PIL.Image
def getImagesAndLabels(path):
    
    imagePaths=[os.path.join(path,f) for f in os.listdir(path)] 

    faces=[]
    
    Ids=[]
    
    for imagePath in imagePaths:
     
        pilImage=PIL.Image.open(imagePath).convert('L')
        
        imageNp=np.array(pilImage,'uint8')
        
        Id=int(os.path.split(imagePath)[-1].split(".")[1])
        
        faces.append(imageNp)
        Ids.append(Id)        
    return faces,Ids

def TrackImages():
    recognizer = cv2.face.LBPHFaceRecognizer_create()
    recognizer.read("train.yml")
    harcascadePath = "haarcascade_frontalface_default.xml"
    faceCascade = cv2.CascadeClassifier(harcascadePath);    
    df=pd.read_csv("StudentDetails\StudentDetails.csv")
    cam = cv2.VideoCapture(0)
    font = cv2.FONT_HERSHEY_SIMPLEX        
    col_names =  ['Id','Name','Date','Time']
    attendance = pd.DataFrame(columns = col_names)    
    while True:
        ret, im =cam.read()
        gray=cv2.cvtColor(im,cv2.COLOR_BGR2GRAY)
        faces=faceCascade.detectMultiScale(gray, 1.2,5)    
        for(x,y,w,h) in faces:
            cv2.rectangle(im,(x,y),(x+w,y+h),(225,0,0),2)
            Id, conf = recognizer.predict(gray[y:y+h,x:x+w])                                   
            if(conf < 50):
                ts = time.time()      
                date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                aa=df.loc[df['RollNo'] == Id]['Name'].values
                tt=str(Id)+"-"+aa
                attendance.loc[len(attendance)] = [Id,aa,date,timeStamp]
                
            else:
                Id='Unknown'                
                tt=str(Id)  
            if(conf > 75):
                noOfFile=len(os.listdir("UnidentifiedImages"))+1
                cv2.imwrite("UnidentifiedImages\Image"+str(noOfFile) + ".jpg", im[y:y+h,x:x+w])            
            cv2.putText(im,str(tt),(x,y+h), font, 1,(255,255,255),2)        
        attendance=attendance.drop_duplicates(subset=['Id'],keep='first')    
        cv2.imshow('im',im)
        if (cv2.waitKey(1)==ord('q')):
            break
    ts = time.time()      
    date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
    timeStamp = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
    Hour,Minute,Second=timeStamp.split(":")
    fileName="AttendanceRegister\Attendance_"+date+"_"+Hour+"-"+Minute+"-"+Second+".csv"
    attendance.to_csv(fileName,index=False)
    cam.release()
    cv2.destroyAllWindows()
    print(attendance)
    res=attendance
    message2.configure(text= res)
    for i in rns:
        if i not in attendance:
            print(i,"absent")
    




  
clear = tk.Button(window, text="CLEAR INPUT", command=clear,bg="cyan",fg="black",font=('Bahnschrift SemiBold', 13,"bold"))
clear.place(x=150, y=500)
cap = tk.Button(window, text="CAPTURE IMAGE", command=TakeImages  ,bg="cyan"  ,fg="black"  ,width=30  ,height=2, activebackground = "Red" ,font=('Bahnschrift SemiBold', 13,"bold"))
cap.place(x=1200, y=200)
train = tk.Button(window, text="TRAIN IMAGES", command=TrainImages  ,bg="cyan"  ,fg="black"  ,width=30  ,height=2, activebackground = "Red" ,font=('Bahnschrift SemiBold', 13,"bold"))
train.place(x=1200, y=300)
track = tk.Button(window, text="RECOGNISE FOR ATTENDANCE", command=TrackImages  ,bg="cyan"  ,fg="black"  ,width=30  ,height=2, activebackground = "Red" ,font=('Bahnschrift SemiBold', 13,"bold"))
track.place(x=1200, y=400)
quit1 = tk.Button(window, text="QUIT", command=window.destroy  ,bg="cyan"  ,fg="black"  ,width=30  ,height=2, activebackground = "Red" ,font=('Bahnschrift SemiBold', 13,"bold"))
quit1.place(x=1200, y=500)
devBy = tk.Text(window, background=window.cget("background"), borderwidth=0,font=('Bahnschrift Light', 25, 'italic'))
devBy.insert("insert", "Developed by Harikrishnan and Anirudh - XI-B")
devBy.configure()
devBy.place(x=800, y=750)

#----------------------------------------------------------------------------------------------------------------------------------------------

from tkinter import * 
from tkinter.ttk import *
from time import strftime
def time(): 
    string = strftime('%H:%M:%S %p') 
    lbl.config(text=string) 
    lbl.after(1000,time) 

lbl = Label(window, font = ('Bahnschrift Light', 40, 'bold'))
lbl.place(x=670,y=180)
time() 


