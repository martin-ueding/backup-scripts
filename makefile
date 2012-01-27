# Copyright (c) 2012 Martin Ueding <dev@martin-ueding.de>

pythonfiles:=$(wildcard *.py) backup-external backup-status

epydoc: $(pythonfiles)
	epydoc -v $^

.PHONY: clean
clean:
	$(RM) *.pyc
	$(RM) -f html
