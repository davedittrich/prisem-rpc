=======================================================
                PRISEM RPC utilities
=======================================================

* GitHub repo: https://github.com/davedittrich/prisem-rpc/
* Documentation: https://prisem-rpc.readthedocs.io/
* License: Apache License Version 2.0

The PRISEM RPC utilities were written as part of the
Public Regional Information Security Event Monitoring
project, sponsored by the City of Seattle with funding
from the Department of Homeland Security.

These utilities implement an `AMQP`_-based Remote Procedure
Call (RPC) client/server processing framework, and a
fanout based logging mechanism using a `RabbitMQ`_ server
for AMQP.

.. figure:: docs/source/images/rabbitmq-bus-architecture-v3.png
   :alt: PRISEM RabbitMQ bus architecture
   :width: 90 %
   :align: center

   PRISEM RabbitMQ bus architecture

..

.. _AMQP:  https://www.amqp.org/
.. _RabbitMQ: https://www.rabbitmq.com/

They were used to transmit blacklists for use by a
Netflow-to-SiLK network flow monitoring system called
*Botnets* written by the University of Michigan, for
remotely querying the historic SiLK network flow
files to perform basic network forensics tasks using
shared Indicators of Compromise and Observables,
and for performing text-based anonymization of these
reports for external sharing.

.. figure:: docs/source/images/rabbitmq-flows.png
   :alt: PRISEM data flows through RabbitMQ
   :width: 90 %
   :align: center

   PRISEM data flows through RabbitMQ

..

Setup
-----

The following are simple stand-alone steps for working with this
repository by itself. (These tools were integrated into the
Distributed Incident Management System (DIMS) platform and
are automatically installed in that environment.)

First, you need to create a virtual environment and activate it.

.. code-block:: none

  $ pip install virtualenv
  $ virtualenv .venv
  $ . .venv/bin/activate
  (.venv)$ 

..


Next, install required pre-requisites into the environment.

.. code-block::

  (.venv)$ pip install -U -r requirements.txt

..

Now, install the PRISEM RPC utilities into the virtual environment.

.. code-block::

  (.venv)$ python setup.py install

..

Contact:
--------

Dave Dittrich < dave.dittrich @ gmail.com >

.. |copy|   unicode:: U+000A9 .. COPYRIGHT SIGN

Copyright |copy| 2010-2017 David Dittrich < dave.dittrich @ gmail.com >. All rights reserved.

.. include:: LICENSE
   :literal:
