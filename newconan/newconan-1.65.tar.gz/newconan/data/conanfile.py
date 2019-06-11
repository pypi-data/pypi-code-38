from conans import ConanFile, CMake, tools

class {project_name}Conan(ConanFile):
    name = "{project_name}"
    version = "1.0.0"
    settings = "os", "compiler", "build_type", "arch"
    requires = ()
    generators = "cmake"
    scm = {
        "type": "git",
        "subfolder": name,
        "url": "auto",
        "revision": "auto"
    }
    options = {
        "shared": [True, False],
    }
    default_options = {
        "shared": {is_shared}
    }
    
    def build(self):
        cmake = CMake(self)
        cmake.definitions["BUILD_TEST"] = False
        cmake.definitions["BUILD_SHARED"] = self.options.shared
        cmake.configure(source_folder=self.name)
        cmake.build()
    
    def imports(self):
        self.copy("*.dll", dst="bin", src="bin")
        self.copy("*.dll", dst="bin", src="lib")
        self.copy("*.so", dst="bin", src="bin")
        self.copy("*.so", dst="bin", src="lib")
        self.copy("*.pdb", dst="bin", src="bin")
        self.copy("*", dst="bin/assets/public", src="resources")
    
    def package(self):
        self.copy("*.h", dst="include", src=f"{self.name}/src")
        self.copy("*.dll", dst="bin", src="bin", keep_path=False)
        self.copy("*.so", dst="bin", src="bin", keep_path=False)
        self.copy("*.dylib", dst="bin", src="bin", keep_path=False)
        self.copy("*.a", dst="lib", src="lib", keep_path=False)
        self.copy("*.lib", dst="lib", src="lib", keep_path=False)
        self.copy("*", dst=f"resources/{self.name}", src=f"{self.name}/assets/public/{self.name}")
    
    def package_info(self):
        self.cpp_info.libs = tools.collect_libs(self)
