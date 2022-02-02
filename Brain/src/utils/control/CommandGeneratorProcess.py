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


        speed = 0.1
        angle = 0
        prev_angle = 0
        inc = -15.0
        start = time.time()
        drive,steer = {},{}
        inputs = []

        try:
            while True:
                #Receive lane detection information.
                try:
                    max_dist, min_dist = 100,30

                    # inputs = [inPs[0].recv() for _ in range(3)]
                    l_dist,r_dist = inPs[0].recv()
                    # print(f'Input:{x}, {dir}')


                    if l_dist and r_dist:
                        if l_dist > max_dist: l_dist = max_dist
                        if r_dist > max_dist: r_dist = max_dist

                        if l_dist < min_dist: l_dist = min_dist
                        if r_dist < min_dist: r_dist = min_dist
                    
                    elif l_dist and not r_dist:
                        if l_dist > max_dist: l_dist = max_dist
                        if l_dist < min_dist: l_dist = min_dist
                        r_dist = max_dist
                    elif r_dist and not l_dist:
                        if r_dist > max_dist: r_dist = max_dist
                        if r_dist < min_dist: r_dist = min_dist
                        l_dist = max_dist

                    print(f'l_dist: {l_dist},r_dist: {r_dist}')
                    x =  r_dist - l_dist

                    print(f'x: {x}')
                    angle = x * (20/(max_dist-min_dist))

                    print(f'Angle: {angle}')

                    if (l_dist,r_dist) == (0,0): #No lanes were detected
                        drive = {'action':'1',
                                 'speed': 0.00}
                        steer = {'action':'2',
                                 'steerAngle': 0.00}
                        angle = 0.00

                    else:
                            drive = {'action':'1',
                                     'speed': 0.00}
                            steer = {'action':'2',
                                     'steerAngle': float(angle)}
                    

                    dir = "LEFT" if angle > 0 else "RIGHT"
                    # print(f'{x} -> {dir}: {angle}\n')


                    # if time.time() - start > 20:
                    #     print('Time Limit Reached')
                    #     drive = {'action':'1',
                    #              'speed': 0.0}
                    #     steer = {'action':'2',
                    #              'steerAngle': 0.00}
                    
                    # drive = {'action':'1',
                    #         'speed': 0.8}
                    # steer = {'action':'2',
                    #          'steerAngle': inc}
                    
                    send([drive,steer])
                    


                except Exception as f: print(f)
                           

        except Exception as e: print(e)


        self.server_socket.close()