BIN=/opt/dims/bin
USER:= $(shell whoami)
REV:= $(shell if [ -f VERSION ]; then cat VERSION; else git describe; fi)
UID:= $(id -u)
PYTHONPATH:=..
PACKAGENAME:=prisem-rpc
PYTHON:=$(shell which python)
SERVER:=rabbit.devops.local
DATA=$(GIT)/dims-sample-data

# To force queue base names to include username, uncomment next line.
#QUEUEALT:=_$(USER)

QUEUEALT:=
# To force queue base names to include "_dev", uncomment next line.
#QUEUEALT:=_dev
#QUEUEALT:=_test

#HELP release - package and upload a release"
.PHONY: release
#release: sdist bdist_wheel
release: clean sdist
	cp $(shell echo dist/$(PACKAGENAME)-*.tar.gz|head -n1) /vm/cache/sources/
	ansible -i $(GIT)/private-develop/inventory/ \
		-m copy -a "src=$(shell echo dist/$(PACKAGENAME)-*.tar.gz|head -n1) dest=/opt/dims/src" orange.devops.develop

#HELP bdist_egg - build an egg package
.PHONY: bdist_egg
bdist_egg:
	python setup.py bdist_egg
	ls -l dist/*.egg

#HELP bdist_wheel - build a wheel package
.PHONY: bdist_wheel
bdist_wheel:
	python setup.py bdist_wheel
	ls -l dist/*.whl

#HELP sdist - build a source package
.PHONY: sdist
sdist:
	python setup.py sdist
	ls -l dist/*.tar.gz

#HELP artifact - build a source package artifact in directory "output"
.PHONY: artifact
artifact: sdist
	[ -d output ] || mkdir output
	cp $(shell ls -t dist/*.tar.gz|head -n 1) output
	(cd output && for F in *; do sha256sum $$F > $$F.sha256sum; done)

DEBUG:=
# To add debugging output, uncomment next line.
#DEBUG:=--debug

VERBOSE:=
# To be verbose, uncomment
#VERBOSE:=--verbose

BANNER:==============================================================


.PHONY: help dohelp clean usage testusage dotestusage examples \
	start-anon restart-anon stop-anon status-anon test testa1 testa2 testa3 testa4 \
	start-rwfind stop-rwfind status-rwfind testrw1 testrw2 testrw3 testrw4 testrw5 testrw6 testrw7 \
	testusage \
	start-cif stop-cif status-cif restart-cif testcif1 \
	start-crosscor stop-crosscor status-crosscor restart-crosscor testcc1 testcc2 testcc3 \
	testlm1 testlm2 testlm3 testlm4 \
	install logs version \
	map50 map65 map95

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

#HELP logs - watch logs from RPC services in realtime
logs:
	$(PYTHON) logmon --server $(SERVER)

#HELP example - show some examples in more detail
example:
	@less EXAMPLE.txt

#HELP clean - clean up temp files
clean:
	-$(MAKE) stop-anon stop-rwfind stop-cifbulk stop-crosscor
	-(cd docs; make clean)
	-find . -name '*.pyc' -exec rm -f {} ';'
	-rm -rf dist build MANIFEST *.egg-info
	-rm -f *.log *.{orig,rej}
	-rm -f *-lastrequest.txt *-lastresponse.txt
	-rm -f malware*.txt ips*.txt map*.txt test*.txt
	-rm -rf output

#HELP
#HELP C designates use of "canned" data
#HELP L designates use of "live" data
#HELP

#HELP map95 - Produce a map file of 95% confidence infrastructure/malware info (L)
map95: map95.txt ips95.txt

ips95.txt: malware95.txt
	@echo $(BANNER)
	@echo "[+] Using 'ipgrep' to extract a list of malware IP addresses from malware95.txt:"
	@echo ""
	ipgrep -v -l malware95.txt | grep "^[0-9]" > ips95.txt
	@echo $(BANNER)
	@echo "[+] Extracted `wc -l < ips95.txt` IP addresses that look like this:"
	@head -n 5 ips95.txt
	@echo "..."
	@echo ""

map95.txt: malware95.txt
	@echo $(BANNER)
	@echo "[+] Generating an 95\% confidence  map file for anonymization/statistics"
	@echo ""
	cut -s -d '|' -f 9,10 malware95.txt |\
		grep -v "prefix" |\
		grep "^[0-9]" |\
		awk -F\| '{gsub(/[ ]*/,"",$$2); \
			split($$1,a," "); \
			printf "%s|%s_%s|%s_%s\n",  $$2,a[1],a[2],a[1],a[2];}' |\
		sed 's/ *//g' > map95.txt
	@head -n 5 map95.txt
	@echo ""

