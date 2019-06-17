import os
import multiprocessing
from . import AOS, AVS


class BuildParams:
    OS_CALL_TYPE_SYSTEM = 0  # AOS.system
    OS_CALL_TYPE_PROCESS = 1  # AOS.process

    def __init__(self, sourceDir, installDir, buildType):
        """
        :param sourceDir: 根 CMakeLists.txt 所在目录
        :param installDir: 安装目录(--prefix)
        :param buildType: 构建类型(Debug or Release)
        """
        self.sourceDir = sourceDir
        self.installDir = installDir
        self.buildType = buildType

        self.extraCMakeOptions = ''  # 额外的CMake选项，比如 -Dxxx=yyy

        # 生成64位程序
        # Linux下若要编译32位，需要修改CMakeLists.txt: set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -m32")
        self.x64 = True

        self.win32_vsVersion = 12  # 在Windows上构建时，使用的VS版本号

        self.unix_makeEncoding = 'iso-8859-1'  # 执行make时使用的encoding（仅当osCallType为OS_CALL_TYPE_PROCESS时才需要指定）
        self.unix_makeJobCount = multiprocessing.cpu_count() - 2  # 执行make时的并发job数量

        self.osCallType = self.OS_CALL_TYPE_SYSTEM  # 调用命令行的方式

    @property
    def generator(self):
        if os.name == 'nt':
            return ('Visual Studio %d' % self.win32_vsVersion) + (' Win64' if self.x64 else '')
        else:
            return 'Unix Makefiles'

    @property
    def unix_makeJobCountStr(self):
        if self.unix_makeJobCount >= 2:
            return '-j%d' % self.unix_makeJobCount
        else:
            return ''

    @property
    def osCall(self):
        def wrapperSystem(cmd, encoding=None):
            return AOS.system(cmd)

        if self.osCallType == self.OS_CALL_TYPE_SYSTEM:
            return wrapperSystem
        elif self.osCallType == self.OS_CALL_TYPE_PROCESS:
            return AOS.process
        else:
            assert False


def _make_win32(buildParams):    
    # 注意/t:INSTALL会失败
    buildParams.osCall(
        r'%s %s /t:build /p:Configuration=%s /p:BuildInParallel=true /m'
        % (AVS.Path(buildParams.win32_vsVersion).MSBuildEXE, 'INSTALL.vcxproj', buildParams.buildType))

def _make_unix(buildParams):    
    buildParams.osCall('make VERBOSE=1 %s' % buildParams.unix_makeJobCountStr, buildParams.unix_makeEncoding)
    buildParams.osCall('make install', buildParams.unix_makeEncoding)

def cmake(buildParams):
    """
    在当前位置进行构建并安装
    """
    buildParams.osCall('cmake -G "%s" %s -DCMAKE_INSTALL_PREFIX="%s" -DCMAKE_BUILD_TYPE=%s %s' % (
        buildParams.generator,
        buildParams.sourceDir,
        buildParams.installDir,
        buildParams.buildType,
        buildParams.extraCMakeOptions
    ), encoding='UTF-8')
    
    if os.name == 'nt':
        _make_win32(buildParams)
    else:
        _make_unix(buildParams)


# 关于接口的设计
# BuildParams并未提供buildDir，而是让用户自己创建buildDir，并进入其中进行cmake
# 好处是sourceDir的意义更清晰，并且和cmake命令的工作方式一致