# Copyright © 2012-2014 Martin Ueding <dev@martin-ueding.de>

pythonfiles := backup-external backup-status

all:

install:
	install -d "$(DESTDIR)/usr/bin"
	install android-sync -t "$(DESTDIR)/usr/bin"
	install backup-chaos -t "$(DESTDIR)/usr/bin"
	install backup-external -t "$(DESTDIR)/usr/bin"
	install backup-status -t "$(DESTDIR)/usr/bin"
	install backup-webserver -t "$(DESTDIR)/usr/bin"
	install backup-webservers -t "$(DESTDIR)/usr/bin"

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
