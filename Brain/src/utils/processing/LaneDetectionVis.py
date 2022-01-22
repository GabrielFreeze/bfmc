import cv2
import numpy as np

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
        
        stamps,frame = inPs[0].recv()

        lane = None

        try: lane = Lane(frame.shape[1],frame.shape[0])
        except Exception as e: print(str(e))


        while True and lane:

            #Receive

            stamps,image = inPs[0].recv()            

            #--> Processing of the image occurs here <--
            # radius,dir = lane.run(image)  
            output = lane.vis(image)          

            #Send
            for outP in outPs:
                outP.send([[stamps],output])
