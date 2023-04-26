from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.files import copy, get
import os


class AgilitySDKConan(ConanFile):
    name = "agility-sdk"
    description = "Agility DirectX12 SDK"
    license = "****????"
    homepage = "https://devblogs.microsoft.com/directx/directx12agility/"
    url = "https://github.com/conan-io/conan-center-index"
    topics = ("graphics", "windows")
    settings = "os", "arch", "compiler", "build_type"

    def layout(self):
        self.folders.build = "build"

    def package_id(self):
        del self.info.settings.compiler
        del self.info.settings.build_type

    def validate(self):
        if self.info.settings.os != "Windows":
            raise ConanInvalidConfiguration("Agility SDK is only intended to be used on Windows.")

    def source(self):
        pass

    def build(self):
        get(self, **self.conan_data["sources"][self.version], destination=self.build_folder)

    def package(self):
        copy(self, pattern="*", src=os.path.join(self.build_folder, "build", "native", "bin", self._msvc_platform), dst=os.path.join(self.package_folder, "bin"))
        copy(self, pattern="*", src=os.path.join(self.build_folder, "build", "native", "include"), dst=os.path.join(self.package_folder, "include"))
        copy(self, pattern="*", src=os.path.join(self.build_folder, "build", "native", "src"), dst=os.path.join(self.package_folder, "src"))

    def package_info(self):
        self.cpp_info.libdirs = []

    @property
    def _msvc_platform(self):
        return {
            "x86_64": "x64",
            "x86": "win32",
            "armv8": "arm64",
            "armv8_32": "arm",
            "armv7": "arm",
        }[str(self.settings.arch)]
