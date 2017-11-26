BIN=/opt/dims/bin
USER:= $(shell whoami)
REV=$(shell git describe)
UID:= $(id -u)
PYTHONPATH:=..
PYTHON:=/opt/local/bin/python

DEBUG:=
# To add debugging output, uncomment next line.
#DEBUG:=--debug

VERBOSE:=
# To be verbose, uncomment
#VERBOSE:=--verbose

MAPFILE:=prisem.yml

BANNER:==============================================================



.PHONY: help dohelp clean usage test dotestusage examples install

#HELP help - this help text
help:
	@-$(MAKE) dohelp 2>/dev/null | less

dohelp:
	@echo "usage: make [something]"
	@echo ""
	@echo "Where 'something' is one of:"
	@echo ""
	@grep "^#HELP" Makefile | sed 's/#HELP//'
	@echo ""
	@echo "For more on using these scripts, try 'make usage or 'make example'."
	@echo ""
	@echo ""

#HELP usage - show how to use these scripts
usage:
	@cat USAGE.txt

#HELP clean - clean up temp files
clean:
	-$(MAKE) stop-anon stop-rwfind stop-cifbulk stop-yamltest
	-find .. -name '*.pyc' -exec rm -f {} ';'
	-rm -rf dist build MANIFEST
	-rm -f *.log *.{orig,rej}
	-rm -f *-lastrequest.txt *-lastresponse.txt
	-rm -f malware*.txt ips*.txt map*.txt test*.txt

#HELP

#HELP test - test

test:
	$(PYTHON) yamltest prisem.yml


install: $(BIN)/yamltest

$(BIN)/yamltest: yamltest
	sed "s/@@REV@@/$(REV)/" < $< > $@
	chmod +x $@