malware95.txt:
	@echo $(BANNER)
	@echo "[+] Pulling a feed of malware (confidence >= 95) infrastructure indicators from CIF..."
	@echo ""
	cif -s medium -c 95 -n -q infrastructure/malware > malware95.txt
	@echo $(BANNER)
	@echo "[+] Found `wc -l malware95.txt` records in CIF that look like this:"
	@head -n 15 malware95.txt
	@echo ""

#HELP map65 - Produce a map file (map65.txt) for demonstrating anonymization (L)
map65: map65.txt ips65.txt

ips65.txt: malware65.txt
	@echo $(BANNER)
	@echo "[+] Using 'ipgrep' to extract a list of malware IP addresses from malware65.txt:"
	@echo ""
	ipgrep -v -l malware65.txt | grep "^[0-9]" > ips65.txt
	@echo $(BANNER)
	@echo "[+] Extracted `wc -l < ips65.txt` IP addresses that look like this:"
	@head -n 5 ips65.txt
	@echo "..."
	@echo ""

malware65.txt:
	@echo $(BANNER)
	@echo "[+] Pulling a feed of malware (confidence >= 65) infrastructure indicators from CIF..."
	@echo ""
	cif -s medium -c 65 -n -q infrastructure/malware > malware65.txt
	@echo $(BANNER)
	@echo "[+] Found `wc -l < malware65.txt` records in CIF that look like this:"
	@head -n 15 malware65.txt
	@echo ""

map65.txt: malware65.txt
	@echo $(BANNER)
	@echo "[+] Generating a map file for anonymization/statistics"
	@echo ""
	cut -s -d '|' -f 10,11,12 malware65.txt |\
		grep -v "prefix" |\
		grep "^[0-9]" |\
		awk -F\| '{printf "%s|%s_%s|%s_%s\n",  $$1,$$2,$$3,$$2,$$3;}' |\
		sed 's/ *//g' > map65.txt
	@head -n 5 map65.txt
	@echo ""

#HELP map50 - Produce a large map file (map50.txt) for demonstrating anonymization (L)
map50: map50.txt

ips50.txt: malware50.txt
	@echo $(BANNER)
	@echo "[+] Using 'ipgrep' to extract a list of malware IP addresses from malware50.txt:"
	@echo ""
	ipgrep -v -l malware50.txt | grep "^[0-9]" > ips50.txt
	@echo $(BANNER)
	@echo "[+] Extracted `wc -l ips50.txt` IP addresses that look like this:"
	@head -n 5 ips50.txt
	@echo "..."
	@echo ""

malware50.txt:
	@echo $(BANNER)
	@echo "[+] Pulling a feed of malware (confidence >= 50) infrastructure indicators from CIF..."
	@echo ""
	cif -s medium -c 50 -n -q infrastructure/malware > malware50.txt
	@echo $(BANNER)
	@echo "[+] Found `wc -l malware50.txt` records in CIF that look like this:"
	@head -n 15 malware50.txt
	@echo ""

map50.txt: malware50.txt
	@echo $(BANNER)
	@echo "[+] Generating a map file for anonymization/statistics"
	@echo ""
	@cut -s -d '|' -f 10,11,12 malware50.txt |\
	       	grep -v "prefix" |\
	       	grep "^[0-9]" |\
	       	awk -F\| '{printf "%s|%s_%s|%s_%s\n",  $$1,$$2,$$3,$$2,$$3;}' |\
	       	sed 's/ *//g' > map50.txt
	@head -n 5 map50.txt
	@echo ""


#HELP

