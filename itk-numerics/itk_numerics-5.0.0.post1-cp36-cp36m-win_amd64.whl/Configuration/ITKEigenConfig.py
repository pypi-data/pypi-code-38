depends = ('ITKPyBase', 'ITKImageFilterBase', )
templates = (
  ('EigenAnalysis2DImageFilter', 'itk::EigenAnalysis2DImageFilter', 'itkEigenAnalysis2DImageFilterIF2IF2IVF22', True, 'itk::Image< float,2 >, itk::Image< float,2 >, itk::Image< itk::Vector< float,2 >,2 >'),
  ('EigenAnalysis2DImageFilter', 'itk::EigenAnalysis2DImageFilter', 'itkEigenAnalysis2DImageFilterIF2IF2IVF32', True, 'itk::Image< float,2 >, itk::Image< float,2 >, itk::Image< itk::Vector< float,3 >,2 >'),
  ('EigenAnalysis2DImageFilter', 'itk::EigenAnalysis2DImageFilter', 'itkEigenAnalysis2DImageFilterIF2IF2IVF42', True, 'itk::Image< float,2 >, itk::Image< float,2 >, itk::Image< itk::Vector< float,4 >,2 >'),
)
snake_case_functions = ('eigen_analysis2_d_image_filter', )
