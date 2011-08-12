#!/bin/bash
# Copyright (c) 2011 Martin Ueding <dev@martin-ueding.de>

set -e
set -u
set -x

subfolder=
user=
passwd=
dumpsite=

while getopts "hu:p:b:n:s:d:f:" OPTION
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
		f)
			subfolder="$OPTARG"
			;;
	esac
done


# Create a current folder if it does not exist yet.
current="$backupdir/$name"
if [[ ! -d "$current" ]]
then
	mkdir -p "$current"
fi

# Test whether this needs to be backuped already
if [[ $(( $(date +%s) - $(stat "$current/performed") )) -gt $(( 3600 * 24 * 3)) ]]
then
	echo "This needs a backup"
else
	exit 0
fi

# Create a mountpoint for the FTP.
tempdir=$(mktemp -d)
chgrp fuse "$tempdir"
chmod 700 "$tempdir"

# Mount the FTP
curlftpfs "$server" "$tempdir"

# Copy all the new data into the current directory
rsync -avE --delete "$tempdir/$subfolder" "$current"

# Release the mounted FTP
fusermount -u "$tempdir"
rmdir "$tempdir"

# Dump the MySQL database.
if [[ -n "$user" && -n "$passwd" && -n "$dumpsite" ]]
then
	sqlfile="$current/dump.sql"
	if [ ! -f $sqlfile ]
	then
		wget --user $user --password $passwd -O $sqlfile "$dumpsite"
	fi
fi

# Create an archive which contains the current snapshot.
tar -czf "$backupdir/$name-$(date +%y%m%d).tar.gz" -C "$backupdir" "$name"

# Mark the current execution of the backup.
touch "$current/performed"
