Install
=======

1. Install `Anaconda 3 <https://www.anaconda.com/>`_ for Python
2. Install ``msdss-users-api`` via pip or through a conda environment

.. code::

   conda create -n msdss-users-api python=3.8
   conda activate msdss-users-api
   pip install msdss-users-api[postgresql]

.. note::

    Optionally, you can also install other databases supported by ``sqlalchemy``:

    .. code::

        pip install msdss-users-api[mysql]
        pip install msdss-users-api[sqlite]