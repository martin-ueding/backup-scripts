# Copyright © 2012-2013 Martin Ueding <dev@martin-ueding.de>

pythonfiles := backup-external backup-status

all:
	@echo "Nothing to do."

install:
	python setup.py install --install-layout deb --root "$(DESTDIR)"

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
