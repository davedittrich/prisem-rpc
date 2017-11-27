.. _installation:

Installing the PRISEM utilities
-------------------------------

This section describes installation of the PRISEM AMQP
utilities in a virtual environment. This virtual environment
encapsulates all of the dependencies and PRISEM AMQP
utilities within a single environment that is activated
by scripts that call these utilities (including
service deaemons that are run by ``init`` or its 
equivalent on Linux distributions).


.. todo::

   Describe invoking the virtual environment manually using
   ``workon`` from ``virtualenvwrapper``, or automatically
   by way of BASH functions that hook the builtin commands
   ``cd``, ``pushd`` and ``popd``.

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ workon
    dims
    prisem
    pygraph

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ echo $PATH
    /Users/dittrich/.virtualenvs/prisem/bin:/Users/dittrich/perl5/perlbrew/bin:/Users/dittrich/perl5/perlbrew/perls/perl-5.12.5_WITH_THREADS/bin:/Users/dittrich/bin:/opt/dims/bin:/opt/cif/bin:/opt/local/bin:/opt/local/Library/Frameworks/Python.framework/Versions/2.7/bin:/opt/cif/bin:/Users/dittrich/bin:/opt/dims/bin:/usr/bin:/bin:/usr/sbin:/sbin:/usr/local/bin:/opt/local/bin:/usr/local/MacGPG2/bin

..

.. todo::

   Describe how the environment is activated from within
   scripts that wish to use these utilities.

..

The scripts can be installed manually into the virtual environment
using ``pip``. Before installation, ``pip`` shows the following
packages installed in the virtual environment:

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ pip freeze
    arrow==0.5.0
    gnureadline==6.3.3
    ipdb==0.8
    ipython==2.4.0
    pika==0.9.14
    python-dateutil==2.4.0
    semantic-version==2.3.1
    six==1.9.0

..

Using ``pip`` to install the contents of the ``src/`` directory
will use the ``setup.py`` file to control installation:

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ pip install -e .
    Obtaining file:///Users/dittrich/git/prisem/src
        warning: manifest_maker: MANIFEST.in, line 2: 'recursive-include' expects <dir> <pattern1> <pattern2> ...
    Installing collected packages: prisem-rpc
      Running setup.py develop for prisem-rpc
        warning: manifest_maker: MANIFEST.in, line 2: 'recursive-include' expects <dir> <pattern1> <pattern2> ...
        Creating /Users/dittrich/.virtualenvs/prisem/lib/python2.7/site-packages/prisem-rpc.egg-link (link to .)
        Adding prisem-rpc 1.1.1 to easy-install.pth file
        Installing anon_client script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing anon_server script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing cifbulk_client script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing cifbulk_server script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing crosscor.sh script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing crosscor_client script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing crosscor_server script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing cumdist script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing logmon script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing rpcserver script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing rwfind_client script to /Users/dittrich/.virtualenvs/prisem/bin
        Installing rwfind_server script to /Users/dittrich/.virtualenvs/prisem/bin
        Installed /Users/dittrich/git/prisem/src
    Successfully installed prisem-rpc

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ git stat
    ?? src/prisem-rpc.egg-info/

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ tree prisem-rpc.egg-info/
    prisem-rpc.egg-info/
    ├── PKG-INFO
    ├── SOURCES.txt
    ├── dependency_links.txt
    └── top_level.txt
    
    0 directories, 4 files

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ head prisem-rpc.egg-info/*
    ==> prisem-rpc.egg-info/PKG-INFO <==
    Metadata-Version: 1.0
    Name: prisem-rpc
    Version: 1.1.1
    Summary: PRISEM RPC scripts
    Home-page: UNKNOWN
    Author: David Dittrich
    Author-email: dittrich@speakeasy.net
    License: UNKNOWN
    Description: PRISEM RPC clients and services.
    Platform: UNKNOWN
    
    ==> prisem-rpc.egg-info/SOURCES.txt <==
    MANIFEST.in
    README
    anon_client
    anon_server
    cifbulk_client
    cifbulk_server
    crosscor
    crosscor_client
    crosscor_server
    cumdist
    
    ==> prisem-rpc.egg-info/dependency_links.txt <==
    
    
    ==> prisem-rpc.egg-info/top_level.txt <==
    rpc

..

The package ``prisem-rpc`` is now listed by ``pip`` and programs are
now available via the ``$PATH`` environment variable:

.. code-block:: rest
   :emphasize-lines: 7

   (prisem)[dittrich@localhost src (dev)]$ pip freeze
   arrow==0.5.0
   gnureadline==6.3.3
   ipdb==0.8
   ipython==2.4.0
   pika==0.9.14
   prisem-rpc==1.1.1
   python-dateutil==2.4.0
   semantic-version==2.3.1
   six==1.9.0

..

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ which anon_client
    /Users/dittrich/.virtualenvs/prisem/bin/anon_client

..

The virtual environment contains a link back to the source directory:

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ cat /Users/dittrich/.virtualenvs/prisem/lib/python2.7/site-packages/prisem-rpc.egg-link
    /Users/dittrich/git/prisem/src
    .

..

They can be removed using ``pip`` as well:

.. code-block:: bash

    (prisem)[dittrich@localhost src (dev)]$ pip uninstall prisem-rpc
    Uninstalling prisem-rpc-1.1.1:
      /Users/dittrich/.virtualenvs/prisem/lib/python2.7/site-packages/prisem-rpc.egg-link
    Proceed (y/n)? y
      Successfully uninstalled prisem-rpc-1.1.1

..

