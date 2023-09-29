# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2022 Bartosz Golaszewski <brgl@bgdev.pl>

from os import environ, path
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as orig_build_ext
from shutil import rmtree


class build_ext(orig_build_ext):
    """
    setuptools install all C extentions even if they're excluded in setup().
    As a workaround - remove the tests directory right after all extensions
    were built (and possibly copied to the source directory if inplace is set).
    """

    def run(self):
        super().run()
        rmtree(path.join(self.build_lib, "tests"), ignore_errors=True)


with open("gpiod/version.py", "r") as fd:
    exec(fd.read())


sources = [
    # gpiod Python bindings
    "gpiod/ext/chip.c",
    "gpiod/ext/common.c",
    "gpiod/ext/line-config.c",
    "gpiod/ext/line-settings.c",
    "gpiod/ext/module.c",
    "gpiod/ext/request.c",
]

if "USE_SYSTEM_GPIOD" in environ and environ["USE_SYSTEM_GPIOD"] == "1":
    libraries = ["gpiod"]
    include_dirs = ["gpiod"]
else:
    sources += [
        # gpiod library
        "lib/chip.c",
        "lib/chip-info.c",
        "lib/edge-event.c",
        "lib/info-event.c",
        "lib/internal.c",
        "lib/line-config.c",
        "lib/line-info.c",
        "lib/line-request.c",
        "lib/line-settings.c",
        "lib/misc.c",
        "lib/request-config.c",
    ]
    libraries = []
    include_dirs = ["include", "lib", "gpiod/ext"]


gpiod_ext = Extension(
    "gpiod._ext",
    libraries=libraries,
    sources=sources,
    define_macros=[("_GNU_SOURCE", "1")],
    include_dirs=include_dirs,
    extra_compile_args=[
        "-Wall",
        "-Wextra",
        '-DGPIOD_VERSION_STR="{}"'.format(__version__),
    ],
)

gpiosim_ext = Extension(
    "tests.gpiosim._ext",
    sources=["tests/gpiosim/ext.c"],
    define_macros=[("_GNU_SOURCE", "1")],
    libraries=["gpiosim"],
    extra_compile_args=["-Wall", "-Wextra"],
)

procname_ext = Extension(
    "tests.procname._ext",
    sources=["tests/procname/ext.c"],
    define_macros=[("_GNU_SOURCE", "1")],
    extra_compile_args=["-Wall", "-Wextra"],
)

extensions = [gpiod_ext]
if "GPIOD_WITH_TESTS" in environ and environ["GPIOD_WITH_TESTS"] == "1":
    extensions.append(gpiosim_ext)
    extensions.append(procname_ext)

setup(
    name="libgpiod",
    packages=find_packages(exclude=["tests", "tests.*"]),
    ext_modules=extensions,
    cmdclass={"build_ext": build_ext},
    version=__version__,
    author="Bartosz Golaszewski",
    author_email="brgl@bgdev.pl",
    description="Python bindings for libgpiod",
    long_description="This is a package spun out of the main libgpiod repository containing " \
                     "python bindings to the underlying C library.",
    platforms=["linux"],
    license="LGPLv2.1",
)
