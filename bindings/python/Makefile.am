# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2022 Bartosz Golaszewski <brgl@bgdev.pl>

EXTRA_DIST = \
	MANIFEST.in \
	setup.py

if WITH_TESTS

python-tests:
	GPIOD_WITH_TESTS=1 \
	CFLAGS="-I$(abs_top_srcdir)/include/ -I$(abs_top_srcdir)/tests/gpiosim/ \
	-L$(abs_top_builddir)/lib/.libs/ -L$(abs_top_srcdir)/tests/gpiosim/.libs/" \
	$(PYTHON) -m pip install --prefix=/var/tmp --no-build-isolation --editable .

endif

all-local: python-tests
	GPIOD_WITH_TESTS= \
	CFLAGS="-I$(abs_top_srcdir)/include/ -I$(abs_top_srcdir)/tests/gpiosim/ \
	-L$(abs_top_builddir)/lib/.libs/ -L$(abs_top_srcdir)/tests/gpiosim/.libs/" \
	$(PYTHON) -m build .

install-exec-local:
	GPIOD_WITH_TESTS= \
	$(PYTHON) setup.py install --prefix=$(DESTDIR)$(prefix)

SUBDIRS = gpiod

if WITH_TESTS

SUBDIRS += tests

endif

if WITH_EXAMPLES

SUBDIRS += examples

endif
