import tkinter as tk
from abc import ABC, abstractmethod
from tkinter import ttk
from functools import partial
import ast
from tqdm import tqdm

import os
import cv2
import pandas as pd
import numpy as np
from PIL import Image, ImageTk
from tkinter import filedialog as fd
import time

from decord import VideoReader
from decord import cpu, gpu

from src.model import get_frames, Model
from src.view import MyView, View

class Controler :
    def __init__(self,model : Model, view : View) :
        # load the model
        self.model = model
        # load the view
        self.view = view 

    def load_frames(self) :
        """
            Load the video via the model method
            Show the next frame ie the second afterwards
        """
        self.model.load_frames()  
        self.model.saving = False
        self.view.saving.config(text="Save") 
        self.next_frame()

    def restart(self) :
        """
            Restart all the main variable such as the indexes and the pairing
        """
        self.model.current_frame = 0
        self.model.frame = 0
        self.model.pairs = []
        self.model.videos_paths = []
        self.model.videos = []
        self.model.video_idx = -1
        self.model.saving = False
        self.view.saving.config(text="Save")
        # self.next_frame()

    def next_frame(self, *args) :
        """
            Show the next frame of the video
        """
        self.model.frame += self.model.speed
        self.model.frame = self.model.frame % self.model.length_current
        frame = self.model.get_current_video()[int(self.model.frame)]
        self.view.show_img(frame)
        # save the progress 
        if self.model.saving :
            self.model.current_frame += 1
            if len(self.model.pairs) > self.model.current_frame - 1:
                self.model.pairs[self.model.current_frame-1] = [self.model.video_idx, int(self.model.frame)+1]
            else :
                self.model.pairs.append(
                    [self.model.video_idx, int(self.model.frame)-1]
                )

        # frame idx
        self.view.frame_count.config(text="{}".format(self.model.current_frame+1))
        self.view.frame_count_curr.config(text="{}/{}".format(int(self.model.frame)+1,self.model.length_current))

    def faster(self) :
        self.model.faster()
        self.view.speed.config(text=self.model.get_speed())

    def slower(self) :
        self.model.slower()
        self.view.speed.config(text=self.model.get_speed())

    def previous_frame(self, *args) :
        """
            Show the previous frame of the video
        """
        self.model.frame -= self.model.speed
        self.model.frame = self.model.frame % self.model.length_current
        frame = self.model.get_current_video()[int(self.model.frame)]
        self.view.show_img(frame)
        # save the progress 
        if self.model.saving :
            self.model.current_frame -= 1
            if len(self.model.pairs) > self.model.current_frame - 1:
                self.model.pairs[self.model.current_frame-1] = [self.model.video_idx, int(self.model.frame)-1]
            else :
                self.model.pairs.append(
                    [self.model.video_idx, int(self.model.frame)-1]
                )
        # frame idx
        self.view.frame_count.config(text="{}".format(self.model.current_frame+1))
        self.view.frame_count_curr.config(text="{}/{}".format(int(self.model.frame)+1,self.model.length_current))
        
    def show_frames(self) :
        """
            With cv2, show the video with the current 'model.pairs' status
        """
        self.model.show_frames()

    def create_video(self) :
        """
            With the two videos, create a video similar to the one whown with 'show_frames'
            However, both videos must be loaded
        """    
        video_name = self.view.video_name_entry.get().split(".")[0]
        self.model.create_video(video_name)

    def change_saving(self) :
        self.model.saving = not self.model.saving
        if self.model.saving :
            self.view.saving.config(text="Not save")
        else :
            self.view.saving.config(text="Save")

    def start(self) :
        """
            Start the program main loop
        """
        # set up the view
        self.view.setUp(self)
        # launch it
        self.view.start_main_loop()
