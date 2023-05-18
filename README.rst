=========================
Python CAN-FIX Library
=========================

python-canfix is a Python package that abstracts the details of the
CAN-FIX communication protocol.

CAN-FIX is the CAN bus implementation of a set of protocols and specifications
known as FIX. FIX stands for Flight Information eXchange and is an attempt to
standardize communication among aircraft systems in small aircraft.

The project is hosted on GitHub at...

https://github.com/birkelbach/python-canfix

Installation
============

Install ``canfix`` with ``pip``:
::

    $ pip install python-canfix


You can also install directly from the source directory by running:
::

    $ python setup.py install

The only dependency is python-can, which should be automatically installed
by the above commands.

API
===

You should be familiar with the CANFIX protocol specification before using
this library.  CANFIX has several different message types.  Each of these
types is representd by a class in this library.


NodeAlarm Class
---------------

The constructor can take one named parameter.  ``msg`` can be assigned a
python-can ``Message`` and the instantiated object will be initialized
with the correct information.

**Properties**

``NoneAlarm.node`` - Sets or returns the node address of the node that sent (or will send) the Alarm Message.  Should be an
integer between 1 and 254

``NodeAlarm.alarm`` - Sets or returns the alarm type.  The meaning of this data is dependent on the individual node type.
Should be an integer between 0 and 65,535.

``NodeAlarm.data`` - Sets or returns a list that represents the data for this alarm.  What the data represents is dependent
on the specific type of node and the alarm type.  It should be a list of bytes of up to 6 bytes in length.

``NodeAlarm.msg`` - Sets or returns a can.Message class that is suitable for use with a python-can bus.  If this property
is set with a message received from the can bus then the message will be parsed and the node, alarm and data properties
will be set accordingly.  If it is read then the message will be constructed with the node, alarm and data properties
that should have been previously set.

Example Usage::

    >>> na = canfix.NodeAlarm()
    >>> na.node = 12
    >>> na.alarm = 45321
    >>> na.data = [4,5,6,7]
    >>> na.msg
    >>> na.msg
    can.Message(timestamp=0.0, is_remote_frame=False, is_extended_id=False, is_error_frame=False, arbitration_id=0xc, dlc=0,
    data=[0x9, 0xb1, 0x4, 0x5, 0x6, 0x7])

    >>> msg = bus.recv() # Assume we read the same message that we created above
    >>> na = canfix.NodeAlarm(msg)
    >>> print(na)
    [12] Node Alarm 45321 Data 04050607


Parameter Class
---------------

The constructor can take one named parameter.  ``msg`` can be assigned a
python-can ``Message`` and the instantiated object will be initialized
with the correct information.

**Properties**

``Parameter.node`` - Sets or returns the node address of the node that sent (or will send) the Parameter.
Should be an integer between 1 and 254

``Parameter.identifier`` - Sets or returns the CAN bus identifier for this parameter.  If the identifier is out of
of range for Parameter messages a ValueError exception will be raised.  Setting this will also cause protocol specific
information to be set in the object.  This includes the data type, the engineering units, name etc.

``Parameter.name`` - Sets or returns the name of the parameter.  i.e. "Indicated Airspeed"  If the name is not found
in the protocol ValueError exception will be raised.  Setting this will also cause protocol specific
information to be set in the object.  This includes the data type, the engineering units, identifier etc.

``Parameter.index`` - Sets or returns the index of the parameter.  Should be an integer between 0 and 255.

``Parameter.failure`` - Sets or returns the flag that indicates data failure.  Should be ``True`` or ``False``

``Parameter.quality`` - Sets or returns the flag that indicates data quality.  Should be ``True`` or ``False``

``Parameter.annunciate`` - Sets or returns the flag that indicates the paramter should be annunciated.
Should be ``True`` or ``False``

``Parameter.meta`` - Sets or returns the meta data index for the Parameter.  Should be an integer between 0 and 15

``Parameter.value`` - Sets or returns the value for the parameter.  It can be a list of multiple values if the
particular parameter is expecting multiple values.  It can also be a string