test:
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(MAPFILE) \
		--file $(DATA)/rwfind_201210011617_8428.txt

#HELP testa1 - Demonstrate anonymization/statistics for a PRISEM rwfind report (smaller report)
testa1:
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(MAPFILE) \
		--file $(DATA)/rwfind_201210011617_8428.txt > test.txt
	wc -c test.txt
	sha1sum test.txt
	@cat test.txt

testa1j:
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--json \
		--stats \
		--map $(MAPFILE) \
		--file $(DATA)/rwfind_201210011617_8428.txt > test.txt
	wc -c test.txt
	sha1sum test.txt
	@$(PYTHON) -mjson.tool test.txt

#HELP testa2 - Demonstrate anonymization/statistics for a PRISEM rwfind report (longer report) (C)
testa2:
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(MAPFILE) \
		--file $(DATA)/rwfind_201302210110_18463.txt > test.txt
	wc -c test.txt
	sha1sum test.txt
	@cat test.txt

#HELP testa3 - Demonstrate anonymization of CIF data to show cross-organizational correlation capabilities (L)
testa3: map65.txt ips65.txt
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map map65.txt \
		--file ips65.txt > test.txt
	wc -c test.txt
	sha1sum test.txt
	@cat test.txt

#HELP testa4 - Demonstrate anonymization of CIF data with JSON output. (L)
testa4: map65.txt ips65.txt
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--json \
		--map map65.txt \
		--file ips65.txt > testa4.txt
	wc -c testa4.txt
	sha1sum testa4.txt
	@cat testa4.txt

#HELP testafail - Demonstrate failure message.
testafail:
	cp /dev/null ips65.txt
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map map65.txt \
		--file ips65.txt > test.txt
	wc -c test.txt
	sha1sum test.txt
	@cat test.txt

#HELP

#HELP testrw1 - Demonstrate searching City of Seattle netflow data (L)
testrw1: testrw1.txt
testrw1.txt: map65 ips65.txt
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for flows to/from suspect IPs over last 3 days."
	@echo ""
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--days 3 \
		--searchfile ips65.txt > testrw1.txt
	@echo "[+] Found the following flows:"
	@cat testrw1.txt
	@echo ""

#HELP testrw2 - Demonstrate searching City of Seattle netflow data, then anonymizing w/stats (L)
testrw2: map65.txt ips65.txt testrw1.txt 
	@echo $(BANNER)
	@echo "[+] Anonymizing and generating statistics for suspect IPs"
	@echo ""
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
	       	--stats \
		--map map65.txt \
		--file testrw1.txt >  testrw2-a.txt
	@echo "[+] Results:"
	@cat testrw2-a.txt
	@echo ""
	@echo $(BANNER)
	@echo "[+] Anonymizing and generating statistics for PRISEM related IPs"
	@echo ""
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(MAPFILE) \
		--file testrw2-a.txt > testrw2-b.txt
	@echo "[+] Results:"
	@echo ""
	@cat testrw2-b.txt
	@echo ""

#HELP testrw3 - Search City of Seattle netflow data for CIF 95% confidence indicators (L)
testrw3: testrw3.txt
testrw3.txt: map95
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for flows to/from suspect IPs over last 1 day."
	@echo ""
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--days 1 \
		--searchfile ips95.txt > testrw3.txt
	@echo "[+] Found the following flows:"
	@cat testrw3.txt
	@echo ""

#HELP testrw4 - Search City of Seattle netflow data, then anonymize w/stats (L)
testrw4: map95 testrw3.txt
	@echo $(BANNER)
	@echo "[+] Sending report to Floyd for anonymization+stats of suspect IPs"
	@echo ""
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map map95.txt \
		--file testrw3.txt > testrw3-a.txt
	@cat testrw3-a.txt
	@echo ""
	@echo $(BANNER)
	@echo "[+] Sending report to Floyd for anonymization+stats of PRISEM related IPs"
	@echo ""
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(MAPFILE) \
		--file testrw3-a.txt > testrw3-b.txt
	@echo ""
	@echo $(BANNER)
	@cat testrw3-b.txt
	@echo ""

