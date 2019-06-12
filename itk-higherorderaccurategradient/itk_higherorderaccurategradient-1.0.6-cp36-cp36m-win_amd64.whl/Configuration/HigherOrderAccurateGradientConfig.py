depends = ('ITKPyBase', 'ITKImageIntensity', 'ITKImageGradient', 'ITKImageFeature', 'ITKCommon', )
templates = (
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('HigherOrderAccurateDerivativeImageFilter', 'itk::HigherOrderAccurateDerivativeImageFilter', 'itkHigherOrderAccurateDerivativeImageFilterIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterIF2FF', True, 'itk::Image< float,2 >, float, float'),
  ('HigherOrderAccurateGradientImageFilter', 'itk::HigherOrderAccurateGradientImageFilter', 'itkHigherOrderAccurateGradientImageFilterIF3FF', True, 'itk::Image< float,3 >, float, float'),
)
snake_case_functions = ('higher_order_accurate_derivative_image_filter', 'higher_order_accurate_gradient_image_filter', )
