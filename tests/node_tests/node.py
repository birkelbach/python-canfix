#!/usr/bin/env python

import can
import canfix
import time
import math
import threading


channel = 'vcan0'
interface = 'socketcan'

bus = can.interface.Bus(channel, bustype = interface)

class Node(object):
    def __init__(self, node, device = 0x00, model = 0x00, version = 0x00):
        self.node = node
        self.device = device
        self.model = model
        self.version = version

        # This is an array of tuples.  The tuple is the parameter object
        # itself and the second is a callable that takes the current value
        # and should return the value to send.
        self.parameters = []

    def addParameter(self, name, func):
        p = canfix.Parameter()
        p.node = self.node
        p.name = name
        self.parameters.append((p, func))
        return p

    def sendUpdate(self, bus, full=False):
        for each in self.parameters:
            p = each[0]
            func = each[1]
            p.value = func(p.value)
            bus.send(p.msg)

        if full: # Here we send a whole report
            pass

    def nodeSpecificMessage(self, m):
        if p.controlCode == 0: # Node Identification
            x = canfix.NodeSpecific()
            x.sendNode = self.node
            x.destNode = 0x00
            x.data = [0x01,self.device,self.version,0,0,0]
            x.data[3] = self.model & 0xFF
            x.data[4] = (self.model >> 8) & 0xFF
            x.data[5] = (self.model >> 16) & 0xFF
            bus.send(x.msg)


def sinWave(offset, range, length):
    def f(x):
        y = offset + (range * math.sin((time.time() % length) * (6.28/length)))
        return y
    return f

airData = Node(15, 0x32, 0x0A0B0C, 0x01)
airData.addParameter("Indicated Airspeed", sinWave(110, 0.5, 4))
airData.addParameter("Indicated Altitude", sinWave(5500, 20, 8))
airData.addParameter("Heading", sinWave(180, 20, 7))
airData.addParameter("Vertical Speed", sinWave(0, 2000, 11))
airData.addParameter("Yaw Angle", sinWave(0, 5, 5))

ahrs = Node(16, 0x45)
ahrs.addParameter("Pitch Angle", sinWave(0, 2.0, 12))
ahrs.addParameter("Roll Angle", sinWave(0, 1.0, 6))

engine = Node(64, 64, 1, 2)
engine.addParameter("N1 or Engine RPM #1", sinWave(2400, 10, 10))
engine.addParameter("Manifold Pressure #1", sinWave(23.8, 0.3, 5))
engine.addParameter("Oil Pressure #1", sinWave(75, 1.0, 5))
engine.addParameter("Oil Temperature #1", sinWave(100, 15.0, 7))
engine.addParameter("Coolant Temperature #1", sinWave(75, 5.0, 7))
engine.addParameter("Fuel Quantity #1", sinWave(15, 5.0, 7))
engine.addParameter("Fuel Pump Pressure #1", sinWave(15, 5.0, 7))
engine.addParameter("Cylinder Head Temperature #1", sinWave(85, 50.0, 7))
engine.addParameter("Exhaust Gas Temperature #1", sinWave(1915, 50.0, 7))
engine.addParameter("Fuel Flow #1", sinWave(8, 5.0, 7))


count = 0

while True:
    if count % 4 == 0:
        airData.sendUpdate(bus)
    if count % 10 == 0:
        engine.sendUpdate(bus)
    ahrs.sendUpdate(bus)
    count += 1

    m = bus.recv(0.1)
    if m:
        p = canfix.parseMessage(m)
        if type(p) == canfix.NodeSpecific:
            if p.destNode == airData.node:
                airData.nodeSpecificMessage(p)
            if p.destNode == ahrs.node:
                ahrs.nodeSpecificMessage(p)
            if p.destNode == engine.node:
                engine.nodeSpecificMessage(p)

