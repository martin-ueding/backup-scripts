# Copyright (c) 2012 Martin Ueding <dev@martin-ueding.de>

pythonfiles:=$(wildcard *.py) backup-external backup-status backup-webservers

epydoc: $(pythonfiles)
	epydoc -v $^

.PHONY: clean
clean:
	$(RM) *.pyc
	$(RM) -r html
	$(RM) backup-externalc
	$(RM) backup-statusc
