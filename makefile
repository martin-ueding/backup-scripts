# Copyright (c) 2012 Martin Ueding <dev@martin-ueding.de>

pythonfiles:=backup-external backup-status backup-webservers

epydoc: $(pythonfiles)
	epydoc -v $^

.PHONY: clean
clean:
	$(RM) *.pyc
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r html
	$(RM) backup-externalc
	$(RM) backup-statusc
	$(RM) backup-webserversc
