#  Copyright (c) 2016 Phil Birkelbach
#
#  This program is free software; you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation; either version 2 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA 02111-1307, USA.

# This is the CAN-FIX plugin. CAN-FIX is a CANBus based protocol for
# aircraft data.

# This file loads the JSON protocol description file

import json
import os
import copy

groups = []
parameters = {}


class ParameterDef():
    """Defines an individual CANFIX parameter.  The database would
    essentially be a list of these objects"""
    def __init__(self, name):
        self.name = name
        self.units = None
        self.type = None
        self.multiplier = 1.0
        self.min = None
        self.max = None
        self.index = None
        self.format = None
        self.metadata = {}
        self.remarks = []

    def __unicode__(self):
        s = u"(0x%03X, %d) %s\n" % (self.id, self.id, self.name)
        if self.type:
            s += u"  Data Type: %s\n" % self.type
        if self.units:
            if self.multiplier == 1.0:
                s += u"  Units:     {}\n".format(self.units)
            else:
                s += u"  Units:     {} x {}\n".format(self.units, str(self.multiplier))
        if self.min:
            s += u"  Min:       %s\n" % str(self.min)
        if self.max:
            s += u"  Max:       %s\n" % str(self.max)
        if self.format:
            s += u"  Format:    %s\n" % self.format

        if self.index:
            s += u"  Index:     %s\n" % self.index
        if self.metadata:
            s += u"  Meta Data:\n"
            for each in self.metadata:
                s += u"   0x%02X - %s\n" % (each, self.metadata[each])
        if self.remarks:
            s += u"  Remarks:\n"
            for each in self.remarks:
                s += u"    " + each + u"\n"
        return s

    def __str__(self):
        return unicode(self).encode('utf-8')

def __getText(element, text):
    try:
        return element.find(text).text
    except AttributeError:
        return None

def __getFloat(s):
    """Take string 's,' remove any commas and return a float"""
    if s:
        return float(s.replace(",",""))
    else:
        return None

with open(os.path.dirname(__file__)+"/canfix.json") as f:
    cf = json.load(f)

groups = cf["groups"]

for each in cf["parameters"]:
    pid = each["id"]
    count = each["count"]

    p = ParameterDef(each["name"])
    p.units = each["units"] if "units" in each else None
    p.format = each["format"] if "format" in each else None
    p.type = each["type"]
    p.multiplier = float(each["multiplier"]) if "multiplier" in each else None
    p.min = each["min"] if "min" in each else None
    p.max = each["max"] if "max" in each else None
    p.index = each["index"]
    for x in each["metadata"]:
        p.metadata[int(x)] = each["metadata"][x]
    p.remarks = each["remarks"]

    if count > 1:
        for n in range(count):
            np = copy.copy(p)
            np.name = p.name + " #" + str(n+1)
            np.id = pid + n
            parameters[pid+n] = np
    else:
        p.id = pid
        parameters[pid] = p


def getGroup(id):
    for each in groups:
        if id >= each['startid'] and id <= each['endid']:
            return each

# Returns the parameter given by 'name'
def getParameterByName(name):
    n = name.lower()
    for each in parameters:
        if parameters[each].name.lower() == n:
            return parameters[each]
    return None
