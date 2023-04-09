import clean_page
import cv2
import pytesseract
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import time

start_time = time.time()

def not_negative(num: int, sec=-1) -> int:
    if num <0:
        return 0
    elif sec!=-1 and num>sec:
        return sec
    return num
def pruning_count(left_cords_lst:list, top_cords_lst:list, right_cords_lst:list, bottom_cords_lst:list, element_number:list, all_elms:list, kb=0):
    elms = []
    dt= []
    ct = 0
    for y in element_number:
        e_num = y
        for i in range(len(left_cords_lst)):
            if i != e_num and (top_cords_lst[e_num]-kb<=top_cords_lst[i]<=bottom_cords_lst[e_num]+kb or top_cords_lst[e_num]-kb<=bottom_cords_lst[i]<=bottom_cords_lst[e_num]+kb) and (left_cords_lst[e_num]-kb<=right_cords_lst[i]<=right_cords_lst[e_num]+kb or left_cords_lst[e_num]-kb<=left_cords_lst[i]<=right_cords_lst[e_num]+kb) and e_num not in all_elms and i not in all_elms and e_num not in elms and i not in elms:
                ct+=1
                dt.append([[left_cords_lst[e_num],top_cords_lst[e_num]],[right_cords_lst[e_num],bottom_cords_lst[e_num]]])
                dt.append([[left_cords_lst[i],top_cords_lst[i]],[right_cords_lst[i],bottom_cords_lst[i]]])
                elms.append(i)
    return ct, elms, dt

def recursive__pruning_count(left_cords_lst:list, top_cords_lst:list, right_cords_lst:list, bottom_cords_lst:list, element_number:list, ct, dt, all_elms, kb=0):
    fg = pruning_count(left_cords_lst, top_cords_lst, right_cords_lst, bottom_cords_lst, element_number, all_elms, kb)
    dt+=fg[2]
    all_elms+=fg[1]
    if fg[2]!=[]:
        recursive__pruning_count(left_cords_lst, top_cords_lst, right_cords_lst, bottom_cords_lst, fg[1], ct, dt, all_elms)
        
def del_from_img(img:Image.Image, cords:list):
    for f in cords:
       img1 = ImageDraw.Draw(img) 
       img1.rectangle(((f[0][0], f[0][1]), (f[1][0], f[1][1])),fill=(255, 255, 255))

def combiner_algorithm(left_cords_lst:list, top_cords_lst:list, right_cords_lst:list, bottom_cords_lst:list, w:int, h:int, kb=0, outline = 0) -> None:
    """
        :returns: this is a method so thers no need return data.
    """
    all_cords = []
    delt=[]
    for c in range(len(top_cords_lst)):
        for a in range(len(top_cords_lst)):
            if c != a and (top_cords_lst[c]-kb<=top_cords_lst[a]<=bottom_cords_lst[c]+kb or top_cords_lst[c]-kb<=bottom_cords_lst[a]<=bottom_cords_lst[c]+kb) and (left_cords_lst[c]-kb<=right_cords_lst[a]<=right_cords_lst[c]+kb or left_cords_lst[c]-kb<=left_cords_lst[a]<=right_cords_lst[c]+kb) and c not in delt and a not in delt:
                right_cords_lst[c]=int(max([right_cords_lst[c],right_cords_lst[a]]))
                left_cords_lst[c]=int(min([left_cords_lst[c],left_cords_lst[a]]))
                top_cords_lst[c]=int(min([top_cords_lst[c],top_cords_lst[a]]))
                bottom_cords_lst[c]=int(max([bottom_cords_lst[c],bottom_cords_lst[a]]))
                delt.append(a)
    d=0
    for i in range(len(top_cords_lst)):
        if i in delt:
            del left_cords_lst[i-d]
            del top_cords_lst[i-d]
            del right_cords_lst[i-d]
            del bottom_cords_lst[i-d]
            d+=1
        else:
            left_cords_lst[i-d]=not_negative(left_cords_lst[i-d]-outline)
            top_cords_lst[i-d]=not_negative(top_cords_lst[i-d]-outline)
            right_cords_lst[i-d]=not_negative(right_cords_lst[i-d]+outline, w-1)
            bottom_cords_lst[i-d]=not_negative(bottom_cords_lst[i-d]+outline, h-1)
            
    
    for g in range(len(top_cords_lst)):
        all_cords.append([[left_cords_lst[g],top_cords_lst[g]],[right_cords_lst[g],bottom_cords_lst[g]]])
    
    return all_cords

def text_boxes(img_path, rectangle=False):
    orign_im = Image.open(img_path)
    wfd, hfd = orign_im.size
    image= clean_page.pil_to_cv2(clean_page.clean_image_file(img_path))
    edged = cv2.Canny(image, 30, 200)
    cnts, _ = cv2.findContours(edged, cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    print("Number of Contours found = " + str(len(cnts)))
    extLeft, extRight, extTop, extBot = [], [], [], []
    cords=[]
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
    #conver img
    ret_im = clean_page.cv2_to_pil(image)
    all_del = []
    #first filtering (10 combination)
    for i in range(len(extLeft)):
        ct=0
        dt=[]
        all_elms = []
        recursive__pruning_count(extLeft, extTop, extRight, extBot,[i], ct, dt, all_elms, 3)
        all_elms.append(i)
        dt.append([[extLeft[i],extTop[i]],[extRight[i],extBot[i]]])
        ct=len(all_elms)
        if ct>10:
            del_from_img(ret_im, dt)
            all_del+=all_elms
    d=0
    for u in range(len(extLeft)):
        if u in all_del:
            del extLeft[u-d]
            del extRight[u-d]
            del extTop[u-d]
            del extBot[u-d]
            d+=1
    #create groups 
    combiner_algorithm(extLeft, extTop, extRight, extBot, wfd, hfd, 15)
    combiner_algorithm(extLeft, extTop, extRight, extBot, wfd, hfd, outline=12)
    cords = combiner_algorithm(extLeft, extTop, extRight, extBot, wfd, hfd, 1)
    d=0
    for u in range(len(extLeft)):
        if extRight[u-d]-extLeft[u-d]<80 and extBot[u-d]-extTop[u-d]<wfd/2:
            del_from_img(ret_im, [cords[u-d]])
            del cords[u-d]
            del extLeft[u-d]
            del extRight[u-d]
            del extTop[u-d]
            del extBot[u-d]
            d+=1
    if rectangle == False:
        cords = combiner_algorithm(extLeft, extTop, extRight, extBot, wfd, hfd, 10)
    for t in range(len(cords)):
        img1 = ImageDraw.Draw(orign_im)
        img1.line((cords[t][0][0], cords[t][0][1] , cords[t][0][0], cords[t][1][1]), fill ="blue", width = 2)
        img1.line((cords[t][0][0], cords[t][0][1] , cords[t][1][0], cords[t][0][1]), fill ="blue", width = 2)
        img1.line((cords[t][1][0], cords[t][0][1] , cords[t][1][0], cords[t][1][1]), fill ="blue", width = 2)
        img1.line((cords[t][0][0], cords[t][1][1] , cords[t][1][0], cords[t][1][1]), fill ="blue", width = 2)
    
    return orign_im

text_boxes(r"C:\Users\Mate\Desktop\AI comic translator --full recognition\07.jpg").show() 
    




print("--- %s seconds ---" % (time.time() - start_time))
