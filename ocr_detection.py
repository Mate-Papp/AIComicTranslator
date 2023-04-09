import pytesseract
from PIL import Image, ImageDraw
import matplotlib.pyplot as plt
import os
import math
dir=os.path.dirname(__file__)

def delet_from_arr(element_number: int, arr: list):
    for element in arr:
        del arr[element][element_number]

def get_text_boxes(image_path: Image.Image, mode="manhwa", LANG = "eng") -> Image.Image:
    try: 
        Image.open(image_path)
    except:
        try:
            image_path.convert('1', dither=Image.NONE)
        except:
            raise ValueError('Your image_path is not a PIL.Image.')
        else:   
            image = image_path
    else:
        image = Image.open(image_path)
    
    w, h = image.size
    bw_im = image.convert('1', dither=Image.NONE)
    num=4
    CORDS=[]
    if mode=="manga":
        s=30
        y=120
    elif mode=="manhwa":
        s=60
        y=150
    for ig in range(math.ceil(h/s)):
        im=bw_im.crop((0,ig*s,w,ig*s+y))
        wi,hi=im.size
        im=im.resize((wi*num,hi*num))
        DATAS = pytesseract.image_to_boxes(im, LANG, output_type='dict')
        if DATAS!={}:
            dt = 0
            del DATAS['page']
            for i in range(len(DATAS['left'])):
                DATAS['bottom'][i-dt]=int(hi-(int(DATAS['bottom'][i-dt])/num))+ig*s
                DATAS['right'][i-dt]=int(int(DATAS['right'][i-dt])/num )
                DATAS['top'][i-dt]=int(hi-(int(DATAS['top'][i-dt])/num))+ig*s
                DATAS['left'][i-dt]=int(int(DATAS['left'][i-dt])/num )
                d_width = DATAS['right'][i-dt]-DATAS['left'][i-dt]
                d_height = DATAS['bottom'][i-dt]-DATAS['top'][i-dt]
                if mode=="manhwa":
                    if 10<d_width<w/4 and 10<d_height<w/3:
                        CORDS.append([[int(DATAS['left'][i-dt]),int(DATAS['top'][i-dt])],[int(DATAS['right'][i-dt]),int(DATAS['bottom'][i-dt])]])
                    else:
                        delet_from_arr(i-dt, DATAS)
                        dt+=1
                elif mode=="manga":
                    if 4<d_width<w/6 and 4<d_height<w/5:
                        CORDS.append([[int(DATAS['left'][i-dt]),int(DATAS['top'][i-dt])],[int(DATAS['right'][i-dt]),int(DATAS['bottom'][i-dt])]])
                    else:
                        delet_from_arr(i-dt, DATAS)
                        dt+=1
                
    for t in CORDS:
        img1 = ImageDraw.Draw(image)
        img1.line((t[0][0], t[0][1] , t[0][0], t[1][1]), fill ="blue", width = 2)
        img1.line((t[0][0], t[0][1] , t[1][0], t[0][1]), fill ="blue", width = 2)
        img1.line((t[1][0], t[0][1] , t[1][0], t[1][1]), fill ="blue", width = 2)
        img1.line((t[0][0], t[1][1] , t[1][0], t[1][1]), fill ="blue", width = 2)
        
    return image