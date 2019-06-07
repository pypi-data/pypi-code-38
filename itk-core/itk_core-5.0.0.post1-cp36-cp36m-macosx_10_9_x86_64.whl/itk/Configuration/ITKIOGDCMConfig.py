depends = ('ITKPyBase', 'ITKIOImageBase', )
templates = (
  ('GDCMImageIO', 'itk::GDCMImageIO', 'itkGDCMImageIO', True),
  ('GDCMImageIOFactory', 'itk::GDCMImageIOFactory', 'itkGDCMImageIOFactory', True),
  ('GDCMSeriesFileNames', 'itk::GDCMSeriesFileNames', 'itkGDCMSeriesFileNames', True),
)
snake_case_functions = ('gdcm_series_file_names', )
