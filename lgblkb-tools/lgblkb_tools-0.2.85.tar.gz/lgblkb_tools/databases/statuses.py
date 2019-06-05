class MainStatus:
	delimiter='_'
	
	def __init__(self,prefix,is_fallback):
		self.prefix=prefix
		self.is_fallback=is_fallback
	
	def __get_status(self,status_text):
		out_status=MainStatus.delimiter.join([self.prefix,status_text])
		if self.is_fallback: return fbsm[out_status]
		else: return out_status
	
	@property
	def Download(self): return self.__get_status('Download')
	
	@property
	def HistoricDownload(self): return self.__get_status('HistoricDownload')
	
	@property
	def ImageCheck(self): return self.__get_status('ImageCheck')
	
	@property
	def AtmosphericCorrection(self): return self.__get_status('AtmosphericCorrection')
	
	@property
	def IndexProcessing(self): return self.__get_status('IndexProcessing')

class Status:
	__unprocessed='Unprocessed'
	
	def __init__(self,is_fallback=False):
		self.__is_fallback=is_fallback
	
	def __get_normal_status(self,out_status):
		if self.__is_fallback: return fbsm[out_status]
		else: return out_status
	
	@property
	def Unprocessed(self): return self.__get_normal_status(self.__unprocessed)
	
	unprocessed_vals=[__unprocessed,'0','',None]
	FinishedRequest='FinishedRequest'
	SearchingForCloudFreeProducts='SearchingForCloudFreeProducts'
	Error_NoOptimalProduct='Error_NoOptimalProduct'
	Error_Check_AtmosCor_ProductDoesNotExist='Error_Check_AtmosCor_ProductDoesNotExist'
	Error_Sen2Cor='Error_Sen2Cor'
	Error_DownloadResultsEmpty='Error_DownloadResultsEmpty'
	NoAvailableProducts='NoAvailableProducts'
	NoAvailableHistoricData='NoAvailableHistoricData'
	NotForProcessing='NotForProcessing'
	
	def __get_complex_status(self,prefix):
		return MainStatus(prefix,self.__is_fallback)
	
	@property
	def QueuedFor(self): return self.__get_complex_status('QueuedFor')
	
	@property
	def Running(self): return self.__get_complex_status("Running")
	
	@property
	def Finished(self): return self.__get_complex_status("Finished")
	
	@property
	def SubmittedTo(self): return self.__get_complex_status("SubmittedTo")
	
	@property
	def WaitingFinish(self): return self.__get_complex_status("WaitingFinish")
	
	@property
	def fallback_to(self):
		return Status(is_fallback=True)

image_status=Status()
fallback_status_mapper=dict()
fallback_status_mapper[image_status.Unprocessed]=['0','',
                                                  image_status.Running.Download,
                                                  image_status.QueuedFor.Download,
                                                  image_status.QueuedFor.HistoricDownload,
                                                  image_status.Running.ImageCheck,
                                                  image_status.Error_DownloadResultsEmpty,
                                                  image_status.Error_NoOptimalProduct,
                                                  image_status.NoAvailableProducts]
fallback_status_mapper[image_status.SubmittedTo.AtmosphericCorrection]=[image_status.Running.AtmosphericCorrection,
                                                                        image_status.QueuedFor.AtmosphericCorrection,
                                                                        image_status.WaitingFinish.AtmosphericCorrection]
fallback_status_mapper[image_status.SubmittedTo.IndexProcessing]=[image_status.QueuedFor.IndexProcessing,
                                                                  image_status.Running.IndexProcessing]
fallback_status_mapper[image_status.SubmittedTo.ImageCheck]=[image_status.QueuedFor.ImageCheck,
                                                             image_status.QueuedFor.Download,
                                                             image_status.Running.ImageCheck,
                                                             image_status.Running.Download,
                                                             image_status.NoAvailableProducts]
fbsm=fallback_status_mapper

def main():
	pass

if __name__=='__main__':
	main()
