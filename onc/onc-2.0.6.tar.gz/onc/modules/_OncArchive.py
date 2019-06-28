from ._OncService import _OncService
import requests
import json
import puremagic
import humanize
import time
from ._util import saveAsFile
from ._util import _printErrorMessage

class _OncArchive(_OncService):
    """
    Methods that wrap the API archivefiles service
    """

    def __init__(self, config: dict):
        super().__init__(config)


    def getListByLocation(self, locationCode: str, filters: dict):
        """
        Get a list of files for a given location code and device category code, and filtered by others optional parameters.
        """
        filters['locationCode'] = locationCode
        try:
            return self._getList(filters, by='location')
        except Exception: raise


    def getListByDevice(self, deviceCode: str, filters: dict):
        """
        Get a list of files available in Oceans 2.0 Archiving System for a given device code. The list of filenames can be filtered by time range.
        """
        filters['deviceCode'] = deviceCode
        try:
            return self._getList(filters, by='device')
        except Exception: raise


    def getFile(self, filename: str='', overwrite: bool=True):
        cfg = self.config
        url = self._serviceUrl('archivefiles')
        filters = {
            'token'   : cfg['token'],
            'method'  : 'getFile',
            'filename': filename,
        }

        try:
            # Download the archived file with filename (response contents is binary)
            start = time.time()
            response = requests.get(url, filters, timeout=self.config['timeout'])
            elapsed = time.time() - start
            
            if response.ok:
                # Save file to output path
                outPath = self.config['outPath']
                saveAsFile(response, outPath, filename, overwrite)

                # @BUGFIX (2018/11/27): Currently the API might return a .gz file without extension
                # if this is a gzipped compressed file with the wrong extension, append the extension
                filePath = '{:s}/{:s}'.format(outPath, filename)
                mime = puremagic.magic_file(filePath)
                if mime[0][1] == 'application/x-gzip':
                    extension = filePath.split(".")[-1]
                    if extension != 'gz':
                        oldFilePath = filePath
                        filePath += '.gz'
                        try:
                            os.rename(oldFilePath, filePath)
                        except:
                            filePath = oldFilePath
                            self._log('   A compressed file was downloaded to "{0}" but it was impossible to add the .gz extension. Consider doing this manually.'.format(filePath))
                
            else:
                status = response.status_code
                if self.showInfo:
                    _printErrorMessage(response, filters)
                
                if status == 400:
                    raise Exception('   The request failed with HTTP status 400.', response.json())
                else:
                    raise Exception('   The request failed with HTTP status {:d}.'.format(status), response.text)

        except Exception: raise
        
        return {
            'url'         : response.url,
            'status'      : response.status_code,
            'size'        : len(response.content),
            'downloadTime': round(elapsed, 3),
            'file'        : filePath
        }


    def getDirectFiles(self, filters: dict, overwrite: bool=True):
        '''
        Method to download files from the archivefiles service 
        which match filter criteria defined by a dictionary of filters
        see https://wiki.oceannetworks.ca/display/help/archivefiles for usage and available filters
        '''
        # make sure we only get a simple list of files
        if 'returnOptions' in filters:
            del filters['returnOptions']

        # Get a list of files
        try:
            if 'locationCode' in filters and 'deviceCategoryCode' in filters:
                dataRows = self.getListByLocation(filters)
            elif 'deviceCode' in filters:
                dataRows = self.getListByDevice(filters)
            else:
                raise Exception('getDirectFiles filters require either a combination of "locationCode" and "deviceCategoryCode", or a "deviceCode" present.')
        except Exception: raise
        
        n = len(dataRows['files'])
        print('Obtained a list of {:d} files to download.'.format(n))

        # Download the files obtained
        tries = 1
        successes = 0
        size = 0
        time = 0
        downInfos = []
        for filename in dataRows['files']:
            print('   ({:d} of {:d}) Downloading file: "{:s}"...'.format(tries, n, filename))
            try:
                downInfo = self.getFile(filename, overwrite)
                size += downInfo['size']
                time += downInfo['downloadTime']
                downInfos.append(downInfo)
                successes += 1
            except Exception: raise
            tries += 1

        print('{:d} files ({:s}) downloaded'.format(successes, humanize.naturalsize(size)))
        print('Total Download Time: {:s}'.format(self._formatDuration(time)))

        return {
            'downloadResults': downInfos,
            'stats': {
                'totalSize'   : size,
                'downloadTime': time,
                'fileCount'   : successes
            }
        }


    def _getList(self, filters: dict, by: str='location'):
        """
        Wraps archivefiles getListByLocation and getListByDevice methods
        """
        url = self._serviceUrl('archivefiles')
        filters['token'] = self.token
        if by == 'location': 
            filters['method'] = 'getListByLocation'
        else:
            filters['method'] = 'getListByDevice'

        # parse and remove the artificial paramenter extension
        extension = None
        if 'extension' in filters:
            extension = filters['extension']
            del filters['extension']

        try:
            result = self._doRequest(url, filters)
        except Exception: raise

        # filter by extension
        if extension:
            result = self._filterByExtension(result, extension)

        return result


    def _filterByExtension(self, results: dict, extension: str):
        '''
        Filter results to only those where filenames end with the extension
        Return a filtered list
        '''
        n = len(extension)
        filtered = [] # appending is faster than deleting
        
        # figure out the row type downloaded from the contents
        rowFormat = ''
        r0 = results['files'][0]
        if isinstance(r0, str):
            rowFormat = 'filename'
        elif isinstance(r0, dict):
            if 'dataProductCode' in r0:
                rowFormat = 'archiveLocation'
            else:
                rowFormat = 'all'

        # filter
        for file in results['files']:
            if rowFormat == 'filename':
                if file[-n:] == extension:
                    filtered.append(file)   
            else:
                if file['filename'][-n:] == extension:
                    filtered.append(file)
        results['files'] = filtered

        return results
