depends = ('ITKPyBase', 'ITKOptimizersv4', 'ITKMetricsv4', )
templates = (
  ('ImageRegistrationMethodv4', 'itk::ImageRegistrationMethodv4', 'itkImageRegistrationMethodv4REGv4F2F2', True, 'itk::Image< float, 2 >, itk::Image< float, 2 >'),
  ('ImageRegistrationMethodv4', 'itk::ImageRegistrationMethodv4', 'itkImageRegistrationMethodv4REGv4F3F3', True, 'itk::Image< float, 3 >, itk::Image< float, 3 >'),
)
snake_case_functions = ('image_registration_methodv4', )
