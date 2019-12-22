# -*- coding: utf-8 -*-
"""
Created on Fri Nov 15 10:11:22 2019

@author: micha
"""
#Functions for compression, encoding, decoding and evaluation
#import packages required
import collections
import cv2
import matplotlib.pyplot as plt
import numpy as np
import scipy.fftpack as fp
import skimage
import svm
import brisque as br
import os
import sys

#Import metrics to measure effect of compression
def compressratio(file1,file2):

    file1Size = float(os.stat(file1).st_size)
    file2Size = float(os.stat(file2).st_size)

    difference = file1Size - file2Size

    ratio = (((file1Size - file2Size) / file1Size) * 100) # Math to find ratio. Somehow broken (?!).

    print("Original size: " + str(file1Size))
    print("New size: " + str(file2Size))
    print("Change in size: " + str(difference))
    print("Size change ratio: " + str(ratio) + "%")
    return ratio

def mse(imageA, imageB):
	# the 'Mean Squared Error' between the two images is the
	# sum of the squared difference between the two images;
	# NOTE: the two images must have the same dimension
    err=np.sum((imageA.astype("float") - imageB.astype("float")) ** 2)
    err/=float(imageA.shape[0] * imageA.shape[1])
    print(err)
    return err
    

def score(img):
    brisq=br.BRISQUE()
    feats=brisq.get_feature(img)
    err=brisq.get_score(img)
    print("Brisque Score: "+str(err))
    return err
#Build display image function 
def showImage(img):
    plt.figure(figsize=(15,15))
    plt.imshow(img,cmap='gray')
    plt.xticks([]),plt.yticks([])
    plt.show()


#1.For the color image need to re encode RGB colorspace into YCbCr color space

R, G, B = 'r', 'g', 'b'
Y, CB, CR = 'y', 'cb', 'cr'

def rgbTOycbcr(r, g, b):
   #For encoding input of RGB layers to convert from the range of R, G, B is [0, 255] to Y, Cb, Cr should be [0, 255], [-128, 127], [-128, 127] 
    return collections.OrderedDict((
        (Y, + 0.299 * r + 0.587 * g + 0.114 * b),
        (CB, - 0.168736 * r - 0.331264 * g + 0.5 * b),
        (CR, + 0.5 * r - 0.418688 * g - 0.081312 * b)
    ))
  
        
def ycbcrTOrgb(y, cb, cr):
    #For decoding input of RGB layers to convert from Y, Cb, Cr should be [0, 255], [-128, 127], [-128, 127] to the range of R, G, B is [0, 255] 
    return collections.OrderedDict((
        (R, y + 1.402 * cr),
        (G, y - 0.714 * cr - 0.344 * cb ),
        (B, y + 1.773 * cb)
    ))
    
def downSample(array, mode):
    if mode not in {1, 2, 4}:
        raise ValueError(f'Mode ({mode}) must be 1, 2 or 4.')
    if mode == 4:
        return array
    return array[::3 - mode, ::2]

def upSample(array, mode):
    if mode not in {1, 2, 4}:
        raise ValueError(f'Mode ({mode}) must be 1, 2 or 4.')
    if mode == 4:
        return array
    return array.repeat(3 - mode, axis=0).repeat(2, axis=1)

#3.Discrete cosine transformation
def dct2D(array):
    return fp.dct(fp.dct(array,norm='ortho', axis=0), norm='ortho', axis=1) 

def idct2D(array):
    return fp.idct(fp.idct(array,norm='ortho', axis=0), norm='ortho', axis=1)

#4.Quantization of elements in the matrix
def quantize(block,component,quality,inverse=False):
    factor=5000/np.int32(quality)
    if component == Y:
       q= load_quantization_table(component)
       if inverse:
        return (block * (q*factor/100)).round().astype(np.int32)
       else:
           return (block / q).round().astype(np.int32)
    else:  
        q=load_quantization_table(component)
        if inverse:
            return (block * (q*factor/100)).round().astype(np.int32)
        else:
            return (block / (q*factor/100)).round().astype(np.int32)
    
    
def load_quantization_table(component):
    # Quantization Table for: Photoshop - (Save For Web 080)
    # (http://www.impulseadventure.com/photo/jpeg-quantization.html)
    if component == 'Y':
        q = np.array([[16, 11, 10, 16, 24, 40, 51, 61],
                      [12, 12, 14, 19, 26, 58, 60, 55],
                      [14, 13, 16, 24, 40, 57, 69, 56],
                      [14, 17, 22, 29, 51, 87, 80, 62],
                      [18, 22, 37, 56, 68, 109, 103, 77],
                      [24, 36, 55, 64, 81, 104, 113, 92],
                      [49, 64, 78, 87, 103, 121, 120, 101],
                      [72, 92, 95, 98, 112, 100, 103, 99]])
    elif component == 'Cr':
        q = np.array([[3, 3, 5, 9, 13, 15, 15, 15],
                      [3, 4, 6, 11, 14, 12, 12, 12],
                      [5, 6, 9, 14, 12, 12, 12, 12],
                      [9, 11, 14, 12, 12, 12, 12, 12],
                      [13, 14, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12],
                      [15, 12, 12, 12, 12, 12, 12, 12]])
    else:
        raise ValueError((
            "component should be either 'Y' or 'Cr' or 'Cb' "
            "but '{comp}' was found").format(comp=component))

    return q

def run_length_encoding(array):
    i = 0
    skip = 0
    stream = []    
    bitstream = ""
    image = array.astype(int)
    while i < image.shape[0]:
        if image[i] != 0:            
            stream.append((image[i],skip))
            bitstream = bitstream + str(image[i])+ " " +str(skip)+ " "
            skip = 0
        else:
            skip = skip + 1
        i = i + 1

    return bitstream


   