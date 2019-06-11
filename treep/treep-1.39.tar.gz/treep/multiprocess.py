# Treep, copyright 2019 Max Planck Gesellschaft
# Author : Vincent Berenz 

# This file is part of Treep.

#    Treep is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    Treep is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with Treep.  If not, see <https://www.gnu.org/licenses/>.



import multiprocessing,copy


class _Pseudo_lock:
    def __enter__(self):
        return self
    def __exit__(self,type,value,traceback):
        pass


class Multiprocess:

    def __init__(self,
                 multiprocess,
                 target_function,
                 console,
                 raise_exception):

        self._multiprocess = multiprocess
        self._target_function = target_function
        self._console = console
        self._raise_exception = raise_exception

        if multiprocess:
            manager = multiprocessing.Manager()
            self._shared_errors = manager.dict()
            self._shared_lock = manager.Lock()

        else :
            self._shared_errors = {}
            self._shared_lock = _Pseudo_lock()


    def execute(self,repo_config):

        processes = []

        for repo_name,config in repo_config.items():

            if self._multiprocess:
                process = multiprocessing.Process( target = self._target_function,
                                                   args = ( self._shared_errors,self._shared_lock,
                                                            config,
                                                            self._console,self._raise_exception ) )
                process.start()
                processes.append(process)

            else :

                self._target_function(self._shared_errors,self._shared_lock,
                                      config,
                                      self._console,self._raise_exception)

        if self._multiprocess:
            for process in processes:
                process.join()

        return self._shared_errors
        