#HELP testrw5 - Search City of Seattle netflow data for suspicious IPs over last 7 days (C)
testrw5:
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for flows to/from suspect IPs over last 7 days."
	@echo ""
	@echo 192.168.1.0/24 > ips.txt
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--stime $(shell date -d '-7 days' +%s) \
		--etime $(shell date +%s) \
		--searchfile ips.txt > testrw5.txt
	@echo "[+] Found the following flows:"
	@cat testrw5.txt
	@echo ""

#HELP testrw6 - Search City of Seattle netflow data for suspect IP on a specific day (C)
testrw6:
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for some suspicious IPs."
	@echo ""
	@echo 89.248.172.58 > ips.txt
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--json \
		--start-date "2014/01/03:00" \
		--end-date "2014/01/04:00" \
		--searchfile ips.txt > testrw6.txt
	@echo "[+] Found the following flows:"
	@cat testrw6.txt
	@echo ""

#HELP testrw7 - Search City of Seattle netflow data for another suspect CIDR block for one month (C)
testrw7:
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for suspicious CIDR block."
	@echo ""
	@echo 61.147.103.0/24 > ips.txt
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--start-date "2013/10/15:00" \
		--end-date "2013/11/15:00" \
		--searchfile ips.txt > testrw7.txt
	@echo "[+] Found the following flows:"
	@cat testrw7.txt
	@ipgrep -s testrw7.txt
	@echo ""

#HELP testrw8 - Same as testrw7, but output JSON (C)
testrw8:
	@echo $(BANNER)
	@echo "[+] Searching on Pink.seattle.gov for suspicious CIDR block."
	@echo ""
	@echo 61.147.103.0/24 > ips.txt
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--json \
		--topn 100 \
		--start-date "2013/10/15:00" \
		--end-date "2013/11/15:00" \
		--searchfile ips.txt > testrw8.txt
	@echo "[+] Found the following flows:"
	@cat testrw8.txt
	@ipgrep -s testrw8.txt
	@echo ""

#HELP testrw9 - Similar to testrw3, but for 2014/03/07 (C)
testrw9:
	@echo $(BANNER)
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--json \
		--topn 100 \
		--start-date "2014/03/07:00" \
		--end-date "2014/03/08:00" \
		--searchfile $(DATA)/ips95-20140308.txt > testrw9a.txt
	$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--stats \
		--map $(DATA)/map95-20140308.txt \
		--file testrw9a.txt > testrw9.txt
	@echo "[+] Found the following flows:"
	@cat testrw9.txt
	@ipgrep -s testrw9.txt
	@echo ""


#HELP testrwfail - Test failure mode (no search file)
testrwfail:
	@echo $(BANNER)
	@echo "[+] Attempting to search for nothing."
	@echo ""
	cp /dev/null ips.txt
	$(PYTHON) rwfind_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base rwfind$(QUEUEALT) \
		--topn 100 \
		--json \
		--start-date "2014/01/01:00" \
		--end-date "2014/01/08:00" \
		--searchfile ips.txt
	@echo ""

#HELP

ips65-subset.txt: ips65.txt
	@grep '\.[12345][56789]\.[2468]' ips65.txt > ips65-subset.txt

#HELP testlm1 - Search Log Matrix subset of records for CIF 65% confidence indicators, last 1 day (L)
testlm1: ips65-subset.txt
	@echo $(BANNER)
	@echo ""
	@echo "[+] Searching Log Matrix for `wc -l < ips65-subset.txt` records associated with suspect IPs over last 1 day."
	$(PYTHON) lmsearch_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base lmsearch$(QUEUEALT) \
		--days 1 \
		--searchfile ips65-subset.txt > testlm1.txt
	@echo "[+] Found log records that look like:"
	@$(PYTHON) -mjson.tool < testlm1.txt > testlm1-pp.txt
	@head -n 20 testlm1-pp.txt
	@echo ""

