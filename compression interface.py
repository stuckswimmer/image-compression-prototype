# -*- coding: utf-8 -*-
"""
Created on Fri Dec 13 08:26:57 2019

@author: micha
"""

import tkinter
from tkinter import *
from tkinter import filedialog
from tkinter.ttk import Frame, Button, Style
import tkinter.messagebox
import cv2

import numpy as np
import math
import os
import logging
import time

from zigzag import zigzag
from compressmeths import (rgbTOycbcr, downSample,
                     dct2D, quantize, load_quantization_table, run_length_encoding,compressratio)

global data, bitstream, path

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

def applyo(entry_widget):  # ADDED WIDGET ARGUMENT
    global output_path
    """ Some function outside class. """
    print("clicked")
    output_path = entry_widget.get()  # REFERENCE ENTRY WIDGET PASSED AS ARGUMENT
    print(output_path)
    
def applycom():
    global bitstream
    print("clicked")
    bitstream=compress(data,component,blocksize,quality)
    print(bitstream)

def save():
    print("clicked")
    write_to_file(bitstream,output_path)
    print("success")
    ratio=compressratio(path,output_path)
    messagebox.showinfo('Metrics','The new fle has a Compression ratio : '+ str(ratio))
    

def preprocess(filepath, greylevel=True, subsampling_mode=1):
    if greylevel:
        img=cv2.imread(filepath,0)
        cv2.imshow('input image', img)
        cv2.waitKey(0)
        data = np.array(img, dtype=np.uint8) 
        #data=data-128
        return data
    #for colour images
    else: 
        img=cv2.imread(filepath,1)
        Y,Cb,Cr = Image.fromarray(img).convert('YCbCr').split()
        Y = np.asarray(Y).astype(int)
        Cb = np.asarray(Cb).astype(int)
        Cr = np.asarray(Cr).astype(int)
        
        Cb =downSample(Cb, subsampling_mode)
        Cr=downSample(Cr, subsampling_mode)
        return Y,Cb,Cr
def select_image():
	# grab a reference to the image panels
    global data, path
	# open a file chooser dialog and allow the user to select an input
	# image
    path = tkinter.filedialog.askopenfilename()
    	# ensure a file path was selected
    if len(path) > 0:
		# load the image from disk, convert it to grayscale, and detect
		# edges in it
        data = preprocess(path)
        
def compress(data,component,blocksize,quality):
    global bitstream
    # get size of the image
    # No of blocks needed : Calculation
    nrows , ncols = data.shape[0],data.shape[1]
    h = np.float32(nrows) 
    w = np.float32(ncols) 
    blocksize = np.float32(blocksize)
    # if nrows / blocksize == 0:
    nbh = math.ceil(h/blocksize)
    
    #else:
    #nbh=nbh
    # if nrows / blocksize == 0:
    nbw = math.ceil(w/blocksize)
    nbw = np.int32(nbw)
    nbh = np.int32(nbh)
    blocksize=np.int32(blocksize)
    #else:
    #nbw=nbw
    # width of padded image
    H =  blocksize * nbh
    W =  blocksize * nbw
    
    # create a numpy zero matrix with size of H,W
    padded_img = np.zeros((H,W))
    
    # copy the values of img  into padded_img[0:h,0:w]
    for i in range(nrows):
            for j in range(ncols):
                    pixel = data[i,j]
                    padded_img[i,j] = pixel 
    
    
    cv2.imshow('', np.uint8(padded_img))
    cv2.waitKey(0)
    
    
    # start encoding:
    # divide image into defined block size by block size blocks
    # To each block apply a 2D discrete cosine transform and apply a quantization to each value in the block rounding in each case
    # The quantized DCT coefficients are reordered from low energy to high energy as less memory is taken up with lists of smaller numbers
    # The 1D zigzagged block is reshaped into the original block 
    
    for i in range(nbh):
        
        # Compute start and end row index of the block
        row_block_start = i*blocksize                
        row_block_end = row_block_start+blocksize
        
        for j in range(nbw):
            
            # Compute start & end column index of the block
            col_block_start = j*blocksize                       
            col_block_end = col_block_start+blocksize
                        
            block = padded_img[ row_block_start : row_block_end , col_block_start : col_block_end ]
                       
            # apply a 2D discrete cosine transform to the selected block                       
            DCT = dct2D(block)    
            #Apply quantization to DCT block given the component and the amount of compression 
            Quantized = quantize(DCT,component,quality) 
            # reorder DCT coefficients in zig zag order by calling zigzag function
            # will give a one dimensional array
            Zigzagged = zigzag(Quantized)
            # reshape the reordered array back to (blocksize by blocksize) 
            reshaped= np.reshape(Zigzagged, (blocksize, blocksize)) 
            # copy reshaped matrix into padded_img on current block corresponding indices
            padded_img[row_block_start : row_block_end , col_block_start : col_block_end] = reshaped                        
    
    cv2.imshow('', np.uint8(padded_img))
    cv2.waitKey(0)
    #The whole image is flattened into a 1 dimensional array
    arranged = padded_img.flatten()
    #The 1 dimensional array is passed through a runlength encoding function to produce a bitstream
    bitstream = run_length_encoding(arranged)
    
    # Two terms are assigned for size as well, semicolon denotes end of image to reciever
    bitstream = str(padded_img.shape[0]) + " " + str(padded_img.shape[1]) + " " + bitstream + ";"
    return bitstream

def write_to_file(bitstream,filepath):
    try:
        f = open(filepath, 'w')
    except FileNotFoundError as e:
        raise FileNotFoundError(
                "No such directory: {}".format(
                    os.path.dirname(filepath))) from e
    f.write(bitstream)      


class Example(Frame):
    def __init__(self):
        super().__init__()

        self.initUI()    # initiate the GUI

    def initUI(self):
        self.master.title("GuI compression")
        self.pack(fill=BOTH, expand=True)

        frame = Frame(self)   # frame for Kilograms
        frame.pack(fill=X)
        
        image_select = Button(frame, text="Select an image", command=select_image)
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
        
        lbl_output = Label(frame, text="File Output")
        lbl_output.pack()

        entry_output = Entry(frame)
        entry_output.pack(fill=X, padx=(5, 30), expand=True)

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
        
        btn_convert=Button(frame_btn, text="Apply output path",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: applyo(entry_obj))
        btn_convert.pack(side=LEFT, padx=5, pady=5)
        
        frame_btn2 = Frame(self)    # frame for buttons
        frame_btn2.pack(fill=BOTH, expand=True, padx=20, pady=5)
        
        btn_convert=Button(frame_btn2, text="Compress!",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: applycom())
        btn_convert.pack()
        btn_convert=Button(frame_btn2, text="Save",
                        # DEFINE ANONYMOUS FUNCTION WITH DEFAULT ARGUMENT SO IT'S
                        # AUTOMATICALLY PASSED TO THE TARGET FUNCTION.
                        command=lambda entry_obj=entry_output: save())
        btn_convert.pack()


def main():
    root = Tk()
    root.geometry("500x500+400+200")
    app = Example()
    root.mainloop()

if __name__ == '__main__':
    main()