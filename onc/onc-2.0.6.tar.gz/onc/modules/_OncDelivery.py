from ._OncService import _OncService
from datetime import datetime, timedelta
import requests
import os
import humanize
from time import sleep, time
from ._DataProductFile import _DataProductFile
from ._PollLog import _PollLog
from .Exceptions import MaxRetriesException


class _OncDelivery(_OncService):
    """
    Methods that wrap the API data product delivery services
    """

    def __init__(self, config: dict):
        super().__init__(config)


    def orderDataProduct(self, filters: dict, maxRetries: int, downloadResultsOnly: bool, includeMetadataFile: bool, overwrite: bool):
        fileList = []
        try:
            # Request the product
            requestData = self.requestDataProduct(filters)
            
            if downloadResultsOnly:
                # Only run and return links
                runData = self.runDataProduct(requestData['dpRequestId'], waitComplete=True)
                for runId in runData['runIds']:
                    fileList.extend(self._infoForProductFiles(runId, runData['fileCount'], includeMetadataFile))
            else:
                # Run and download files
                runData = self.runDataProduct(requestData['dpRequestId'], waitComplete=False)
                for runId in runData['runIds']:
                    fileList.extend(self._downloadProductFiles(runId, includeMetadataFile, maxRetries, overwrite))
            
            print('')
            self._printProductOrderStats(fileList, runData)
        except Exception: raise

        return self._formatResult(fileList, runData)


    def requestDataProduct(self, filters: dict):
        """
        Data product request
        """
        filters['method'] = 'request'
        filters['token']  = self.token
        try:
            url = '{:s}api/dataProductDelivery'.format(self.baseUrl)
            response = self._doRequest(url, filters)
        except Exception: raise

        self._estimatePollPeriod(response)
        self._printProductRequest(response)
        return response


    def runDataProduct(self, dpRequestId: int, waitComplete: bool):
        """
        Run a product request and optionally wait until the product generation is complete
        Return a dictionary with information of the run process
        """
        status = ''
        log = _PollLog(True)
        url = '{:s}api/dataProductDelivery'.format(self.baseUrl)
        runResult = {'runIds': [], 'fileCount': 0, 'runTime': 0, 'requestCount': 0}
        
        try:
            start = time()
            while status != 'complete':
                response = requests.get(url, {'method': 'run', 'token': self.token, 'dpRequestId': dpRequestId}, timeout=self.config['timeout'])
                runResult['requestCount'] += 1

                if response.ok:
                    data = response.json()
                else:
                    code = response.status_code
                    if self.showInfo: util.printErrorMessage(response, params)
                    raise Exception('The server request failed with HTTP status {:d}.'.format(code), code)
                
                if waitComplete:
                    status = data[0]['status']
                    log.logMessage(data)
                    sleep(self.pollPeriod)
                else:
                    status = 'complete'
            
            #self.print(data)
            #print('got filecount {}'.format(data[0]['fileCount']))
            runResult['fileCount'] = data[0]['fileCount']
            runResult['runTime'] = time() - start
            
            # print a new line after the process finishes
            if waitComplete:
                print('')

        except Exception: raise
        
        # gather a list of runIds
        for run in data:
            runResult['runIds'].append(run['dpRunId'])

        return runResult


    def downloadDataProduct(self, runId: int, maxRetries: int, downloadResultsOnly: bool, includeMetadataFile: bool, overwrite: bool):
        '''
        A public wrapper for downloadProductFiles that lets a user download data products with a runId
        '''
        try:
            if downloadResultsOnly:
                fileData = self._infoForProductFiles(runId, 0, includeMetadataFile)
            else:
                fileData = self._downloadProductFiles(runId, includeMetadataFile, maxRetries, overwrite)
        except Exception: raise

        return fileData


    def _downloadProductFiles(self, runId: int, getMetadata: bool, maxRetries: int, overwrite: bool, fileCount: int=0):
        fileList = []
        index = 1
            
        try:
            # keep increasing index until fileCount or until we get 404
            doLoop = True
            timeout = self.config['timeout']
            print('Downloading data product files with runId {:d}...'.format(runId))
            while doLoop:
                #print('downloading index {:d}'.format(index))
                dpf = _DataProductFile(runId, str(index), self.baseUrl, self.token)
                status = dpf.download(timeout, self.pollPeriod, self.outPath, maxRetries, overwrite)

                if status == 200:
                    fileList.append(dpf.getInfo(download=True))
                    index += 1

                if (status == 404) or (fileCount > 0 and index >= fileCount):
                    doLoop = False
                
            # get metadata if required
            if getMetadata:
                dpf = _DataProductFile(runId, 'meta', self.baseUrl, self.token)
                status = dpf.download(timeout, self.pollPeriod, self.outPath, maxRetries, overwrite)
                if status != 404:
                    fileList.append(dpf.getInfo(download=True))

        except Exception: raise

        return fileList


    def _infoForProductFiles(self, dpRunId: int, fileCount: int, getMetadata: bool):
        # If we don't know the fileCount, get it from the server (takes longer)
        if fileCount <= 0:
            fileCount = self._countFilesInProduct(dpRunId)

        # Build a file list of data product file information
        fileList = []
        indexes = list(range(1, fileCount + 1))
        if getMetadata:
            indexes.append('meta')
        
        for index in indexes:
            dpf = _DataProductFile(dpRunId=dpRunId, index=str(index), baseUrl=self.baseUrl, token=self.token)
            dpf.setComplete()
            fileList.append(dpf.getInfo())

        return fileList


    def _countFilesInProduct(self, runId: int):
        '''
        Given a runId, polls the "download" method to count the number of files available for download
        Uses HTTP HEAD to avoid downloading the files
        '''
        url = '{:s}api/dataProductDelivery'.format(self.baseUrl)
        filters = {'method': 'download', 'token': self.token, 'dpRunId': runId, 'index': 1}
        status = 200
        
        try:
            while status == 200:
                response = requests.head(url, filters, timeout=self.config['timeout'])
                status = response.status_code
                if status == 200:
                    filters['index'] += 1
        except Exception: raise
        return filters['index']


    def _printProductRequest(self, response):
        """
        Prints the information from a response given after a data product request
        The request response format might differ depending on the product source (archive or generated on the fly)
        """
        isGenerated = ('estimatedFileSize' in response)
        print('Request Id: {:d}'.format(response['dpRequestId']))
        
        if isGenerated:
            print('Estimated File Size: {:s}'.format(response['estimatedFileSize']))
            print('Estimated Processing Time: {:s}'.format(response['estimatedProcessingTime']))
        else:
            print('File Size: {:s}'.format(response['fileSize']))
            print('Data product is ready for download.')


    def _estimatePollPeriod(self, response):
        """
        Sets a poll period adequate to the estimated processing time
        Longer processing times require longer poll periods to avoid going over maxRetries
        """
        # Parse estimated processing time
        txtEstimated = response['estimatedProcessingTime']
        parts = txtEstimated.split(' ')
        if len(parts) == 2:
            unit = parts[1]
            factor = 1
            if unit   == 'min':
                factor = 60
            elif unit == 'hour':
                factor = 3600
            total = factor * int(parts[0])
            self.pollPeriod = max(0.02 * total, 1.0) # poll every 2%
        else:
            # No estimated processing time available, so we keep the default
            pass


    def _printProductOrderStats(self, fileList: list, runInfo: dict):
        """
        Prints a formatted representation of the total time and size downloaded
        after the product order finishes
        """
        downloadCount = 0
        downloadTime = 0
        size = 0
        
        for file in fileList:
            size += file["size"]
            if file["downloaded"]:
                downloadCount += 1
                downloadTime  += file['fileDownloadTime']

        # Print run time
        runTime = timedelta(seconds=runInfo['runTime'])
        print('Total run time: {:s}'.format(humanize.naturaldelta(runTime)))
        
        if downloadCount > 0:
            # Print download time
            if downloadTime < 1.0:
                txtDownTime = '{:.3f} seconds'.format(downloadTime)
            else:
                txtDownTime = humanize.naturaldelta(downloadTime)
            print('Total download Time: {:s}'.format(txtDownTime))

            # Print size and count of files
            print('{:d} files ({:s}) downloaded'.format(downloadCount, humanize.naturalsize(size)))
        else:
            print('No files downloaded.')


    def _formatResult(self, fileList: list, runInfo: dict):
        size = 0
        downloadTime = 0
        requestCount = runInfo['requestCount']
        
        for file in fileList:
            downloadTime += file['fileDownloadTime']
            size         += file['size']
            requestCount += file['requestCount']

        result = {
            'downloadResults': fileList,
            'stats': {
                'runTime'     : round(runInfo['runTime'], 3),
                'downloadTime': round(downloadTime, 3),
                'requestCount': requestCount,
                'totalSize'   : size
            }
        }

        return result