#HELP testlm2 - Search Log Matrix records for CIF 65% confidence indicators, last 7 days (L)
testlm2: ips65.txt
	@echo $(BANNER)
	@echo "[+] Searching Log Matrix for records associated with suspect IPs over last 7 days."
	@echo ""
	$(PYTHON) lmsearch_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base lmsearch$(QUEUEALT) \
		--days 7 \
		--searchfile ips65.txt > testlm2.txt
	@echo "[+] Found log records that look like:"
	@$(PYTHON) -mjson.tool < testlm2.txt > testlm2-pp.txt
	@head -n 20 testlm2-pp.txt
	@echo ""

#HELP testlm3 - Search Log Matrix records for specific IPs from testrw6 (L via testrw6)
testlm3: testrw6
	@echo $(BANNER)
	@echo "[+] Searching Log Matrix for specific IPs from testrw6."
	@echo ""
	$(PYTHON) lmsearch_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base lmsearch$(QUEUEALT) \
		--start-date "2014/01/03:00" \
		--end-date "2014/01/04:00" \
		--searchfile ips.txt > testlm3.txt
	@echo "[+] Found log records that look like:"
	@$(PYTHON) -mjson.tool < testlm3.txt > testlm3-pp.txt
	@head -n 20 testlm3-pp.txt
	@echo ""

#HELP testlm4 - Search Log Matrix records for specific IPs from testrw6 (L via testrw6)
testlm4: ips95.txt
	@echo $(BANNER)
	@echo "[+] Searching Log Matrix for 95% confidence indicators from CIF over past 1 day."
	@echo ""
	$(PYTHON) lmsearch_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base lmsearch$(QUEUEALT) \
		--days 1 \
		--searchfile ips95.txt > testlm4.txt
	@echo "[+] Found log records that look like:"
	@$(PYTHON) -mjson.tool < testlm4.txt > testlm4-pp.txt
	@head -n 20 testlm4-pp.txt
	@echo ""


#HELP

#HELP testcif1 - Search for CIF 65% confidence IPs via Sphinx interface (L via CIF)
testcif1: ips65.txt
	@echo $(BANNER)
	@echo "[+] Searching CIF on Floyd (via Sphinx) for records associated with suspect IPs."
	@echo ""
	head -n 3 ips65.txt > ips.txt
	$(PYTHON) cifbulk_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base cifbulk_v1$(QUEUEALT) \
		--searchfile ips.txt > testcif1.txt
	@echo "[+] Found the following records:"
	@$(PYTHON) -mjson.tool testcif1.txt
	@echo ""

#HELP testcif2 - Search for Botnets related IPs IPs via Sphinx interface (L via /var/log/botnets.log on pink)
testcif2.txt: testcif2
testcif2:
	@if [ ! -f /var/log/botnets.log ]; then echo "Run this on pink.seattle.gov"; exit 1; fi
	@echo $(BANNER)
	@echo "[+] Extracting some recent Botnets events from /var/log/botnets.log"
	@echo ""
	egrep "Shadow|CIF|ICU2" /var/log/botnets.log | ipgrep -a | ipgrep -v -l > botnets.txt
	@echo $(BANNER)
	@echo "[+] Extracted `wc -l < botnets.txt` IP addresses that look like this:"
	@head -n 5 botnets.txt
	@echo "..."
	$(PYTHON) cifbulk_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base cifbulk_v1$(QUEUEALT) \
		--searchfile botnets.txt > testcif2.txt
	@echo "[+] Found the following records:"
	@$(PYTHON) -mjson.tool testcif2.txt
	@echo ""

#HELP testcif3 - Search for info about APT1 IPs.
testcif3: testcc1
	@echo $(BANNER)
	@echo "[+] Searching CIF on Floyd (via Sphinx) for records associated with APT1 intrusion set."
	@echo ""
	ipgrep -v -l \
		-n $(MAPFILE) \
		testcc1.txt > testcif3a.txt

	$(PYTHON) cifbulk_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base cifbulk_v1$(QUEUEALT) \
		--searchfile testcif3a.txt > testcif3.txt
	@echo "[+] Found the following records:"
	@$(PYTHON) -mjson.tool testcif3.txt
	@echo ""

