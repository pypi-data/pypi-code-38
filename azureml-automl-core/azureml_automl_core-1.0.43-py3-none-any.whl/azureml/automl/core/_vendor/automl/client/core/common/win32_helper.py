# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
"""win32_helper.py, Helper code that wraps the Win32 API using ctypes."""
from typing import cast, Dict, List, Optional, Tuple, TypeVar
import sys


if sys.platform == 'win32':
    import ctypes
    from ctypes import wintypes
    from ctypes import windll
    from .exceptions import ClientException

    JobInfoStruct = TypeVar('JobInfoStruct', bound=ctypes.Structure)

    class PROCESS_MEMORY_COUNTERS_EX(ctypes.Structure):
        """Process memory counters class."""

        _fields_ = [('cb', wintypes.DWORD),
                    ('PageFaultCount', wintypes.DWORD),
                    ('PeakWorkingSetSize', wintypes.WPARAM),
                    ('WorkingSetSize', wintypes.WPARAM),
                    ('QuotaPeakPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaPeakNonPagedPoolUsage', wintypes.WPARAM),
                    ('QuotaNonPagedPoolUsage', wintypes.WPARAM),
                    ('PagefileUsage', wintypes.WPARAM),
                    ('PeakPagefileUsage', wintypes.WPARAM),
                    ('PrivateUsage', wintypes.WPARAM)]

    class IO_COUNTERS(ctypes.Structure):
        """IO counters class."""

        _fields_ = [('ReadOperationCount', wintypes.ULARGE_INTEGER),
                    ('WriteOperationCount', wintypes.ULARGE_INTEGER),
                    ('OtherOperationCount', wintypes.ULARGE_INTEGER),
                    ('ReadTransferCount', wintypes.ULARGE_INTEGER),
                    ('WriteTransferCount', wintypes.ULARGE_INTEGER),
                    ('OtherTransferCount', wintypes.ULARGE_INTEGER)]

    class JOBOBJECT_BASIC_ACCOUNTING_INFORMATION(ctypes.Structure):
        """Basic accounting information class."""

        _fields_ = [('TotalUserTime', wintypes.LARGE_INTEGER),
                    ('TotalKernelTime', wintypes.LARGE_INTEGER),
                    ('ThisPeriodTotalUserTime', wintypes.LARGE_INTEGER),
                    ('ThisPeriodTotalKernelTime', wintypes.LARGE_INTEGER),
                    ('TotalPageFaultCount', wintypes.DWORD),
                    ('TotalProcesses', wintypes.DWORD),
                    ('ActiveProcesses', wintypes.DWORD),
                    ('TotalTerminatedProcesses', wintypes.DWORD)]

    class JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION(ctypes.Structure):
        """Basic accounting information and IO counters class."""

        _fields_ = [('BasicInfo', JOBOBJECT_BASIC_ACCOUNTING_INFORMATION),
                    ('IoInfo', IO_COUNTERS)]

    class MEMORYSTATUSEX(ctypes.Structure):
        """The information about memory."""

        _fields_ = [
            ('dwLength', wintypes.ULONG),
            ('dwMemoryLoad', wintypes.ULONG),
            ('ullTotalPhys', wintypes.ULARGE_INTEGER),
            ('ullAvailPhys', wintypes.ULARGE_INTEGER),
            ('ullTotalPageFile', wintypes.ULARGE_INTEGER),
            ('ullAvailPageFile', wintypes.ULARGE_INTEGER),
            ('ullTotalVirtual', wintypes.ULARGE_INTEGER),
            ('ullAvailVirtual', wintypes.ULARGE_INTEGER),
            ('ullAvailExtendedVirtual', wintypes.ULARGE_INTEGER)
        ]

    class JobObjectInfoClass:
        """Job object information class."""

        JobObjectBasicAccountingInformation = 1
        JobObjectBasicAndIoAccountingInformation = 8
        JobObjectBasicLimitInformation = 2
        JobObjectBasicProcessIdList = 3
        JobObjectBasicUIRestrictions = 4
        JobObjectCpuRateControlInformation = 15
        JobObjectEndOfJobTimeInformation = 6
        JobObjectExtendedLimitInformation = 9
        JobObjectGroupInformation = 11
        JobObjectGroupInformationEx = 14
        JobObjectLimitViolationInformation = 13
        JobObjectLimitViolationInformation2 = 35
        JobObjectNetRateControlInformation = 32
        JobObjectNotificationLimitInformation = 12
        JobObjectNotificationLimitInformation2 = 34

    class Win32Exception(ClientException):
        """Exception related to a win32 API call."""

        def __init__(self, api_name: str, error_code: int):
            """
            Construct a new Win32Exception.

            :param api_name: API name
            :param error_code: Win32 error code
            """
            self.api_name = api_name
            self.error_code = error_code
            super().__init__('Win32 {} API call failed: [WinError {}] {}'.format(
                api_name, error_code, ctypes.FormatError(error_code)
            ))

    class Win32Helper:
        """Win32Helper class."""

        def __init__(self):
            """Initialize Win32Helper class."""
            # Get a handle to ourselves for future use

            # HANDLE GetCurrentProcess()
            self.current_process = cast(wintypes.HANDLE, windll.kernel32.GetCurrentProcess())

            self.child_handles = {}     # type: Dict[int, wintypes.HANDLE]

            if not self.is_process_in_job():
                # Create a job with the name automl-{PID} and assign ourselves to it. All child processes will inherit
                # this job object so we can look them up later.
                # We don't need to hold a reference to the job object because passing NULL instead of a job handle
                # will make the Win32 API use this process's job.

                # HANDLE CreateJobObjectW(LPSECURITY_ATTRIBUTES lpJobAttributes, LPWSTR lpName)
                job_object = cast(wintypes.HANDLE,
                                  windll.kernel32.CreateJobObjectW(None, 'automl-{}'.format(self.get_process_id())))

                self.assign_process_to_job_object(job_object)

        def __del__(self):
            """Destructor for the Win32Helper class."""
            # Clean up all handles to child processes to prevent memory leaks
            for pid in self.child_handles:
                self.close_handle(self.child_handles[pid])

        def close_handle(self, handle: wintypes.HANDLE) -> None:
            """
            Close handle wrapper for the Win32 CloseHandle function.

            BOOL WINAPI CloseHandle(
              _In_ HANDLE hObject
            );

            :param handle: A valid handle to an open object.
            """
            success = windll.kernel32.CloseHandle(handle)
            if success == 0:
                raise self.get_error('CloseHandle')

        def get_process_id(self) -> int:
            """
            Get process Id for Win32 GetProcessId function.

            DWORD GetProcessId(
              HANDLE Process
            );

            :return: the pid of the current process
            """
            return cast(int, windll.kernel32.GetProcessId(self.current_process))

        def open_process(self, pid: Optional[int] = None) -> wintypes.HANDLE:
            """
            Open process wrapper for the Win32 OpenProcess function.

            Note: If a handle was already opened, the previously opened handle is returned instead. This is to prevent
            memory leaks from opening too many handles and then failing to close them. This way, we only need to close
            handles once (when this object is destroyed).
            HANDLE OpenProcess(
              DWORD dwDesiredAccess,
              BOOL  bInheritHandle,
              DWORD dwProcessId
            );

            :param pid: The PID of the process to create a handle for. If None, uses the current process.
            :return: the handle of the process
            """
            if pid is None:
                return self.current_process

            if pid in self.child_handles:
                return self.child_handles[pid]

            PROCESS_ALL_ACCESS = (0x000F0000 | 0x00100000 | 0xFFF)
            handle = cast(wintypes.HANDLE, windll.kernel32.OpenProcess(PROCESS_ALL_ACCESS, False, pid))
            if handle == 0:
                raise self.get_error('OpenProcess')
            self.child_handles[pid] = handle
            return handle

        def get_process_memory_info(self, pid: Optional[int] = None) -> PROCESS_MEMORY_COUNTERS_EX:
            """
            Get process memory info wrapper for the Win32 GetProcessMemoryInfo function.

            BOOL GetProcessMemoryInfo(
              HANDLE                   Process,
              PPROCESS_MEMORY_COUNTERS ppsmemCounters,
              DWORD                    cb
            );

            :param pid: ID of the process we want to get memory usage for. If None, gets usage for current process.
            :return: a PROCESS_MEMORY_COUNTERS_EX struct
            """
            handle = self.open_process(pid)
            pmc = PROCESS_MEMORY_COUNTERS_EX()
            success = windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(pmc), ctypes.sizeof(pmc))
            if success == 0:
                raise self.get_error('GetProcessMemoryInfo')
            return pmc

        def assign_process_to_job_object(self, job: wintypes.HANDLE, pid: Optional[int] = None) -> None:
            """
            Assign process to job object wrapper for the Win32 AssignProcessToJobObject function.

            BOOL WINAPI AssignProcessToJobObject(
              _In_ HANDLE hJob,
              _In_ HANDLE hProcess
            );
            :param job: Handle to the job object we want to assign to.
            :param pid: ID of the process we want to assign to the job. If None, assigns the current process.
            """
            handle = self.open_process(pid)
            success = windll.kernel32.AssignProcessToJobObject(job, handle)
            if success == 0:
                raise self.get_error('AssignProcessToJobObject')

        def is_process_in_job(self) -> bool:
            """
            Is process in job wrapper for the Win32 IsProcessInJob function.

            BOOL WINAPI IsProcessInJob(
              _In_     HANDLE ProcessHandle,
              _In_opt_ HANDLE JobHandle,
              _Out_    PBOOL  Result
            );

            :return: true if this process is running inside a job, false otherwise
            """
            result = ctypes.c_bool(False)
            success = windll.kernel32.IsProcessInJob(self.current_process, None, ctypes.byref(result))

            if success == 0:
                raise Win32Helper.get_error('IsProcessInJob')

            return result.value

        def query_information_job_object(self,
                                         job_object_info_class: int,
                                         job_info_struct: JobInfoStruct) -> JobInfoStruct:
            """
            Query job object information wrapper for the Win32 QueryInformationJobObject function.

            Queries info for the job this process is in.
            BOOL WINAPI QueryInformationJobObject(
              _In_opt_  HANDLE             hJob,
              _In_      JOBOBJECTINFOCLASS JobObjectInfoClass,
              _Out_     LPVOID             lpJobObjectInfo,
              _In_      DWORD              cbJobObjectInfoLength,
              _Out_opt_ LPDWORD            lpReturnLength
            );

            :param job_object_info_class: the info class that should be queried
            :param job_info_struct: a struct to pass to the query
            :return: a struct with the job info, type depends on which info class is specified
            """
            out_size = wintypes.DWORD()

            success = windll.kernel32.QueryInformationJobObject(None,
                                                                job_object_info_class,
                                                                ctypes.byref(job_info_struct),
                                                                ctypes.sizeof(job_info_struct),
                                                                ctypes.byref(out_size))
            if success == 0:
                raise self.get_error('QueryInformationJobObject')
            return job_info_struct

        def get_process_times(self, pid: Optional[int] = None) -> Tuple[float, float, float, float]:
            """
            Get process time wrapper for the Win32 GetProcessTimes function.

            Retrieves timing information for the specified process.
            Note: The Win32 API returns times in 100ns increments, but this function converts to seconds.
            BOOL GetProcessTimes(
              HANDLE     hProcess,
              LPFILETIME lpCreationTime,
              LPFILETIME lpExitTime,
              LPFILETIME lpKernelTime,
              LPFILETIME lpUserTime
            );

            :param pid: The PID of the process to get timing information for. If None, gets info for this process.
            :return: a tuple of ints containing (creation time, exit time, kernel time, user time) in seconds
            """
            handle = self.open_process(pid)

            creation_time = wintypes.FILETIME()
            exit_time = wintypes.FILETIME()
            kernel_time = wintypes.FILETIME()
            user_time = wintypes.FILETIME()

            success = windll.kernel32.GetProcessTimes(handle,
                                                      ctypes.byref(creation_time),
                                                      ctypes.byref(exit_time),
                                                      ctypes.byref(kernel_time),
                                                      ctypes.byref(user_time))
            if success == 0:
                raise self.get_error('GetProcessTimes')

            def ft_to_sec(ft):
                total = ft.dwHighDateTime << 32
                total += ft.dwLowDateTime
                return total / 10000000

            return ft_to_sec(creation_time), ft_to_sec(exit_time), ft_to_sec(kernel_time), ft_to_sec(user_time)

        def get_current_memory_usage(self) -> Tuple[int, int]:
            """
            Get physical and virtual memory usage of this process.

            :return: a tuple containing [physical memory used, virtual memory used] in bytes
            """
            mem_info = self.get_process_memory_info()
            return mem_info.WorkingSetSize, mem_info.PrivateUsage

        def get_children_memory_usage(self) -> Tuple[int, int]:
            """
            Get physical and virtual memory usage of all of this process's children.

            :return: a tuple containing [physical memory used, virtual memory used] in bytes
            """
            pids = self.get_job_process_list()
            mem_info = [self.get_process_memory_info(pid) for pid in pids if pid != self.current_process]
            physical_mem = 0
            virtual_mem = 0
            for info in mem_info:
                physical_mem += info.WorkingSetSize
                virtual_mem += info.PrivateUsage
            return physical_mem, virtual_mem

        def get_job_accounting_info(self) -> JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION:
            """
            Get basic accounting and I/O accounting information for the job this process is in.

            :return: a JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION struct
            """
            struct = JOBOBJECT_BASIC_AND_IO_ACCOUNTING_INFORMATION()
            return self.query_information_job_object(JobObjectInfoClass.JobObjectBasicAndIoAccountingInformation,
                                                     struct)

        def get_job_process_list(self) -> List[int]:
            """
            Get list of pids of all processes associated with the job this process is in.

            :return: a list of all pids
            """
            max_processes = 100
            while True:
                try:
                    # This must be defined dynamically because the struct is variable length
                    class JobObjectBasicProcessIdListStruct(ctypes.Structure):
                        _fields_ = [('NumberOfAssignedProcesses', wintypes.DWORD),
                                    ('NumberOfProcessIdsInList', wintypes.DWORD),
                                    ('ProcessIdList', wintypes.WPARAM * max_processes)]
                    struct = JobObjectBasicProcessIdListStruct()
                    struct.NumberOfAssignedProcesses = max_processes
                    self.query_information_job_object(JobObjectInfoClass.JobObjectBasicProcessIdList, struct)
                    break
                except Win32Exception as e:
                    # Win32 error code 234: More data is available
                    if e.error_code != 234:
                        raise
                    max_processes *= 2
            return list(struct.ProcessIdList[:struct.NumberOfProcessIdsInList])

        def get_child_process_times(self) -> Tuple[float, float, float, float]:
            """
            Get timing information for all currently running processes in this job, except this one.

            :return: a tuple of ints containing (creation time, exit time, kernel time, user time) in seconds
            """
            pids = self.get_job_process_list()
            timing_info = [self.get_process_times(pid) for pid in pids if pid != self.current_process]
            creation_t = 0.0
            exit_t = 0.0
            kernel_t = 0.0
            user_t = 0.0
            for info in timing_info:
                creation_t += info[0]
                exit_t += info[1]
                kernel_t += info[2]
                user_t += info[3]
            return creation_t, exit_t, kernel_t, user_t

        def get_resource_usage(self) -> Tuple[int, int, float, float, int, int, float, float]:
            """
            Get resource usage for both this process and all child processes in this job.

            :return: a tuple with the following values:
                - parent physical memory usage
                - parent virtual memory usage
                - parent kernel CPU time
                - parent user CPU time
                - child physical memory usage
                - child virtual memory usage
                - child kernel CPU time
                - child user CPU time
            """
            process_creation, process_exit, process_kernel, process_user = self.get_process_times()
            job_info = self.get_job_accounting_info()
            child_kernel = (job_info.BasicInfo.TotalKernelTime / 10000000) - process_kernel
            child_user = (job_info.BasicInfo.TotalUserTime / 10000000) - process_user

            process_phys_mem, process_virt_mem = self.get_current_memory_usage()
            child_phys_mem, child_virt_mem = self.get_children_memory_usage()

            return process_phys_mem, process_virt_mem, process_kernel, process_user, child_phys_mem, child_virt_mem, \
                child_kernel, child_user

        @staticmethod
        def get_all_ram() -> int:
            """
            Retrieve amount of installed RAM in bytes.

            :returns: The amount of memory in bytes.
            """
            kernel32 = ctypes.windll.kernel32
            memoryStatus = MEMORYSTATUSEX()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
            return cast(int, memoryStatus.ullTotalPhys)

        @staticmethod
        def get_available_physical_memory() -> int:
            """
            Retrieve the amount of physical memory available.

            :return: The amount of physical memory in bytes.
            """
            kernel32 = ctypes.windll.kernel32
            memoryStatus = MEMORYSTATUSEX()
            memoryStatus.dwLength = ctypes.sizeof(MEMORYSTATUSEX)
            kernel32.GlobalMemoryStatusEx(ctypes.byref(memoryStatus))
            return cast(int, memoryStatus.ullAvailPhys)

        @staticmethod
        def get_error(api_name: str) -> Win32Exception:
            """
            Retrieve and format the last error generated by a Win32 API call.

            :param api_name: Name of the API call that triggered the error
            :return: RuntimeError with a formatted message describing the error
            """
            return Win32Exception(api_name, ctypes.GetLastError())
else:
    class Win32Helper:
        """Stub class that does nothing. Only used on non-Windows platforms."""

        def __init__(self):
            """Raise an error."""
            raise OSError('Using this class is not supported on non-Windows platforms')
