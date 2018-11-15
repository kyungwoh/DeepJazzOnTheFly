
""" Basic module to ease the use of pyOSC module https://trac.v2.nl/wiki/pyOSC

you must have pyOSC installed for this to run.

This is meant to be used by students or newies that are starting to experiment with OSC. If you are an advanced user
you probably want to bypass this module and use directly pyOSC, we have some examples of very simple use in our website.
Check the pyOSC website for more documentation.

License : LGPL

    This library is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This library is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this library; if not, write to the Free Software
    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA
    
"""

try :
    import osc4py3
    from osc4py3.as_eventloop import *
except :
    print('Install osc4py3')

import logging

def printing_handler(s,x,y):
    print('print')
    print(s,x,y)

def initOSC():
    print('init')    
    logging.basicConfig(format='%(asctime)s - %(threadName)s ø %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger("osc")
    logger.setLevel(logging.DEBUG)
    osc_startup(logger=logger)
    
def initOSCClient(ip='127.0.0.1', port=7401):
    osc_udp_client(ip,port,'client1')
    
def initOSCServer(ip='127.0.0.1', port=7402):
    print('server')
    osc_udp_server(ip, port, 'server1')

def setOSCHandler(address='', hd=printing_handler):
    print('handler')
    osc_method(address, hd) # adding our function

def closeOSC():
    osc_terminate()
    
def sendOSCMsg(address='/midievent', data=[]):
    osc_send(data, 'client1')

def createOSCBundle(address) : # just for api consistency
    return osc4py3.oscbuildparse.OSCBundle(address)
    
def sendOSCBundle(b):
    osc_send(b)

def createOSCMsg(address='/print', data=[]):
    m = osc4py3.oscbuildparse.OSCMessage()
    m.setAddress(address)
    for d in data :
        m.append(d)
    return m

def processOSC():
    print('process')
    finished = False
    while not finished:
        #print('while')
        osc_process()

