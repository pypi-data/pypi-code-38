depends = ('ITKPyBase', 'ITKCommon', )
templates = (
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIVF22IF2', True, 'itk::Image< itk::Vector< float,2 >,2 >, itk::Image< float,2 >'),
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIVF33IF3', True, 'itk::Image< itk::Vector< float,3 >,3 >, itk::Image< float,3 >'),
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIRGBUC2IUC2', True, 'itk::Image< itk::RGBPixel< unsigned char >,2 >, itk::Image< unsigned char,2 >, 3'),
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIRGBAUC2IUC2', True, 'itk::Image< itk::RGBAPixel< unsigned char >,2 >, itk::Image< unsigned char,2 >, 4'),
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIRGBUC3IUC3', True, 'itk::Image< itk::RGBPixel< unsigned char >,3 >, itk::Image< unsigned char,3 >, 3'),
  ('SplitComponentsImageFilter', 'itk::SplitComponentsImageFilter', 'itkSplitComponentsImageFilterIRGBAUC3IUC3', True, 'itk::Image< itk::RGBAPixel< unsigned char >,3 >, itk::Image< unsigned char,3 >, 4'),
)
snake_case_functions = ('split_components_image_filter', )
