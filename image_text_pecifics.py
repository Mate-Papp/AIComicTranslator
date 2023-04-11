import clean_page
import cv2
import pytesseract
import numpy as np
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import time

def contours__lines_ct(img):
    (hi,wi,di)=img.shape
    blank_image = clean_page.inverte(np.zeros((hi,wi,3), np.uint8))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edged = cv2.Canny(gray, 30, 200)
    cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    #print("Number of Contours found = " + str(len(cnts)))
    extLeft, extRight, extTop, extBot = [], [], [], []
    x=[]
    y=[]
    #get contours boxes
    for h in range(len(cnts)):
        x.append([])
        y.append([])
        for t in range(len(cnts[h])):
            x[len(x)-1].append(cnts[h][t][0][0])
            y[len(y)-1].append(cnts[h][t][0][1])
    for i in range(len(x)):
        extLeft.append(min(x[i]))
        extRight.append(max(x[i]))
        extTop.append(min(y[i]))
        extBot.append(max(y[i]))
    count=0
    for i in range(len(extBot)):
        for g in range(len(extBot)):
            if i != g and abs(extBot[i]-extBot[g])==0:
                count+=1  
    return count
        
        

def image_text_rotetion(img:Image.Image):
    counts = []
    counts.append(contours__lines_ct(clean_page.pil_to_cv2(img)))
    for i in range(359):
        degree = i+1
        image = clean_page.pil_to_cv2(img.rotate(-degree, expand=True))
        f = contours__lines_ct(image)
        counts.append(f)
    ret_deg = counts.index(max(counts))
    if ret_deg==180:
        ret_deg=0
    elif ret_deg !=0:
        ret_deg = -ret_deg+360
    return ret_deg 
        
    
print(image_text_rotetion(Image.open(r"C:\Users\Mate\Desktop\AI comic translator --full recognition\01-crop#4.jpg")))