#HELP testcif4 - Search for info about APT1 IPs.
testcif4:
	@echo $(BANNER)
	@echo "[+] Searching CIF on Floyd (via Sphinx) for records associated with suspicious CIDR block (testrw7)."
	@echo ""
	@echo 61.147.103.0/24 > ips.txt
	$(PYTHON) cifbulk_client \
		$(DEBUG) \
		$(VERBOSE) \
		--server $(SERVER) \
		--queue-base cifbulk_v1$(QUEUEALT) \
		--searchfile ips.txt > testcif4.txt
	@echo "[+] Found the following records:"
	@$(PYTHON) -mjson.tool testcif4.txt
	@echo ""


#HELP

#HELP testcc1 - Demonstrate cross-organizational correlation with APT1 intrusion set (C)
testcc1:
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for netflow report."
	@echo ""
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--iff "friend" \
		--map $(MAPFILE) \
		--file $(DATA)/rwfind_201302210110_18463.txt > testcc1.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc1.txt
	@echo ""

#HELP testcc2 - Do cross-organizational correlation against CIF 65% (L via CIF)
testcc2: testa3
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for netflow report."
	@echo ""
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--iff "foe" \
		--map map65.txt \
		--file ips65.txt > testcc2.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc2.txt
	@echo ""

#HELP testcc3 - Demonstrate cross-organizational correlation against CIF 65% (L via CIF)
testcc3:
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for netflow report."
	@echo ""
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--iff "friend" \
		--map $(MAPFILE) \
		--file $(DATA)/websense-samples.txt > testcc3.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc3.txt
	@echo ""

#HELP testcc4 - Do cross-organizational correlation against recent Botnets events (L via /var/log/botnets.log)
testcc4:
	@if [ ! -f /var/log/botnets.log ]; then echo "Run this on pink.seattle.gov"; exit 1; fi
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for recent Botnets events."
	@echo ""
	egrep "Shadow|CIF|ICU2" /var/log/botnets.log > botnets.txt
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--map $(MAPFILE) \
		--iff "friend" \
		--file botnets.txt > testcc4a.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc4a.txt
	@echo $(BANNER)
	@echo "[+] Obtaining CIF context for non-PRISEM participant IDs."
	@echo ""
	egrep UNKNOWN testcc4a.txt | ipgrep -v -l > testcc3b.txt
	$(PYTHON) cifbulk_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base cifbulk_v1$(QUEUEALT) \
		--searchfile testcc3b.txt > testcc4c.txt
	@echo "[+] Found the following records:"
	@cat testcc4c.txt

#HELP testcc5 - Do cross-organizational correlation against lmsearch data (L via testlm4)
testcc5: testlm4
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for lmsearch output (testlm4)."
	@echo ""
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--iff "friend" \
		--map $(MAPFILE) \
		--file testlm4.txt > testcc5.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc5.txt
	@echo ""

#HELP testcc6 - Do cross-organizational correlation against lmsearch data (C)
testcc6:
	@echo $(BANNER)
	@echo "[+] Obtaining cross-correlation results for lmsearch output."
	@echo ""
	$(PYTHON) crosscor_client $(DEBUG) $(VERBOSE) \
		--server $(SERVER) \
		--queue-base crosscor$(QUEUEALT) \
		--iff "friend" \
		--map $(MAPFILE) \
		--file $(DATA)/lmsearch-example-pp.txt > testcc6.txt
	@echo "[+] Cross Correlation results:"
	@cat testcc6.txt
	@echo ""

#HELP
#HELP testgraph1 - Generate network graph from suspect flows (95% confidence CIF feed, last week) (L via CIF)
testgraph1: testrw3
	@echo $(BANNER)
	@echo "[+] Generating statistics for suspect IPs"
	@echo ""
	#$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
	#	--server $(SERVER) \
	#	--queue-base anon$(QUEUEALT) \
	#       	--stats \
	#       	--json \
	#	--map map95.txt \
	#	--file testrw3.txt >  testgraph1-foe.txt
	@ipgrep -a --json -n map65.txt testrw3.txt > testgraph1-foe.txt
	@echo "[+] Results:"
	@$(PYTHON) -mjson.tool testgraph1-foe.txt | head -n 100
	@echo ""
	@echo $(BANNER)
	@echo "[+] Generating statistics for PRISEM related IPs"
	@echo ""
	#$(PYTHON) anon_client $(DEBUG) $(VERBOSE) \
	#	--server $(SERVER) \
	#	--queue-base anon$(QUEUEALT) \
	#	--stats \
	#	--json \
	#	--map $(MAPFILE) \
	#	--file testrw3.txt > testgraph1-friend.txt
	@ipgrep -a --json -n $(MAPFILE) testrw3.txt > testgraph1-friend.txt
	@echo "[+] Results:"
	@echo ""
	@$(PYTHON) -mjson.tool testgraph1-friend.txt | head -n 100


