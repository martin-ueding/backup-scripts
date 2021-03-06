.. Copyright © 2013-2016 Martin Ueding <dev@martin-ueding.de>

#########
Changelog
#########

v3.3.3
    Released: 2016-07-21 14:03:27 +0200

    - Fix previous fix. Sorry!

v3.3.2
    Released: 2016-07-21 13:47:00 +0200

    - Remove ``termcolor`` dependency.

v3.3.1
    Released: 2015-07-26

    - Fail early when ``sshfs`` fails.

v3.3.0
    Released: 2015-07-12

    - Support for ``@list`` entries in the ``todo.txt``.

v3.2.0
    Released: 2015-06-28

    - Support for the Jolla stuff.

v3.1.0
    Released: 2015-03-22

    ``android-sync``:
        - Automatically delete all ``Download/Einkaufsliste*.pdf``
        - Automatically move all ``Download/*.gpx`` files
        - Add ``--offline`` such that the reading list is not generated again,
          which sometimes need an internet connection.

v3.0.0
    Released: 2015-01-16

    - ``backup-external`` now takes some of the responsibilities of
      ``android-sync``. This means that you have to change the
      ``backup-external.ini`` file and add your Android devices there.
      ``backup-external`` now has two new options, ``rsync-options`` and
      ``only-formats``. This seems to be a good setting:

      .. code:: ini

          rsync-options = --max-size=1G --size-only --no-times --no-perms --prune-empty-dirs --inplace
          only-formats = pdf mp4 webm html mp3 ogv png jpg jpeg txt

v2.8.1
    Released: 2015-01-12

    - Fix bug that made ``backup-external`` unusable since a variable name was
      wrong in the program.

v2.8.0
    Released: 2015-01-12

    - Use ``-R`` option of ``rsync`` to transfer all files with a single
      connection and run of ``rsync``.

    - Add a new ``--size`` switch to ``backup-external`` which will use ``du``
      compute the total size of the backup.

v2.7.0
    Released: 2015-01-10

    - Automatically rename YouTube URLs in the reading list to give the video
      title.

v2.6.1
    Released: 2014-12-23

    - Attemt to create leading directories on local paths

v2.6.0
    Released: 2014-12-23

    - Add simple provisioning script that only creates a single encrypted disk
      on an already partitioned disk

v2.5.0
    Released: 2014-12-20

    - Adding experimental provisioning script

v2.4
    Released: 2014-11-30

    - Compile ``.desktop`` files from the reading list folder into a single
      HTML page to use on the device.
    - Fix folder creation error when using USB.

v2.3
    Released: 2014-11-27

    - Allow for different ssh user in the configuration file
    - Remove ``hostname.txt``, use command line specified name

v2.2.1
    Released: 2014-11-07

    - Catch error for each line in the ``todo.txt`` file individually.

v2.2
    Released: 2014-11-06

    - Add progress option for config.

v2.1.1
    Released: 2014-11-03

    - Delete excluded PDF files automatically.

v2.1
    Released: 2014-11-03

    - Copy MP4 files to reading device as well.

v2.0
    Released: 2014-08-11

    - Better configuration. This breaks all your existing configuration. And it
      is not documented yet, sorry :-/.

v1.22.1
    Released: 2014-06-29

    - *backup-chaos*: Limit transfer size to 40 MB.


v1.22
    Released: 2014-06-28

    - *android-sync*: Create an empty ``todo.txt`` on the device. That makes it
      easier to start taking notes.

v1.21
    Released: 2014-06-27

    - *android-sync*: Delete files on device that are not present on the host
      any more

v1.20
    Released: 2014-06-01

    - Add script for another computer.
    - Change maximum sizes for Android.

v1.19.4
    Released: 2014-05-26

    - *backup-chaos*: Ignore all files that are larger than 200 MB.

v1.19.3
    Released: 2014-04-29

    - *android-sync*: Import TODO items right away. In case of an error later
      on, this will make sure that they got imported.

v1.19.2
    Released: 2014-03-31

    - Use JSON instead of YAML to cut external dependencies

v1.19.1
    Released: 2014-03-19

    - Fix name of *backup-external* script

v1.19
    Released: 2014-03-19

    - *android-sync*: Put the folders into a config file

v1.18
    - Make this a Python 3 package which calls its methods directly, not via
      the shell
    - Use INI style config file for *android-sync*
    - Delete empty TODO folder after sync

v1.17.1
    - *backup-external*: Change Gamma partition names

v1.17
    - *android-sync*: Import TODO items
    - *android-sync*: Fix arguments in constructor

v1.16
    - *android-sync*: Accept command line arguments for the devices

v1.15.1
    - Install via makefile only

v1.15
    - *android-sync*: Rewrite in Python 3

v1.14
    - *backup-external*: Use ``termcolor`` instead of my own ``colorcodes``
      module. Make the headings nicer.

v1.13.2
    - *android-sync*: Empty ``DCIM/Camera``

v1.13.1
    - *android-sync*: Sync documents for flat as well

v1.13
    - *android-sync*: Sync ``Pictures/Skitch`` as well

v1.12.1
    - *android-sync*: Fix some errors that caused the script to exit early

v1.12
    - *android-sync*: Simplify script
    - *android-sync*: Discover devices with zeroconf

v1.11
    - *android-sync*: Sync stuff to read

v1.10.1
    - *backup-webserver*: Perform MySQL dump first

v1.10
    - Change the usage of ``backup-status``

v1.9
    - *backup-external*: Support ``-data`` and ``-info`` partitions

v1.8.3
    - *android-sync*: New folders

v1.8.2
    - **Added**: *backup-chaos* script

v1.8.1
    - *android-sync*: Rename GPX files

v1.8
    - *backup-webserver*: Start ``multitail`` in new window

v1.7.2
    - *backup-webserver*: Do not stop on errors

v1.7.1
    - *android-sync*: Sync physik313 module

v1.7
    - *android-sync*: Sync ``/sdcard/Locus/maps`` between devices

v1.6.3
    - Change folder name

v1.6.2
    - Make this ready for release

v1.6.1
    - *android-sync*: Move GPX files automatically

v1.6
    - *android-sync*: Backup of ``~/Dokumente/Studium`` onto the phone
    - *android-sync*: Show disk usage

v1.5.8
    - *android-sync*: Copy links
    - *android-sync*: Copy MP3 files by size only

v1.5.7
    - *android-sync*: Copy LaTeX documentation that is used in ``header.tex``
      onto the device
    - *android-sync*: Empty ``Locus/export`` bin
    - Changelog within the repository

v1.5.6
    - *android-sync*: Move files first
    - *android-sync*: Sync all module handbooks

v1.5.5
    - *android-sync*: Sync Abizeitung

v1.5.4
    - Correct Python version for installation
    - Remove -e flag

v1.5.3
    - *android-sync*: Copy podcasts

v1.5.2
    - *backup-webservers*: Fix subfolder key

v1.5.1
    - *backup-status*: Add both flag

v1.5
    - *backup-webservers*: Sensitive data into INI file
    - New modules

v1.4
    - *android-sync*: Allow IP as first argument
    - *android-sync*: Copy dotfiles into /sdcard as well
    - *android-sync*: Delete empty dropfolder
    - *android-sync*: Do some tasks only for one device
    - *android-sync*: Install nexus script
    - *android-sync*: Move images and sounds from Tablet
    - *android-sync*: Print Nexus banner for Nexus 10
    - *android-sync*: Retrieve hostname from device
    - *android-sync*: Script for both devices
    - *android-sync*: Use unique folder
    - Convert to Python 3
    - Create directories
    - Encoding before copyright message
    - Exclude thumbnails
    - Fix permissions
    - Make setup executable
    - Print usage
    - Refactoring
    - Remove license
    - Rename script
    - Update clean target
    - Use colorcodes module
    - Use other prettytable module
    - Use real copyright symbol

v1.3
    - *android-sync*: Nexus 10 script

v1.2
    - *backup-webservers*: Use old Bash scripts

v1.1.5
    - Delete excluded files

v1.1.4
    - Fix imports

v1.1.3
    - Get the imports right

v1.1.2
    - *setup*: Actually include Python module in installation

v1.1.1
    - *setup*: Use Debian directory layout for Python modules

v1.1
    - *backup-webservers*: Use Python for the webserver backup
    - Merge a bunch of smaller projects into this

v1.0
    Initial Release

.. vim: spell tw=79
