import asyncio
import json
import time
import os
import sys

from aiofile import AIOFile


class MainClient(object):

    targetIP = '127.0.0.1'
    targetPort = 1230
    chunkSize = 128

    def __init__(self, loop=None):
        #self._loop = loop or asyncio.get_event_loop() 
        pass

    def requestCars(self, rawFilter):
        return asyncio.run(self.carsQuery(rawFilter))


    async def carsQuery(self, rawFilter):
        '''TCP запрос на получение машин по фильтру'''

        loop = asyncio.get_running_loop()
        reader, writer = await asyncio.open_connection(self.targetIP, self.targetPort, loop=loop)
        curTime = time.time()
        print('Send: %r' % rawFilter)
        writer.write(json.dumps(rawFilter).encode())

        data = bytearray()
        while True:
            chunk = await reader.read(self.chunkSize)
            if not chunk:
                break
            data += chunk

        curTime = time.time() - curTime

        carsDict = json.loads(data.decode())

        print(*['--------------', f"Recieved data after {curTime} seconds! Closed the socket."], sep='\n')

        writer.close()

        return carsDict
