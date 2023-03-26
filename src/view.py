# -*- coding: UTF-8 -*-
import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from functools import partial
import ast

import cv2
import numpy as np
from PIL import Image, ImageTk

class View(ABC) :
    @abstractmethod
    def setUp(self,controler):
        """
            Set up the tkinter view
        """
        pass

    @abstractmethod
    def start_main_loop() :
        pass

class MyView(View) :
    def setUp(self,controller):
        """
        Set up the view
        """
        # global features
        self.root = tk.Tk()
        self.root.geometry("850x500")
        self.root.title("Video Annotations")

        # Image loader
        self.image_frame = tk.LabelFrame(self.root,text="Image",width=550,height=500)
        self.image_frame.grid_propagate(False) 
        self.image_frame.grid(row=0,column=0)  
        # Preivous : click on it or left arrow
        self.previous = tk.Button(self.image_frame,text="<-",command=controller.previous_frame)
        self.previous.place(x=250, y=450)
        self.root.bind("<Left>",controller.previous_frame)
        # Next : click on it or right arrow
        self.next = tk.Button(self.image_frame,text="->",command=controller.next_frame)
        self.next.place(x=277, y=450)
        self.root.bind("<Right>",controller.next_frame)
        # show the current frame we're at globally
        self.frame_count = tk.Label(self.image_frame)
        self.frame_count.place(x=260, y=430)
        # same for current video
        self.frame_count_curr = tk.Label(self.image_frame)
        self.frame_count_curr.place(x=150, y=430)
        self.already = False
        # button to save or not
        self.saving = tk.Button(self.image_frame,text="Save",command=controller.change_saving)
        self.saving.place(x=120, y=450)
        # button for speed !
        self.speed_low = tk.Button(self.image_frame,text="Slower",command=controller.slower)
        self.speed_low.place(x=320, y=100)
        self.speed_fast = tk.Button(self.image_frame,text="Faster",command=controller.faster)
        self.speed_fast.place(x=430, y=100)
        self.speed =tk.Label(self.image_frame, text="Speed x1")
        self.speed.place(x=370, y=100)


        # Config
        self.text_frame = tk.LabelFrame(self.root,text="Config",width=300,height=500)
        self.text_frame.grid_propagate(False) 
        self.text_frame.grid(row=0,column=1) 
        # Open the first video
        load_vid = partial(controller.load_frames)
        self.open_button = ttk.Button(
            self.text_frame,
            text='Open video',
            command=load_vid
        )
        self.open_button.place(x=120, y=30)
        # restart the count of all idx at 0
        self.button_restart = tk.Button(self.text_frame, text="Restart", command=controller.restart)
        self.button_restart.place(x=130, y=60)
        # display the results of 'pairs' via cv2
        self.button_display = tk.Button(self.text_frame, text="Look at video!", command=controller.show_frames)
        self.button_display.place(x=111, y=100)
        # create and save the video!
        self.button_save = tk.Button(self.text_frame, text="Save video!", command=controller.create_video)
        self.button_save.place(x=121, y=130)
        # name of the video
        self.video_name_entry = tk.Entry(self.text_frame, bd =5)
        self.video_name_entry.place(x=95, y=160)
        
    def show_img(self, image) :
        """
            Show the image of the loaded video
        """
        ori_size = (1920,1080)
        try :
            _ = image.shape
        except :
            # if it's not an image, we replace it with zeros
            image = np.zeros((10,10,3))
            image = cv2.resize(image, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
    
        # to Image
        image_total = Image.fromarray(image.astype(np.uint8))
        # Display
        resize_image = image_total
        img = ImageTk.PhotoImage(resize_image)

        if not self.already :
            # create the label to store the image only the first time as the mainloop must be restarted
            self.image_label = tk.Label(self.image_frame,image=img)
            self.image_label.place(x=30,y=5)
            self.already = True
            self.root.mainloop()
        else :
            # update the image label
            self.image_label.configure(image=img)
            self.image_label.image = img
    
    def start_main_loop(self) :
        """
        Main loop for the view
        """
        self.root.mainloop()