#HELP testhelp - Test --help in RPC clients/servers.
testhelp:
	@(for i in anon rwfind cifbulk crosscor lmsearch; \
		do \
			echo $(BANNER); \
			[ -f $${i}_client ] && $(PYTHON) $${i}_client --help; \
			echo ""; \
			echo $(BANNER); \
			[ -f $${i}_server ] && $(PYTHON) $${i}_server --help; \
			echo ""; \
		done) | less

#HELP testusage - Test --usage in RPC clients/servers.
testusage:
	@-$(MAKE) dotestusage 2>&1 | less -p '\[\+\+\+\]'

dotestusage:
	@echo "[+] anon usage"
	-$(PYTHON) anon_client \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--usage
	@echo "[+] rwfind usage"
	-$(PYTHON) rwfind_client \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--usage
	@echo "[+] cifbulk usage"
	-$(PYTHON) cifbulk_client \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--usage
	@echo "[+] crosscor usage"
	-$(PYTHON) crosscor_client \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--usage
	@echo "[+] lmsearch usage"
	-$(PYTHON) lmsearch_client \
		--server $(SERVER) \
		--queue-base anon$(QUEUEALT) \
		--usage

#HELP
#HELP start-anon - start anon_server RPC service
start-anon:
	-bash rpcserver anon_server start anon$(QUEUEALT) $(DEBUG)

#HELP restart-anon - restart anon_server RPC service
restart-anon: stop-anon start-anon

#HELP status-anon - show status of anon_server RPC service
status-anon:
	-bash rpcserver anon_server status

#HELP stop-anon - stop anon_server RPC service
stop-anon:
	-bash rpcserver anon_server stop

#HELP start-rwfind - start rwfind_server RPC service
start-rwfind:
	-bash rpcserver rwfind_server start rwfind$(QUEUEALT) $(DEBUG)

#HELP start-rwfind - show status of rwfind_server RPC service
status-rwfind:
	-bash rpcserver rwfind_server status

#HELP stop-rwfind - stop rwfind_server RPC service
stop-rwfind:
	-bash rpcserver rwfind_server stop

#HELP restart-rwfind - restart rwfind_server RPC service
restart-rwfind: stop-rwfind start-rwfind

#HELP start-cifbulk - start cifbulk_server RPC service
start-cifbulk:
	-bash rpcserver cifbulk_server start cifbulk_v1$(QUEUEALT) $(DEBUG)

#HELP start-cifbulk - show status of cifbulk_server RPC service
status-cifbulk:
	-bash rpcserver cifbulk_server status

#HELP stop-cifbulk - stop cifbulk_server RPC service
stop-cifbulk:
	-bash rpcserver cifbulk_server stop

#HELP restart-cifbulk - restart cifbulk_server RPC service
restart-cifbulk: stop-cifbulk start-cifbulk

#HELP start-crosscor - start crosscor_server RPC service
start-crosscor:
	-bash rpcserver crosscor_server start crosscor$(QUEUEALT) $(DEBUG)

#HELP start-crosscor - show status of crosscor_server RPC service
status-crosscor:
	-bash rpcserver crosscor_server status

#HELP stop-crosscor - stop crosscor_server RPC service
stop-crosscor:
	-bash rpcserver crosscor_server stop

#HELP restart-crosscor - restart crosscor_server RPC service
restart-crosscor: stop-crosscor start-crosscor


#HELP install - install scripts (into virtual environment)
install:
	pip install -e .

#HELP uninstall - uninstall scripts (from virtual environment)
uninstall:
	rm $(BIN)/crosscor
	pip uninstall
