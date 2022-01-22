# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC orginazers
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:

# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.

# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.

# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.

# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

#========================================================================
# SCRIPT USED FOR WIRING ALL COMPONENTS
#========================================================================
import sys
import os

dir_path = os.path.dirname(os.path.realpath(__file__))+'/'

sys.path.append('.')

import time
import signal
from multiprocessing import Pipe, Process, Event, Queue 

# hardware imports
from src.hardware.camera.cameraprocess                      import CameraProcess
from src.hardware.camera.CameraSpooferProcess               import CameraSpooferProcess
from src.hardware.serialhandler.SerialHandlerProcess        import SerialHandlerProcess

# utility imports
from src.utils.camerastreamer.CameraStreamerProcess         import CameraStreamerProcess
from src.utils.remotecontrol.RemoteControlReceiverProcess   import RemoteControlReceiverProcess
from src.utils.processing.LaneDetectionProcess              import LaneDetectionProcess
from src.utils.processing.LaneDetectionVis                  import LaneDetectionVis
from src.utils.control.CommandGeneratorProcess              import CommandGeneratorProcess


# =============================== CONFIG =================================================
enableStream        =  True
enableCameraSpoof   =  True 
enableRc            =  True

# =============================== INITIALIZING PROCESSES =================================
allProcesses = list()


# =============================== CAMERA ===============================================
if enableStream:
    camR1, camS1 = Pipe(duplex = False)
    camR2, camS2 = Pipe(duplex = False)


    if enableCameraSpoof:
        camProc = CameraSpooferProcess([],[camS2],dir_path+'camera-spoof-vids')
    else: 
        camProc = CameraProcess([],[camS1, camS2])
    allProcesses.append(camProc)

    laneR1, laneS1 = Pipe(duplex = False)
    laneR2, laneS2 = Pipe(duplex = False)

    # laneProc = LaneDetectionProcess([camR1],[laneS1])
    # allProcesses.append(laneProc)

    # -------- Visualisation Purposes --------
    laneProc = LaneDetectionVis([camR2],[laneS2])
    allProcesses.append(laneProc)
    streamProc = CameraStreamerProcess([laneR2], [])
    allProcesses.append(streamProc)


# =============================== CONTROL =================================================

rcShR, rcShS   = Pipe(duplex = False)           # rc      ->  serial handler

#Control based on lane information
# rcProc = CommandGeneratorProcess([laneR1],[rcShS])
# allProcesses.append(rcProc)


#Remote Control from PC
# rcProc = RemoteControlReceiverProcess([],[rcShS])
# allProcesses.append(rcProc)


# Serial Handler Process
# shProc = SerialHandlerProcess([rcShR], [])
# allProcesses.append(shProc)

# ===================================== START PROCESSES ==================================
print("Starting the processes!",allProcesses)
for proc in allProcesses:
    proc.daemon = True
    proc.start()


# ===================================== STAYING ALIVE ====================================
blocker = Event()  

try:
    blocker.wait()
except KeyboardInterrupt:
    print("\nCatching a KeyboardInterruption exception! Shutdown all processes.\n")
    for proc in allProcesses:
        if hasattr(proc,'stop') and callable(getattr(proc,'stop')):
            print("Process with stop",proc)
            proc.stop()
            proc.join()
        else:
            print("Process witouth stop",proc)
            proc.terminate()
            proc.join()
