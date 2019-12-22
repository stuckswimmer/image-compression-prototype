# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 10:48:36 2019

@author: micha
"""
import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, Button, Style
import cv2
import tkinter.messagebox

import numpy as np
import math
import os
import logging
import time

from zigzag import izigzag
from compressmeths import (ycbcrTOrgb, upSample, 
                     idct2D, quantize, load_quantization_table, R, G, B,
                     compressratio, mse, score)

global array, bitstream, path, contents,img,decoded_img

def applyc(entry_widget):  # ADDED WIDGET ARGUMENT
    global component
    """ Some function outside class. """
    print("clicked")
    component = entry_widget.get()  # REFERENCE ENTRY WIDGET PASSED AS ARGUMENT
    print(component)

def applyb(entry_widget):  # ADDED WIDGET ARGUMENT
    global blocksize
    """ Some function outside class. """
    print("clicked")
    blocksize = entry_widget.get()  # REFERENCE ENTRY WIDGET PASSED AS ARGUMENT
    print(blocksize)

def applyq(entry_widget):  # ADDED WIDGET ARGUMENT
    global quality
    """ Some function outside class. """
    print("clicked")
    quality = entry_widget.get()  # REFERENCE ENTRY WIDGET PASSED AS ARGUMENT
    print(quality)

    
def applydecom():
    global decoded_img
    print("clicked")
    decoded_img=decompress(contents,component,quality,blocksize)
    print(decoded_img)

def metrics():
    print("clicked")
    mean=mse(img,decoded_img)
    original=score(img)
    decom=score(decoded_img)
    #messagebox.showinfo('mean square error is'+ mean)
    messagebox.showinfo('Metrics','The Mean Squared Error is: '+ str(mean)+'\nThe original has a BRISQUE score: '+ str(original)+'\nThe decompressed has a BRISQUE score: '+ str(decom))
    
    
    
def select_image():
	# grab a reference to the image panels
    global contents, path
	# open a file chooser dialog and allow the user to select an input
	# image
    path = tkinter.filedialog.askopenfilename()
    	# ensure a file path was selected
    if len(path) > 0:
        file1 = open("image.txt","r")
        if file1.mode=='r':
            contents=file1.read()
            print(contents)
def select_original():
	# grab a reference to the image panels
    global img
	# open a file chooser dialog and allow the user to select an input
	# image
    original = tkinter.filedialog.askopenfilename()
    	# ensure a file path was selected
    if len(path) > 0:
        img=cv2.imread(original,0)
        cv2.imshow('input image', img)
        cv2.waitKey(0)

def decompress(contents,component,quality,blocksize):
    encoded = contents.split()
    nrows = int(''.join(filter(str.isdigit, encoded[0])))
    ncols = int(''.join(filter(str.isdigit, encoded[1])))

    array = np.zeros(nrows*ncols).astype(int)
    
    #Run length decoding
    #Set variables for loops, height, element and width. 
    h = 0
    e = 2
    w = 0
    
    while h < array.shape[0]:
        #Reached the end of the bitstream
        if(encoded[e] == ';'):
            break
        # Check for a - sign in string to remove intensity normalisation
        if "-" not in encoded[e]:
            array[h] = int(''.join(filter(str.isdigit, encoded[e])))        
        else:
            array[h] = -1*int(''.join(filter(str.isdigit, encoded[e])))        
    
        if(e+3 < len(encoded)):
            w = int(''.join(filter(str.isdigit, encoded[e+3])))
    
        if w == 0:
            h = h + 1
        else:                
            h = h + w + 1        
    
        e = e + 2
    
    #Reshape the decoded bitstream into the dimensions of the original image
    array = np.reshape(array,(nrows,ncols))
    cv2.imshow('', np.uint8(array))
    cv2.waitKey(0)
    #Reset loop variables readay for iteration over the different zigzagged arrays 
    i = 0
    j = 0
    # initialisation of decompressed image
    padded_img = np.zeros((nrows,ncols))
   
    while i < nrows:
        j = 0
        while j < ncols:        
            bitstreamed = array[i:i+8,j:j+8]  
            block=bitstreamed.flatten()             
            block = izigzag(block)            
            dequantized = quantize(block,component,quality,inverse=True,)                
            padded_img[i:i+8,j:j+8] = idct2D(dequantized)        
            j = j + 8        
        i = i + 8
    #Clip the image intensities so none are below 0 and above 255  
    padded_img[padded_img > 255] = 255
    padded_img[padded_img < 0] = 0
   
    padded_img = np.uint8(padded_img)
    cv2.imshow('decoded padded image.jpg', padded_img)
    cv2.waitKey(0)
    
    # Remove the image padding to make the dimensions divisible by 8
    decoded_img = padded_img[0:nrows,0:ncols]
    cv2.imshow('decodedimage', decoded_img)
    cv2.waitKey(0)
    return decoded_img

class Example(Frame):
    def __init__(self):
        super().__init__()

        self.initUI()    # initiate the GUI

    def initUI(self):
        self.master.title("GuI compression")
        self.pack(fill=BOTH, expand=True)

        frame = Frame(self)   # frame for Kilograms
        frame.pack(fill=X)
        
        image_select = Button(frame, text="Select file", command=select_image)
        image_select.pack(side="top", fill="both", expand="yes", padx="10", pady="10")


        lbl_component = Label(frame, text="Component")
        lbl_component.pack()

        entry_component = Entry(frame)
        entry_component.pack()
        
        lbl_quality = Label(frame, text="Quality")
        lbl_quality.pack()

        entry_quality = Entry(frame)
        entry_quality.pack()
        
        lbl_blocksize = Label(frame, text="Blocksize")
        lbl_blocksize.pack()

        entry_blocksize = Entry(frame)
        entry_blocksize.pack()

        entry_output = Entry(frame)
        entry_output.pack(fill=X, padx=(500, 30), expand=True)

        frame_btn = Frame(self)    # frame for buttons
        frame_btn.pack(fill=BOTH, expand=True, padx=20, pady=5)

        btn_convert=Button(frame_btn, text="Apply component",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_component: applyc(entry_obj))
        btn_convert.pack(side=LEFT, padx=5, pady=5)
        
        btn_convert=Button(frame_btn, text="Apply quality",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_quality: applyq(entry_obj))
        btn_convert.pack(side=LEFT, padx=5, pady=5)
        
        btn_convert=Button(frame_btn, text="Apply blocksize",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_blocksize: applyb(entry_obj))
        btn_convert.pack(side=LEFT, padx=5, pady=5)
        
        btn_convert=Button(frame_btn, text="Select Original",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: select_original())
        btn_convert.pack(side=LEFT, padx=5, pady=5)
        
        frame_btn2 = Frame(self)    # frame for buttons
        frame_btn2.pack(fill=BOTH, expand=True, padx=20, pady=5)
        
        btn_convert=Button(frame_btn2, text="Deompress!",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: applydecom())
        btn_convert.pack()
        btn_convert=Button(frame_btn2, text="Metrics",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: metrics())
        btn_convert.pack()
        
        



def main():
    root = Tk()
    root.geometry("500x400+400+200")
    app = Example()
    root.mainloop()

if __name__ == '__main__':
    main()