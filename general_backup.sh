#!/bin/bash
# Copyright (c) 2011 Martin Ueding <dev@martin-ueding.de>

set -e
set -u

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

cleanup() {
	# Release the mounted FTP
	if [[ -d "$tempdir" ]]
	then
		fusermount -u "$tempdir"
		rmdir -- "$tempdir"
	fi
}

trap cleanup EXIT
trap cleanup ERR

# Create a current folder if it does not exist yet.
current="$backupdir/$name"
if [[ ! -d "$current" ]]
then
	mkdir -p -- "$current"
fi

# write everything to a log file
exec > "$backupdir/$name.log" 2>&1

# Test whether this needs to be backuped already
if [[ -f "$current/performed" ]]
then
	if [[ $(( $(date +%s) - $(stat -c %Y "$current/performed") )) -lt $(( 3600 * 24 * 3)) ]]
	then
		exit 0
	fi
fi

# Create a mountpoint for the FTP.
tempdir=$(mktemp -d)
chgrp fuse -- "$tempdir"
chmod 700 -- "$tempdir"

# Mount the FTP
curlftpfs "$server" "$tempdir"

# Copy all the new data into the current directory
rsync -avE --delete -- "$tempdir/$subfolder" "$current"

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
destdir="$backupdir/$(date +%y%m)"
if [[ ! -d "$destdir" ]]
then
	mkdir -p -- "$destdir"
fi
tar -czf "$destdir/$name-$(date +%y%m%d).tar.gz" -C "$backupdir" "$name"

# Mark the current execution of the backup.
touch "$current/performed"

echo "Backup $name is done."
