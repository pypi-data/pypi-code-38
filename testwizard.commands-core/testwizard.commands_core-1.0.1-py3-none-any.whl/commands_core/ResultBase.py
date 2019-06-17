class ResultBase():
    def __init__(self, success, successMessage, failMessage):
        self.success = success
        if(success):
            self.message = successMessage
        else:
            self.message = failMessage
    
    def getMessageForErrorCode(self, message, errorCode):
        return self.errorCodes(errorCode, message)

    def errorCodes(self, errorCode, message):
        return{
            11: message +": Invalid path",
            12: message +": File not found",
            13: message +": Bitmap buffer is empty\nDo 'captureReferenceBitmap()' or 'loadReferenceBitmap(filename)' first",
            14: message +": Timeout out of range",
            15: message +": Value out of range 0..100",
            16: message +": Region coordinates invalid",
            17: message +": Bitmap must have 24bpp RGB format",
            18: message +": Bitmap has the wrong size",
            19: message +": Cannot loaod bitmap",
            20: message +": Error while saving bitmap",
            21: message +": Region bitmap buffer empty\nDo 'captureReferenceBitmap()' and 'SetRegion(x, y, width, height)' first",
            22: message +": No capture engine available",
            160: message +": Error while applying filter",
            161: message +": Value out of range(-1000 to 1000)"
        }.get(errorCode,message)