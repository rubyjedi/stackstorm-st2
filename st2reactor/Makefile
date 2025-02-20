# <<<< TO DEPRICATE
SHELL := /bin/bash
RPM_ROOT=~/rpmbuild
RPM_SOURCES_DIR := $(RPM_ROOT)/SOURCES/
RPM_SPECS_DIR := $(RPM_ROOT)/SPECS/
VER=0.4.0
COMPONENTS := st2reactor

.PHONY: rpm
rpm:
	pushd ~ && rpmdev-setuptree && popd
	tar --transform=s~^~$(COMPONENTS)-$(VER)/~ -czf $(RPM_SOURCES_DIR)/$(COMPONENTS).tar.gz bin conf $(COMPONENTS)
	cp packaging/rpm/$(COMPONENTS).spec $(RPM_SPECS_DIR)/
	cd $(RPM_SPECS_DIR) && rpmbuild --clean --rmsource -ba $(COMPONENTS).spec

.PHONY: deb
deb:
	mkdir -p ~/debbuild
	tar --transform=s~^~$(COMPONENTS)-$(VER)/~ -czf ~/$(COMPONENTS).tar.gz bin conf $(COMPONENTS) packaging/debian
	pushd ~ && tar -xzf $(COMPONENTS).tar.gz && cd $(COMPONENTS)-$(VER) && cp -Rf packaging/debian ./ && dpkg-buildpackage -us -uc -b && popd
	cp -f ~/$(COMPONENT)*.deb ~/debbuild/
# >>>>

WHEELDIR ?= /tmp/wheelhouse
ST2_COMPONENT := $(notdir $(CURDIR))
ST2PKG_RELEASE ?= 1
ST2PKG_VERSION ?= $(shell python -Wd -Werror -c "from $(ST2_COMPONENT) import __version__; print __version__,")

ifneq (,$(wildcard /etc/debian_version))
	DEBIAN := 1
	DESTDIR ?= $(CURDIR)/debian/$(ST2_COMPONENT)
else
	REDHAT := 1
endif

.PHONY: all install wheelhouse
all: install

install: wheelhouse injectdeps changelog

post_install: bdist_wheel
	# post_install is triggered debian/rules file, don't call it from install target!
	# We don't want anything like below to be postinst
	sed -i -r "/args\s*=\s*/s%logs%/var/log/st2%g" $(DESTDIR)/etc/st2/logging.*conf

populate_version: .stamp-populate_version
.stamp-populate_version:
	# populate version should be run before any pip/setup.py works
	sh ../scripts/populate-version.sh
	touch $@

requirements:
	python ../scripts/fixate-requirements.py -s in-requirements.txt -f ../fixed-requirements.txt

changelog: populate_version
ifeq ($(DEBIAN),1)
	debchange -v $(ST2PKG_VERSION)-$(ST2PKG_RELEASE) -M "automated build version: $(ST2PKG_VERSION)"
endif

wheelhouse: .stamp-wheelhouse
.stamp-wheelhouse: populate_version requirements
	# Install wheels into shared location
	pip wheel --wheel-dir=$(WHEELDIR) -r requirements.txt
	touch $@

injectdeps: .stamp-injectdeps
.stamp-injectdeps:
	# We can modify requirements ONLY AFTER wheelhouse has been built
	@echo "st2common" >> requirements.txt
	touch $@

bdist_wheel: .stamp-bdist_wheel
.stamp-bdist_wheel: populate_version
	python setup.py bdist_wheel -d $(WHEELDIR)
	touch $@