``Parameter.msg`` - Sets or returns a can.Message class that is suitable for use with a python-can bus.  If this property
is set with a message received from the can bus then the message will be parsed and the properties
will be set accordingly.  If it is read then the message will be constructed with properties
that should have been previously set.

``Parameter.fullName`` - Returns a string that represents the parameter that includes the index and the index name.
This property is read only.

``Parameter.units`` - Read only property that returns a string indicating the engineering units for this Parameter.
This is a protocol specific piece of information and should not change.

``Parameter.type`` - Read only property that returns a string indicating the datatype for the Parameter.
This is a protocol specific piece of information and should not change.

``Parameter.min`` - Read only property that returns a value that indicates the minimum value for the Parameter.
This is a protocol specific piece of information and should not change.

``Parameter.max`` - Read only property that returns a value that indicates the maximum value for the Parameter.
This is a protocol specific piece of information and should not change.

``Parameter.format`` - Read only property that returns the format of the data in the Parameter value.  This is typically
used to indicated what WORD and BYTE type data means.
This is a protocol specific piece of information and should not change.

``Parameter.remarks`` - Read only property that returns a list of remarks that are associated with this Parameter
in the protocol specification.
This is a protocol specific piece of information and should not change.

``Parameter.indexName`` - Read only property that retuns he name of what the index represents.  i.e. Cylinder
This is a protocol specific piece of information and should not change.

``Parameter.multiplier`` - Read only property that returns the multiplier for the Parameter.  Some paramters use
an integer with a multiplier as the value in the message.  For example if we had a Parameter value of 123.4 and
the multiplier is 0.1 then the data that would be communicated on the bus would be 1234.  The receiver would then
multiply by 0.1 to get the original value of 123.4.  The ``python-canfix`` library handles these details for you
so you don't need to concern yourself with this detail.  It is a part of the protocol and is included here for
applications that want to display protocol specific information to the user.
This is a protocol specific piece of information and should not change.

Example Usage::

    >>> pa = canfix.Parameter()
    >>> pa.node = 2
    >>> pa.value = 123.4
    >>> print(pa)
    [2] Indicated Airspeed: 123.4 knots
    >>> pa.msg
    can.Message(timestamp=0.0, is_remote_frame=False, is_extended_id=False, is_error_frame=False, arbitration_id=0x183,
    dlc=0, data=[0x2, 0x0, 0x0, 0xd2, 0x4])


TwoWayMsg Class
---------------

The constructor can take one named parameter.  ``msg`` can be assigned a
python-can ``Message`` and the instantiated object will be initialized
with the correct information.

**Properties**

``TwoWayMsg.channel`` - Sets the channel that this message will be sent on.  There are
16 channels numbered 0-15

``TwoWayMsg.type`` - Set to either 'Request' or 'Response'  This determines which
side of the channel to use.

``TwoWayMsg.data`` - Up to eight bytes

NodeSpecific Class
------------------

The constructor can take one named parameter.  ``msg`` can be assigned a
python-can ``Message`` and the instantiated object will be initialized
with the correct information.

**Properties**

``NodeSpecific.destNode`` - Represents the node address of the node that this
message is addressed to.  Should be an integer between 1 and 254.

``NodeSpecific.controlCode`` - The control code for the messge.  Currently, valid
values are 0-10.  Future versions of the CAN-FIX specification may use 11-127 and
values from 128 to 255 are reserved for user defined functions.  The control
code is basically the function of the message.  See the CAN-FIX specification
for details.

``NodeSpecific.data`` - Up to 8 bytes of data that is dependent on which type
of message that is being sent.

Functions
---------

``parseMessage(msg)`` - When passed a ``Message`` this function figures
out what the message type is, instantiates the correct object type and
returns that object.  This function would be used for most all received
messages.

Example Usage::

  >>> msg = bus.recv()
  >>> msg
  can.Message(timestamp=0.0, is_remote_frame=False, is_extended_id=False,
  is_error_frame=False, arbitration_id=0x183, dlc=5,
  data=[0xc, 0x0, 0x0, 0xd2, 0x4])
  >>> p = canfix.parseMessage(msg)
  >>> p
  <canfix.Parameter object at 0x7f6984fe9c10>
  >>> print(p)
  [12] Indicated Airspeed: 123.4 knots
