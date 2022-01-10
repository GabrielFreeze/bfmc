import cv2
from threading       import Thread
from src.templates.workerprocess import WorkerProcess


class LaneDetectionProcess(WorkerProcess):
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
        super(LaneDetectionProcess,self).__init__(inPs, outPs)


    # ===================================== RUN ==========================================
    def run(self):
        """ start the threads"""
        super(LaneDetectionProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the read thread to receive the video.
        """
        readTh = Thread(name = 'LaneDetectionProcess', target = self._process_stream, args = (self.inPs, self.outPs))
        self.threads.append(readTh)

    def _process_stream(self, inPs, outPs):
        """Read the image from input stream, process it 
           and send the lane detection information """

        while True:

            #Receive
            stamps,image = inPs[0].recv()

            #--> Processing of the image occurs here <--

            radius = 1
            position = 1
            # print(f'Lane Detection {radius},{position}')

            #Send
            for outP in outPs:
                outP.send([radius,position])
