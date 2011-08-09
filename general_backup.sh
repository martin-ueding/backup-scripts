#!/bin/bash
# Copyright (c) 2011 Martin Ueding <dev@martin-ueding.de>

set -e
set -u

while getopts "h" OPTION
do
	case $OPTION in
		h)
			echo "Help is not there right now. Sorry."
			exit 1;
			;;
		u)
			user="$OPTARG"
			;;
		p)
			passwd="$OPTARG"
			;;
		b)
			backupdir="$OPTARG"
			;;
		n)
			name="$OPTARG"
			;;
		s)
			server="$OPTARG"
			;;
		d)
			dumpsite="$OPTARG"
			;;
	esac
done

exit 1


# Create a current folder if it does not exist yet.
if [[ ! -d "$current" ]]
then
	mkdir -p "$current"
fi

# Create a mountpoint for the FTP.
tempdir=$(mktemp -d)
chgrp use "$tempdir"
chmod 700 "$tempdir"

# Mount the FTP
curlftpfs "$server" "$tempdir"

# Copy all the new data into the current directory
rsync -avE --delete "$tempdir/" "$current"

# Release the mounted FTP
fusermount -u "$tempdir"
rmdir "$tempdir"

# Dump the MySQL database.
sqlfile="$current/dump.sql"
if [ ! -f $sqlfile ]
then
	wget --user $usr --password $passwd -O $sqlfile \
		"$dumpsite"
fi

# Create an archive which contains the current snapshot.
tar -czf "$backupdir/$name-$(date +%y%m%d).tar.gz" -C "$backupdir" "$name"
