PYTHON ?= python3
PYLINT_DIRS = sfxbridge/ tests/

all: test rpm

test: pylint unittest flake8

reformat:
	isort-3 --recursive $(PYLINT_DIRS)
	yapf --recursive --in-place $(PYLINT_DIRS)

.PHONY: unittest
unittest:
	$(PYTHON) -m pytest -vv tests/

.PHONY: pylint
pylint:
	$(PYTHON) -m pylint --rcfile .pylintrc $(PYLINT_DIRS)

.PHONY: flake8
flake8:
	$(PYTHON) -m flake8 --max-line-length=125 $(PYLINT_DIRS)

.PHONY: coverage
coverage:
	$(PYTHON) -m pytest $(PYTEST_ARG) --cov-report term-missing --cov sfxbridge test/

.PHONY: clean
clean:
	$(RM) -r *.egg-info/ build/ dist/
	$(RM) ../sfxbridge_* test-*.xml
	$(RM) -r rpm
	$(RM) -r __pycache__

.PHONY: rpm
rpm:
	git archive --output=sfxbridge-rpm-src.tar.gz --prefix=sfxbridge/ HEAD
	rpmbuild -bb sfxbridge.spec \
		--define '_sourcedir $(shell pwd)' \
                --define '_topdir $(shell pwd)/rpm' \
		--define 'major_version $(shell git describe --tags --abbrev=0 | cut -f1-)' \
		--define 'minor_version $(subst -,.,$(shell git describe --tags --long | cut -f2- -d-))'
	$(RM) sfxbridge-rpm-src.tar.gz

.PHONY: build-dep-fedora
build-dep-fedora:
	sudo dnf -y --best --allowerasing install \
		python3-flake8 python3-pytest python3-pylint \
		python3-aiohttp systemd-python3

