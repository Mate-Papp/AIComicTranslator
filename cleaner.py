from PIL import Image, ImageFilter, ImageDraw
import pytesseract
import matplotlib.pyplot as plt

#run time : --- 0.3 seconds ---


def not_negative(num: int, sec=-1) -> int:
    if num <0:
        return 0
    elif sec!=-1 and num>sec:
        return sec
    return num
def transformattion(array,im_width):
    import math
    pt=[]
    for i in range(len(array)):
        if i%im_width==0:
            pt.append(list())
            pt[math.floor(i/im_width)].append(array[i])
        else:
            pt[math.floor(i/im_width)].append(array[i])
    return list(pt)
def most_common(lst):
    return max(set(lst), key=lst.count)
def re_transformattion(arr: list):
    import numpy
    randim_image = numpy.array(arr, dtype=numpy.uint8)
    im = Image.fromarray(randim_image)
    return im
def delet_from_arr(element_number: int, arr: list):
    for element in arr:
        del arr[element][element_number]

class ImageCleaner:
    def __init__(self, image_path: Image.Image, tesseract_cmd = 'tesseract', size_num = 1) -> None:
        try: 
            Image.open(image_path)
        except:
            try:
                image_path.convert('1', dither=Image.NONE)
            except:
                raise ValueError('Your image_path is not a PIL.Image.')
            else:   
                self.image = image_path
        else:
            self.image = Image.open(image_path)
        self.size_num = size_num  
        pytesseract.pytesseract.tesseract_cmd = tesseract_cmd 
           
    def detect_caracters(self,lang="eng") -> dict:
        c_im=self.image.convert('1', dither=Image.NONE)
        w, h = c_im.size
        id=c_im.resize((w*self.size_num , h*self.size_num ))
        data = pytesseract.image_to_boxes(id, lang=lang,output_type='dict')
        if data!={}:
            dt = 0
            del data['page']
            for i in range(len(data['left'])):
                data['bottom'][i-dt]=int(h-(int(data['bottom'][i-dt])/self.size_num))
                data['right'][i-dt]=int(int(data['right'][i-dt])/self.size_num )
                data['top'][i-dt]=int(h-(int(data['top'][i-dt])/self.size_num))
                data['left'][i-dt]=int(int(data['left'][i-dt])/self.size_num )
                if int(w*h/2)<=(data['bottom'][i-dt]-data['top'][i-dt])*(data['right'][i-dt]-data['left'][i-dt]):
                    delet_from_arr(i-dt, data)
                    dt+=1
        return data

    def cleaning(self, source_lang="eng",):
        cordinates = self.detect_caracters(source_lang)
        w, h = self.image.size
        if cordinates!={}:
            for i in range(len(cordinates['left'])):
                cleanable_img=self.image.crop((not_negative(cordinates['left'][i]-8),not_negative(cordinates['top'][i]-5),not_negative(cordinates['right'][i]+4,w-1),not_negative(cordinates['bottom'][i]+4,h-1)))
                wh, hh = cleanable_img.size
                datas=transformattion(list(cleanable_img.getdata()),wh)
                for z in range(len(datas)):
                    for q in range(len(datas[0])):
                        if q>4 and z!=0:
                            datas[z][q]=datas[z][q-5]
                self.image.paste(re_transformattion(datas).filter(ImageFilter.BoxBlur(4)),(not_negative(cordinates['left'][i]-8),not_negative(cordinates['top'][i]-5)))
            blurt = self.image.crop((not_negative(min(cordinates['left'])-8),not_negative(min(cordinates['top'])-5),not_negative(max(cordinates['right'])+4,w-1),not_negative(max(cordinates['bottom'])+4,h-1))).filter(ImageFilter.BoxBlur(2)) 
            self.image.paste(blurt, (not_negative(min(cordinates['left'])-8),not_negative(min(cordinates['top'])-5)))   
        return self.image