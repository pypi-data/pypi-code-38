depends = ('ITKPyBase', 'ITKCommon', )
templates = (
  ('PyCommand', 'itk::PyCommand', 'itkPyCommand', False),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUC2IUC2', False, 'itk::Image< unsigned char,2 >, itk::Image< unsigned char,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUC3IUC3', False, 'itk::Image< unsigned char,3 >, itk::Image< unsigned char,3 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUS2IUS2', False, 'itk::Image< unsigned short,2 >, itk::Image< unsigned short,2 >'),
  ('PyImageFilter', 'itk::PyImageFilter', 'itkPyImageFilterIUS3IUS3', False, 'itk::Image< unsigned short,3 >, itk::Image< unsigned short,3 >'),
)
snake_case_functions = ('py_image_filter', )
