.DEFAULT_GOAL := help

ARC_V := $(shell cat findlibs.py | grep 'VERSION' | sed -e 's/.*=//g' -e 's/[" ]//g')
ARC_N := cross-toolchain-${ARC_V}
DST := ./target

help:
	@printf 'Available commands:\n'
	@printf '\ttar    - make source tarfile for packaging and distribution\n'
	@printf '\tbuild  - run helper and build the toolchain in the current directory\n'
	@printf '\tclean  - cleanup everything\n'

tar:
	rm -rf package/${ARC_N}
	mkdir -p package/${ARC_N}
	for f in LICENSE Makefile README.md findlibs.py; do \
		cp $$f package/${ARC_N} ; \
	done
	tar -C package -czvf package/${ARC_N}.tar.gz ${ARC_N}
	rm -rf package/${ARC_N}

build:
	@printf 'Building...\n'
	mkdir ${DST}

clean:
	@printf 'Cleaning...\n'
	rm -rf ${DST}
	rm -rf package
