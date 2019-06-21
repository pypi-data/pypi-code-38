class ImageValidator():
    def validate_file_format(self, file_path: str, file_format: str) -> bool:
        """
        Validates the image's format with the file_format.
        
        Parameters
        ----------
        file_path : str
            path to the file.
        file_format : str
            the file format that will be used for the validation. (e.g. 'jpg', 'tiff')
        
        Returns
        -------
        result : bool
            Return True when it passes the validation, or False
        """
        pass

    def validate_resolution(self, file_path: str, resolution: Tuple[int, int]) -> bool:
        """
        Validates the image's resolution.
        
        Parameters
        ----------
        file_path : str
            path to the file.
        resolution : Tuple[int, int]
            Tuple of the resolution. (e.g. (300, 300))
        
        Returns
        -------
        result : bool
            Return True when it passes the validation, or False
        """
        pass

    def validate_grayscale(self, file_path: str, error_threashold: int) -> bool:
        """
        Validates whether the image is grayscale or not.
        
        Parameters
        ----------
        file_path : str
            Path to the file.
        error_threashold : int
            Error threshold to control the strictness of the validation.
            When threshold is 0, it means every pixel must be grayscale.
        
        Returns
        -------
        result : bool
            Return True when it passes the validation, or False
        """
        pass

