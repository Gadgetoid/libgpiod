# SPDX-License-Identifier: GPL-2.0-or-later
# SPDX-FileCopyrightText: 2022 Bartosz Golaszewski <brgl@bgdev.pl>

from os import environ, path, unlink
from setuptools import setup, Extension, find_packages
from setuptools.command.build_ext import build_ext as orig_build_ext
from setuptools.command.sdist import sdist as orig_sdist
from shutil import rmtree, copytree


def get_gpiod_version_str():
    try:
        return environ["GPIOD_VERSION_STR"]
    except KeyError:
        pass
    try:
        return open("gpiod-version-str.txt", "r").read()
    except OSError:
        return None


def copy_libgpiod_files(func):
    """
    In order to include the lib and include directories in the sdist
    we must temporarily copy them up into the python bindings directory.

    If "./lib" exists we are building from an sdist package and will not
    try to copy the files again.
    """

    def wrapper(self):
        copy_src = not path.exists("./lib")
        if copy_src:
            gpiod_version_str = get_gpiod_version_str()
            if gpiod_version_str is not None:
                open("gpiod-version-str.txt", "w").write(gpiod_version_str)
            copytree("../../lib", "./lib")
            copytree("../../include", "./include")
        func(self)
        if copy_src:
            if gpiod_version_str is not None:
                unlink("gpiod-version-str.txt")
            rmtree("./lib")
            rmtree("./include")

    return wrapper


class build_ext(orig_build_ext):
    """
    setuptools install all C extentions even if they're excluded in setup().
    As a workaround - remove the tests directory right after all extensions
    were built (and possibly copied to the source directory if inplace is set).
    """

    @copy_libgpiod_files
    def run(self):
        super().run()
        rmtree(path.join(self.build_lib, "tests"), ignore_errors=True)


class sdist(orig_sdist):
    """
    Wrap sdist so that we can copy the lib and include files into . where
    MANIFEST.in will include them in the source package.
    """

    @copy_libgpiod_files
    def run(self):
        super().run()


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

extra_compile_args = [
    "-Wall",
    "-Wextra",
]

libraries = ["gpiod"]
include_dirs = ["gpiod"]

if environ.get("LINK_SYSTEM_LIBGPIOD") == "1":
    print("linking system libgpiod (requested by LINK_SYSTEM_LIBGPIOD)")
elif get_gpiod_version_str() is None:
    print("warning: linking system libgpiod (GPIOD_VERSION_STR not specified)")
else:
    print("vendoring libgpiod into standalone library")
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
    extra_compile_args += [
        '-DGPIOD_VERSION_STR="{}"'.format(get_gpiod_version_str()),
    ]


gpiod_ext = Extension(
    "gpiod._ext",
    libraries=libraries,
    sources=sources,
    define_macros=[("_GNU_SOURCE", "1")],
    include_dirs=include_dirs,
    extra_compile_args=extra_compile_args,
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
if environ.get("GPIOD_WITH_TESTS") == "1":
    extensions.append(gpiosim_ext)
    extensions.append(procname_ext)

setup(
    name="libgpiod",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.9.0",
    ext_modules=extensions,
    cmdclass={"build_ext": build_ext, "sdist": sdist},
    version=__version__,
    author="Bartosz Golaszewski",
    author_email="brgl@bgdev.pl",
    description="Python bindings for libgpiod",
    long_description="This is a package spun out of the main libgpiod repository containing " \
                     "python bindings to the underlying C library.",
    platforms=["linux"],
    license="LGPLv2.1",
)
