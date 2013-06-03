# Copyright © 2012-2013 Martin Ueding <dev@martin-ueding.de>

pythonfiles := backup-external backup-status

all:

install:
	./setup.py install --install-layout deb --root "$(DESTDIR)"

html: $(pythonfiles)
	epydoc -v $^

.PHONY: clean
clean:
	$(RM) *.pyc
	$(RM) -r build
	$(RM) -r dist
	$(RM) -r html
	$(RM) backup-externalc
	$(RM) backup-statusc
