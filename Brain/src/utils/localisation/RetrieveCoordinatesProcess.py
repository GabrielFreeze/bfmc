
import time


from threading       import Thread
from src.templates.workerprocess import WorkerProcess
from src.data.localisationssystem.locsys import LocalisationSystem




class RetrieveCoordinatesProcess(WorkerProcess):
    lane = None
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
        """Accepts frames from the camera, performs and visualises lane detection,
        and sends a frame of the same size.
        Parameters
        ------------
        inPs : list(Pipe)
            0 - None
        outPs : list(Pipe)
            Timestamp, x_pos, y_pos, x_rot, y_rot
        """
        super(RetrieveCoordinatesProcess,self).__init__(inPs, outPs)


    # ===================================== RUN ==========================================
    def run(self):
        """ start the threads"""
        super(RetrieveCoordinatesProcess,self).run()

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the read thread to receive the video.
        """
        readTh = Thread(name = 'RetrieveCoordinatesProcess', target = self._process_stream, args = (self.inPs, self.outPs))
        self.threads.append(readTh)

    def _process_stream(self, inPs, outPs):
        """Receive location via WIFI, process it 
           and send information """
        

        #The ID of the car is set to 2. You might need to change this during the actual competition.
        #ID is in the range[0,40]

        LocalisationSystem = LocalisationSystem(ID=2)
        LocalisationSystem.start()

        print('Initialising Localisation System...')
        time.sleep(5)
        print('Localisation System Initalised')

        while True:
            
            try:
                coord = LocalisationSystem.coor()

                timestamp = coord['timestamp']     #Timestamp of received image

                x_pos = coord['coor'][0].real      #Position X-Coordinate 
                y_pos = coord['coor'][0].imag      #Position Y-Coordinate 

                x_rot = coord['coor'][0].imag      #Position X-Rotation
                y_rot = coord['coor'][0].imag      #Position Y-Rotation

                dps = 5

                x_pos = round(x_pos,dps)
                y_pos = round(y_pos,dps)

                x_rot = round(x_rot,dps)
                y_rot = round(y_rot,dps)
                
                # print(f'ID: {LocalisationSystem.ID()}\nTimestamp: {timestamp}\nPosition: {x_pos,y_pos}')
                
                dct = {'timestamp':timestamp,
                    'x_pos':x_pos,
                    'y_pos':y_pos,
                    'x_rot':x_rot,
                    'y_rot':y_rot}
            
                for outP in outPs:
                    outP.send([dct])
            except Exception as e:
                print('Localisation System stopped:' + str(e))
                break

        
        LocalisationSystem.stop()

        LocalisationSystem.join()


            