# Copyright (c) 2019, Bosch Engineering Center Cluj and BFMC organizers
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
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE

import json
import socket
import time

from threading       import Thread

from src.templates.workerprocess import WorkerProcess

class CommandGeneratorProcess(WorkerProcess):
    # ===================================== INIT =========================================
    def __init__(self, inPs, outPs):
        """It receives lane detection information from LaneDetectionProcess,
        and sends appropriate commands to SerialProcessHandler in order to stay within the lane.
        
        Parameters
        ------------
        inPs : list(Pipe)
            0: Radius of curvature of line
            1: Position of vehicle relative to the middle of the lane
        outPs : list(Pipe) 
            List of output pipes (order does not matter)
        """
        self.command = {}
        super(CommandGeneratorProcess,self).__init__( inPs, outPs)

    # ===================================== RUN ==========================================
    def run(self):
        """Apply the initializing methods and start the threads
        """
        self._init_socket()
        super(CommandGeneratorProcess,self).run()

    # ===================================== INIT SOCKET ==================================
    def _init_socket(self):
        """Initialize the communication socket server.
        """
        self.port       =   12244
        self.serverIp   =   '0.0.0.0'

        self.server_socket = socket.socket(
                                    family  = socket.AF_INET, 
                                    type    = socket.SOCK_DGRAM
                                )
        self.server_socket.bind((self.serverIp, self.port))

    # ===================================== INIT THREADS =================================
    def _init_threads(self):
        """Initialize the send thread to transmit commands to other processes. 
        """
        sendTh = Thread(name='CommandGeneratorThread',target = self._send_command, args = (self.inPs, self.outPs, ))
        self.threads.append(sendTh)

    # ===================================== READ STREAM ==================================
    def _send_command(self, inPs, outPs):
        """"It receives lane detection information from LaneDetectionProcess,
        and sends appropriate commands to SerialProcessHandler in order to stay within the lane.
        
        Parameters
        ------------
        inPs : list(Pipe)
            0: Radius of curvature of line
            1: Position of vehicle relative to the middle of the lane
        outPs : list(Pipe) 
            List of output pipes (order does not matter)
        """

        def send(cmds): #Send a sequence of commands
            for cmd in cmds:
                if cmd == {}: continue
                for outP in outPs:
                    outP.send(cmd)




        self.command = {
            'action' : '4',
            'activate' : True
        }

        for outP in outPs:
            outP.send(self.command)
        
        speed = 0.2
        angle = 10
        start = time.time()
        try:
            while True:
                #Receive lane detection information.
                try:
                    offset,dir = inPs[0].recv()
                    
                    # print(f'{dir}: {offset}')
                    # if offset > 100: offset = 100
                    
                    # angle = 20 - offset * (20/100)

                    # self.command = {
                    #     'action': '2', #2 -> Steer command
                    #     'steerAngle': [1,-1][dir] * float(angle)
                    # }


                    if time.time() - start > 5:

                        drive = {'action':'1',
                                 'speed': float(0)}
                        steer = {'action':'2',
                                 'steerAngle': float(5)}
                    else:
                        drive = {'action':'1',
                                 'speed': float(speed)}
                        steer = {'action':'2',
                                 'steerAngle': float(0)}


                    send([drive,steer])


                except Exception as f: print(f)
                           

        except Exception as e: print(e)


        self.server_socket.close()