from conan.tools.build import check_min_cppstd
from conan.tools.microsoft import is_msvc, is_msvc_static_runtime
from conan import ConanFile, Version
from conan.tools import files
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeDeps, CMakeToolchain, cmake_layout
import functools
import os

required_conan_version = ">=1.53.0"


class OpenImageIOConan(ConanFile):
    name = "openimageio"
    description = (
        "OpenImageIO is a library for reading and writing images, and a bunch "
        "of related classes, utilities, and applications. There is a "
        "particular emphasis on formats and functionality used in "
        "professional, large-scale animation and visual effects work for film."
    )
    topics = ("vfx", "image", "picture")
    license = "BSD-3-Clause"
    homepage = "http://www.openimageio.org/"
    url = "https://github.com/conan-io/conan-center-index"

    settings = "os", "arch", "compiler", "build_type"
    options = {
        "shared": [True, False],
        "fPIC": [True, False],
        "with_libjpeg": ["libjpeg", "libjpeg-turbo"],
        "with_libpng": [True, False],
        "with_freetype": [True, False],
        "with_hdf5": [True, False],
        "with_opencolorio": [True, False],
        "with_opencv": [True, False],
        "with_tbb": [True, False],
        "with_dicom": [True, False],
        "with_ffmpeg": [True, False],
        "with_giflib": [True, False],
        "with_libheif": [True, False],
        "with_raw": [True, False],
        "with_openjpeg": [True, False],
        "with_openvdb": [True, False],
        "with_ptex": [True, False],
        "with_libwebp": [True, False],
    }
    default_options = {
        "shared": False,
        "fPIC": True,
        "with_libjpeg": "libjpeg",
        "with_libpng": True,
        "with_freetype": True,
        "with_hdf5": True,
        "with_opencolorio": True,
        "with_opencv": False,
        "with_tbb": False,
        "with_dicom": False,  # Heavy dependency, disabled by default
        "with_ffmpeg": True,
        "with_giflib": True,
        "with_libheif": True,
        "with_raw": False,  # libraw is available under CDDL-1.0 or LGPL-2.1, for this reason it is disabled by default
        "with_openjpeg": True,
        "with_openvdb": False,  # FIXME: broken on M1
        "with_ptex": True,
        "with_libwebp": True,
    }

    short_paths = True

    def export_sources(self):
        files.export_conandata_patches(self)
        #for patch in self.conan_data.get("patches", {}).get(self.version, []):
        #    self.copy(patch["patch_file"])

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.fPIC

    def layout(self):
        cmake_layout(self, src_folder="src")

    def generate(self):
        tc = CMakeToolchain(self)
        tc.variables["CMAKE_DEBUG_POSTFIX"] = ""
        tc.variables["OIIO_BUILD_TOOLS"] = True
        tc.variables["OIIO_BUILD_TESTS"] = False
        tc.variables["BUILD_DOCS"] = False
        tc.variables["INSTALL_DOCS"] = False
        tc.variables["INSTALL_FONTS"] = False
        tc.variables["INSTALL_CMAKE_HELPER"] = False
        tc.variables["EMBEDPLUGINS"] = True
        tc.variables["USE_PYTHON"] = False
        tc.variables["USE_EXTERNAL_PUGIXML"] = True

        tc.variables["USE_JPEGTURBO"] = (self.options.with_libjpeg == "libjpeg-turbo")
        tc.variables["USE_JPEG"] = True  # Needed for jpeg.imageio plugin, libjpeg/libjpeg-turbo selection still works

        tc.variables["USE_HDF5"] = self.options.with_hdf5
        tc.variables["USE_OPENCOLORIO"] = self.options.with_opencolorio
        tc.variables["USE_OPENCV"] = self.options.with_opencv
        tc.variables["USE_TBB"] = self.options.with_tbb
        tc.variables["USE_DCMTK"] = self.options.with_dicom
        tc.variables["USE_FFMPEG"] = self.options.with_ffmpeg
        tc.variables["USE_FIELD3D"] = False
        tc.variables["USE_GIF"] = self.options.with_giflib
        tc.variables["USE_LIBHEIF"] = self.options.with_libheif
        tc.variables["USE_LIBRAW"] = self.options.with_raw
        tc.variables["USE_OPENVDB"] = self.options.with_openvdb
        tc.variables["USE_PTEX"] = self.options.with_ptex
        tc.variables["USE_R3DSDK"] = False
        tc.variables["USE_NUKE"] = False
        tc.variables["USE_OPENGL"] = False
        tc.variables["USE_QT"] = False
        tc.variables["USE_LIBPNG"] = self.options.with_libpng
        tc.variables["USE_FREETYPE"] = self.options.with_freetype
        tc.variables["USE_LIBWEBP"] = self.options.with_libwebp
        tc.variables["USE_OPENJPEG"] = self.options.with_openjpeg

        tc.variables['BUILD_MISSING_FMT'] = False
        tc.variables['INTERNALIZE_FMT'] = False

        if self.options.with_openvdb:
            tc.variables["CMAKE_CXX_STANDARD"] = 14

        tc.cache_variables["BUILD_SHARED_LIBS"] = bool(self.options.shared)
        tc.generate()
        deps = CMakeDeps(self)
        deps.generate()

    def configure(self):
        if self.options.shared:
            del self.options.fPIC

    def requirements(self):
        # Required libraries
        self.requires("zlib/1.2.13")
        self.requires("boost/1.82.0")
        self.requires("libtiff/4.5.0")
        self.requires("openexr/3.1.7")
        if self.options.with_libjpeg == "libjpeg":
            self.requires("libjpeg/9e")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.requires("libjpeg-turbo/2.1.5.1")
        self.requires("pugixml/1.12.1")
        self.requires("libsquish/1.15")
        self.requires("tsl-robin-map/1.0.1")
        self.requires("fmt/9.1.0")

        # Optional libraries
        if self.options.with_libpng:
            self.requires("libpng/1.6.39")
        if self.options.with_freetype:
            self.requires("freetype/2.12.1")
        if self.options.with_hdf5:
            self.requires("hdf5/1.12.1")
        if self.options.with_opencolorio:
            if Version(self.version) < "2.3.7.2":
                self.requires("opencolorio/1.1.1")
            else:
                self.requires("opencolorio/2.1.0")
        if self.options.with_opencv:
            self.requires("opencv/4.5.5")
        if self.options.with_tbb:
            self.requires("onetbb/2020.3")
        if self.options.with_dicom:
            self.requires("dcmtk/3.6.6")
        if self.options.with_ffmpeg:
            self.requires("ffmpeg/4.4")
        # TODO: Field3D dependency
        if self.options.with_giflib:
            self.requires("giflib/5.2.1")
        if self.options.with_libheif:
            self.requires("libheif/1.12.0")
        if self.options.with_raw:
            self.requires("libraw/0.20.2")
        if self.options.with_openjpeg:
            self.requires("openjpeg/2.5.0")
        if self.options.with_openvdb:
            self.requires("openvdb/8.0.1")
        if self.options.with_ptex:
            self.requires("ptex/2.4.0")
        if self.options.with_libwebp:
            self.requires("libwebp/1.3.0")
        # TODO: R3DSDK dependency
        # TODO: Nuke dependency

    def validate(self):
        if self.settings.compiler.get_safe("cppstd"):
            if Version(self.version) >= "2.3.0.0" or self.options.with_openvdb:
                check_min_cppstd(self, 14)
            else:
                check_min_cppstd(self, 11)
        if is_msvc(self) and is_msvc_static_runtime(self) and self.options.shared:
            raise ConanInvalidConfiguration(
                "Building shared library with static runtime is not supported!"
            )

    def source(self):
        files.get(self, **self.conan_data["sources"][self.version], strip_root=True)

    def _patch_sources(self):
        files.replace_in_file(self, f'{self.source_folder}/src/cmake/compiler.cmake', 'set (CMAKE_CXX_STANDARD 14', f'set (CMAKE_CXX_STANDARD {self.settings.compiler.cppstd}')
        files.replace_in_file(self, f'{self.source_folder}/src/cmake/compiler.cmake', 'add_compile_options (/W1)', f'string(REPLACE W3 W1 CMAKE_CXX_FLAGS ${{CMAKE_CXX_FLAGS}})')


        files.replace_in_file(self, f'{self.source_folder}/src/cmake/externalpackages.cmake', 'add_definitions (-DOPENEXR_DLL)', f'#add_definitions (-DOPENEXR_DLL)')
        files.replace_in_file(self, f'{self.source_folder}/src/cmake/externalpackages.cmake', 'add_definitions (-DBOOST_ALL_DYN_LINK=1)', f'#add_definitions (-DBOOST_ALL_DYN_LINK=1)')
        files.replace_in_file(self, f'{self.source_folder}/src/cmake/externalpackages.cmake', 'OPENEXR_VERSION VERSION_GREATER_EQUAL 3.0', f'OpenEXR_VERSION VERSION_GREATER_EQUAL 3.0')


        files.apply_conandata_patches(self)

    def build(self):
        self._patch_sources()
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

        files.rmdir(self, os.path.join(self.package_folder, "lib", "cmake"))
        files.rmdir(self, os.path.join(self.package_folder, "lib", "pkgconfig"))
        files.rmdir(self, os.path.join(self.package_folder, "share"))

        files.copy(self, "LICENSE.md", src=self.source_folder, dst="licenses")

    def package_info(self):
        self.cpp_info.set_property("cmake_file_name", "OpenImageIO")
        self.cpp_info.set_property("cmake_target_name", "OpenImageIO::OpenImageIO")
        self.cpp_info.set_property("pkg_config_name", "OpenImageIO")

        self.cpp_info.components["openimageio_util"].set_property(
            "cmake_target_name", "OpenImageIO::OpenImageIO_Util"
        )
        self.cpp_info.components["openimageio_util"].libs = ["OpenImageIO_Util"]
        self.cpp_info.components["openimageio_util"].requires = [
            "boost::filesystem",
            "boost::thread",
            "boost::system",
            "boost::regex",
            "openexr::openexr",
        ]
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["openimageio_util"].system_libs.extend(
                ["dl", "m", "pthread"]
            )

        self.cpp_info.components["main"].set_property(
            "cmake_target_name", "OpenImageIO::OpenImageIO"
        )
        self.cpp_info.components["main"].set_property("pkg_config_name", "OpenImageIO")
        self.cpp_info.components["main"].libs = ["OpenImageIO"]
        self.cpp_info.components["main"].requires = [
            "openimageio_util",
            "zlib::zlib",
            "boost::thread",
            "boost::system",
            "boost::container",
            "boost::regex",
            "libtiff::libtiff",
            "openexr::openexr",
            "pugixml::pugixml",
            "tsl-robin-map::tsl-robin-map",
            "libsquish::libsquish",
            "fmt::fmt",
        ]
        if self.options.with_libjpeg == "libjpeg":
            self.cpp_info.components["main"].requires.append("libjpeg::libjpeg")
        elif self.options.with_libjpeg == "libjpeg-turbo":
            self.cpp_info.components["main"].requires.append(
                "libjpeg-turbo::libjpeg-turbo"
            )
        if self.options.with_libpng:
            self.cpp_info.components["main"].requires.append("libpng::libpng")
        if self.options.with_freetype:
            self.cpp_info.components["main"].requires.append("freetype::freetype")
        if self.options.with_hdf5:
            self.cpp_info.components["main"].requires.append("hdf5::hdf5")
        if self.options.with_opencolorio:
            self.cpp_info.components["main"].requires.append("opencolorio::opencolorio")
        if self.options.with_opencv:
            self.cpp_info.components["main"].requires.append("opencv::opencv")
        if self.options.with_tbb:
            self.cpp_info.components["openimageio_util"].requires.append("onetbb::onetbb")
        if self.options.with_dicom:
            self.cpp_info.components["main"].requires.append("dcmtk::dcmtk")
        if self.options.with_ffmpeg:
            self.cpp_info.components["main"].requires.append("ffmpeg::ffmpeg")
        if self.options.with_giflib:
            self.cpp_info.components["main"].requires.append("giflib::giflib")
        if self.options.with_libheif:
            self.cpp_info.components["main"].requires.append("libheif::libheif")
        if self.options.with_raw:
            self.cpp_info.components["main"].requires.append("libraw::libraw")
        if self.options.with_openjpeg:
            self.cpp_info.components["main"].requires.append("openjpeg::openjpeg")
        if self.options.with_openvdb:
            self.cpp_info.components["main"].requires.append("openvdb::openvdb")
        if self.options.with_ptex:
            self.cpp_info.components["main"].requires.append("ptex::ptex")
        if self.options.with_libwebp:
            self.cpp_info.components["main"].requires.append("libwebp::libwebp")
        if self.settings.os in ["Linux", "FreeBSD"]:
            self.cpp_info.components["main"].system_libs.extend(["dl", "m", "pthread"])

        if not self.options.shared:
            self.cpp_info.components["main"].defines.append("OIIO_STATIC_DEFINE")
