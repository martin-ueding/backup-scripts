.. Copyright © 2014 Martin Ueding <martin-ueding.de>

###############
backup-external
###############

Configuration
=============

The ``~/.config/backup-scripts/backup-external.ini`` could look like this:

.. code-block:: ini

    [infofiles]
    paths = ~/important.txt

    [Target USB]
    exclude = full
    include = full
    path = /media/mu/Sigma-data

    [Target Server]
    exclude = full
    host = example.org
    include = dotfiles projects
    max-size = 40M
    path =

    [Info USB-info]
    path = /media/mu/USB-info
