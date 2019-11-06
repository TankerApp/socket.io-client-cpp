from conans import ConanFile, CMake, tools
import os


class SocketIOClientCppConan(ConanFile):
    name = "socket.io-client-cpp"
    version = "1.6.3"
    lib_tag = version + ""
    license = "MIT"
    repo_url = "https://github.com/TankerHQ/socket.io-client-cpp"
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False], "with_ssl": [True, False]}
    default_options = "shared=False", "fPIC=True", "with_ssl=True"
    generators = "cmake"
    exports_sources = "*.patch"

    @property
    def socketio_src(self):
        return os.path.join(self.source_folder, self.name)

    @property
    def is_mingw(self):
        return self.settings.os == "Windows" and self.settings.compiler == "gcc"

    def requirements(self):
        self.requires("Boost/1.71.0@tanker/testing")
        if self.options.with_ssl:
            self.requires("LibreSSL/2.9.2@tanker/testing")

    def source(self):
        self.run("git clone %s --single-branch --branch %s --recurse-submodules" % (self.repo_url, self.lib_tag))
        with tools.chdir(self.name):
            self.run("git submodule update --remote")

    def build(self):
        if self.is_mingw:
            tools.patch(patch_file="CMakeLists.txt-mingw.patch", base_path=os.path.join(self.build_folder, self.name))
        cmake = CMake(self)
        cmake.definitions["BUILD_SHARED_LIBS"] = self.options.shared
        cmake.definitions["CMAKE_POSITION_INDEPENDENT_CODE"] = self.options.fPIC
        cmake.definitions["BUILD_WITH_TLS"] = self.options.with_ssl
        cmake.configure(source_dir=self.socketio_src)
        cmake.build()
        cmake.install()

    def package(self):
        # socketio installs in src/build (hardcoded in cmakelists)
        include_path = os.path.join(self.socketio_src, "build", "include", "src")
        self.copy("*", src=include_path, dst="include")
        self.copy("*.a", dst="lib", keep_path=False)
        self.copy("*.so*", dst="lib", keep_path=False)
        self.copy("*.dylib", dst="lib", keep_path=False)
        self.copy("*.lib", dst="lib", keep_path=False)
        self.copy("*.dll", dst="bin", keep_path=False)
        self.copy("*.pdb", dst="lib", keep_path=False)
        self.copy("*LICENSE", dst="licenses", keep_path=False)

    def package_info(self):
        self.cpp_info.libs = ["sioclient"]
        if self.settings.os == "Windows" and self.options.with_ssl:
            self.cpp_info.libs.extend(["crypt32"])
        if self.options.with_ssl:
            self.cpp_info.defines.extend(["SIO_TLS"])
