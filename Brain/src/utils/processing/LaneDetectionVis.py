import cv2
import numpy as np
import time

from threading       import Thread
from src.templates.workerprocess import WorkerProcess
from src.utils.processing.LaneDetectionClass import Lane




class LaneDetectionVis(WorkerProcess):
    lane = None
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
        """Accepts frames from the camera, performs and visualises lane detection,
        and sends a frame of the same size.
        Parameters
        ------------
        inPs : list(Pipe)
            0 - video frames
        outPs : list(Pipe)
            List of output pipes (order does not matter)
        """
        super(LaneDetectionVis,self).__init__(inPs, outPs)


    # ===================================== RUN ==========================================
    def run(self):
        """ start the threads"""
        super(LaneDetectionVis,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the read thread to receive the video.
        """
        readTh = Thread(name = 'LaneDetectionVis', target = self._process_stream, args = (self.inPs, self.outPs))
        self.threads.append(readTh)

    def _process_stream(self, inPs, outPs):
        """Read the image from input stream, process it 
           and send the lane detection information """
        
        stamps,image = inPs[0].recv()
        # image = cv2.resize(image,(image.shape[1]//2,image.shape[0]//2),cv2.INTER_AREA)

        lane = None

        try: lane = Lane(image.shape[1]//4,image.shape[0]//4)
        except Exception as e: print(str(e))


        while True and lane:

            #Receive


            #--> Processing of the image occurs here <--
            # radius,dir = lane.run(image)  
            # image = lane.set_gray(image)
            # frame = lane.eq_hist(frame)

            # image = lane.bin_thresh(image,param1=170,param2=255)

            # frame = lane.get_roi(frame)
            # frame = lane.transform(frame, lane.M)

            #Send
            image = cv2.resize(image,(image.shape[1]//4,image.shape[0]//4),cv2.INTER_AREA)   
            image = lane.vis_new(image)
            # image = lane.set_gray(image)
            # image = lane.bin_thresh(image)
            # image = lane.block_front(image)
            # image = lane.get_roi(image)
            # image = lane.transform(image, lane.M)
            image = cv2.resize(image,(image.shape[1]*4,image.shape[0]*4),cv2.INTER_AREA)

            for outP in outPs:
                outP.send([[stamps],image])
            time.sleep(0.02)
            stamps,image = inPs[0].recv()
