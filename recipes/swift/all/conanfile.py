import os
from conans import ConanFile, tools


class SwiftConan(ConanFile):
    name = "swift"
    version = "5.3.3"
    license = "Apache-2.0 License"
    url = "<Package recipe repository url here, for issues about the package>"
    description = "<Description of Swift here>"
    topics = ("<Put some tag here>", "<here>", "<and here>")
    settings = "os", "compiler", "build_type", "arch"
    no_copy_source = True

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    @property
    def _build_subfolder(self):
        return "build_subfolder"

    def requirements(self):
        self.requires('icu/68.2')

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        os.rename("swift-swift-%s-RELEASE" % self.version, self._source_subfolder)

    def build(self):
        src = os.path.join(self.source_folder, self._source_subfolder)
        build_script = os.path.join(src, 'utils', 'build-script')

        ndk_root = os.environ['NDK_ROOT']

        icu_lib_path = self.deps_cpp_info['icu'].lib_paths[0]
        libicuuc = os.path.join(icu_lib_path, 'libicuuc.a')
        libicui18n = os.path.join(icu_lib_path, 'libicui18n.a')
        libicudata = os.path.join(icu_lib_path, 'libicudata.a')

        icu_include_path = self.deps_cpp_info['icu'].include_paths[0]

        cmd = f'{build_script} -R --android --android-ndk {ndk_root} --android-arch aarch64 --android-api-level {self.settings.os.api_level} ' + \
        f'--android-icu-uc {libicudata} ' + \
        f'--android-icu-uc-include {icu_include_path} ' + \
        f'--android-icu-i18n {libicui18n} ' + \
        f'--android-icu-i18n-include {icu_include_path} ' + \
        f'--android-icu-data {libicudata}'

        self.output.info(cmd)

        self.run(cmd)

    def package(self):
        pass

    def package_info(self):
        pass

