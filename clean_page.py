import numpy as np
import cv2
import sys
import scipy.ndimage
import argparse
import os
import math
import matplotlib.pyplot as plt
from PIL import Image

import connected_components as cc
import arg
import defaults


def clean_page(img, max_scale=defaults.CC_SCALE_MAX, min_scale=defaults.CC_SCALE_MIN):
  #img = cv2.imread(sys.argv[1])
  (hi,wi,di)=img.shape
  

  gray = grayscale(img)

  #create gaussian filtered and unfiltered binary images
  sigma = arg.float_value('sigma',default_value=defaults.GAUSSIAN_FILTER_SIGMA)
  if arg.boolean_value('verbose'):
    print('Binarizing image with sigma value of ' + str(sigma))
  gaussian_filtered = scipy.ndimage.gaussian_filter(gray, sigma=sigma)
  binary_threshold = arg.integer_value('binary_threshold',default_value=defaults.BINARY_THRESHOLD)
  if arg.boolean_value('verbose'):
    print('Binarizing image with sigma value of ' + str(sigma))
  gaussian_binary = binarize(gaussian_filtered, threshold=binary_threshold)
  binary = binarize(gray, threshold=binary_threshold)

  #Draw out statistics on average connected component size in the rescaled, binary image
  average_size = cc.average_size(gaussian_binary)
  #print('Initial mask average size is ' + str(average_size))
  max_size = average_size*max_scale
  min_size = average_size*min_scale

  #primary mask is connected components filtered by size
  mask = cc.form_mask(gaussian_binary, max_size, min_size)

  #secondary mask is formed from canny edges
  canny_mask = form_canny_mask(gaussian_filtered, mask=mask)

  #final mask is size filtered connected components on canny mask
  final_mask = cc.form_mask(canny_mask, max_size, min_size)

  #apply mask and return images
  cleaned = cv2.bitwise_not(binary * final_mask)
  return (cleaned)

def clean_image_file(filename, h:int="full"):
  try:
    cv2.imread(filename)
  except:
    imgs = pil_to_cv2(filename)
    imgm = inverte(pil_to_cv2(filename))
    final_cleaned = filename
    final_cleaned2 = filename
  else:
    imgs = cv2.imread(filename)
    imgm = inverte(cv2.imread(filename))
    final_cleaned = Image.open(filename)
    final_cleaned2 = Image.open(filename)
  wi, hi = final_cleaned.size
  if h== "full":
    h= hi
  for r in range(math.ceil(hi/h)):
    img=imgs[r*h:r*h+h, 0:wi]
    opencv_image = clean_page(img)
    
    color_coverted = cv2.cvtColor(opencv_image, cv2.COLOR_BGR2RGB)
  
    pil_image = Image.fromarray(color_coverted)
    final_cleaned.paste(pil_image, (0, r*h))
  for r in range(math.ceil(hi/h)):
    img=imgm[r*h:r*h+h, 0:wi]
    opencv_image2 = clean_page(img)
    
    color_coverted2 = cv2.cvtColor(opencv_image2, cv2.COLOR_BGR2RGB)
  
    pil_image2 = Image.fromarray(color_coverted2)
    final_cleaned2.paste(pil_image2, (0, r*h))
  finally_c = cv2.bitwise_and(pil_to_cv2(final_cleaned), pil_to_cv2(final_cleaned2))
  finally_c = cv2_to_pil(finally_c)
  return finally_c

def inverte(imagem):
    imagem = cv2.bitwise_not(imagem)
    return imagem
def cv2_to_pil(cv2_img):
    color_coverted = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(color_coverted)
    return pil_image
def pil_to_cv2(pil_img):
    return cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
def grayscale(img):
  gray = cv2.cvtColor(img,cv2.COLOR_BGR2GRAY)
  #adjust histogram to maximize black/white range (increase contrast, decrease brightness)??
  #gray = cv2.equalizeHist(gray)
  return gray

def binarize(img, threshold=190, white=255):
  (t,binary) = cv2.threshold(img, threshold, white, cv2.THRESH_BINARY_INV )
  return binary

def form_canny_mask(img, mask=None):
  edges = cv2.Canny(img, 128, 255, apertureSize=3)
  if mask is not None:
    mask = mask*edges
  else:
    mask = edges
  contours,hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

  temp_mask = np.zeros(img.shape,np.uint8)
  for c in contours:
    #also draw detected contours into the original image in green
    #cv2.drawContours(img,[c],0,(0,255,0),1)
    hull = cv2.convexHull(c)
    cv2.drawContours(temp_mask,[hull],0,255,-1)
    #cv2.drawContours(temp_mask,[c],0,255,-1)
    #polygon = cv2.approxPolyDP(c,0.1*cv2.arcLength(c,True),True)
    #cv2.drawContours(temp_mask,[polygon],0,255,-1)
  return temp_mask

