import cv2
import numpy as np
import os
from decord import VideoReader
from decord import cpu, gpu

from tkinter import filedialog as fd
from tqdm import tqdm

def get_frames(video_path, end=True) :
    """
        Return a list of the frames (as NDArray from Mxnet)
        Decord is very fast comapred to cv2
    """
    # get fps
    video = cv2.VideoCapture(video_path)
    fps = video.get(cv2.CAP_PROP_FPS)

    # base fps is 30
    vr = VideoReader(video_path, ctx=cpu(0))
    frames = []
    for i in tqdm(range(0, len(vr), int((fps+1)//30))) :
        image = vr[i].asnumpy()
        if end :
            image = cv2.resize(image, (min(int(400*image.shape[1] / image.shape[0]),540), 400))
        frames.append(image)

    return frames

class Model :
    def __init__(self) :
        # current idx of the final video
        self.current_frame = 0
        # frames of videos
        self.videos = []
        # index of the current video
        self.video_idx = -1
        # length of current video
        self.length_current = 1
        # current idx of the video
        self.frame = 0
        # pairs of idx for the final video
        self.pairs = []
        # paths of the videos
        self.videos_paths = []
        # saving ?
        self.saving = False
        # speed
        self.speed = 1
    
    def slower(self) :
        self.speed = self.speed / 2
        self.speed = max(0.5, self.speed)

    def faster(self) :
        self.speed *= 2
        self.speed = min(2, self.speed)

    def get_speed(self) :
        if self.speed < 1 :
            return "Speed x{:.1f}".format(self.speed)
        return "Speed x{}".format(int(self.speed))

    def show_frames(self) :
        # loop throught all the pairs
        for video_idx, frame_idx in self.pairs :
            # Load the image
            ori_size = (1920,1080)
            # we put a try in case there is only video 1 or video 2
            try :
                image = self.videos[video_idx][frame_idx]
            except :
                image = np.zeros((10,10,3))
                image = cv2.resize(image, (min(int(400*ori_size[1] / ori_size[0]),540), 400))
            

            # uint8 for display
            image_total = image.astype(np.uint8)
            # RGB
            image_total = cv2.cvtColor(image_total, cv2.COLOR_BGR2RGB)
            # show
            cv2.imshow("video test", image_total)
            # you can interrupt it with the key 'q'
            if cv2.waitKey(25) & 0xFF == ord('q'):
                break

        cv2.destroyAllWindows()

    def create_video(self, video_name) :
        # load the videos again (not to have the resize factor)
        all_videos_frames = []
        for video_path in self.videos_paths :
            all_videos_frames.append(get_frames(video_path, end=False))

        # final size to resize (in case they are not the same)
        all_frames = []
        image_size = (all_videos_frames[0][0].shape[0], all_videos_frames[0][0].shape[1])
        for video_idx, frame_idx in tqdm(self.pairs) :
            # load the images
            frame = all_videos_frames[video_idx][frame_idx]
            # resize
            frame = cv2.resize(frame, image_size[::-1], interpolation=cv2.INTER_CUBIC)
            # npuint8
            image_total = frame.astype(np.uint8)
            # RGB
            image_total = cv2.cvtColor(image_total, cv2.COLOR_BGR2RGB) 
            all_frames.append(image_total)
        
        # with open cv, write the video : format mov or mp4!
        final_size = image_total.shape[:2][::-1]
        if not os.path.exists("videos") :
            os.mkdir("videos")
        # the name if set as a global variable
        out = cv2.VideoWriter(os.path.join("videos", video_name+".mov"),cv2.VideoWriter_fourcc(*'MP4V'), 30, final_size)
        for frame in tqdm(all_frames) :
            out.write(frame)
        out.release()

    def get_current_video(self) :
        """
            return the current video
        """
        return self.videos[self.video_idx]

    def load_frames(self) :
        """
            Load the frames of the current video
            Result of when someone opens a file
        """
        # accept all : If there are errors, it's on you
        filetypes = (
            ('All files', '*.*'),
        )
        # for the file visual
        filename = fd.askopenfilename(
            title='Open a file',
            initialdir='/',
            filetypes=filetypes)
        # retrieve the frames
        frames = get_frames(filename)
        # restart the idx
        self.frame = 0
        # video 
        self.videos_paths.append(filename)
        self.videos.append(frames)
        self.length_current = len(frames)
        self.video_idx += 1
        self.saving = False
        
        
  