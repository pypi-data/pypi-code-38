depends = ('ITKPyBase', 'ITKTransform', 'ITKIOImageBase', )
templates = (
  ('NiftiImageIO', 'itk::NiftiImageIO', 'itkNiftiImageIO', True),
  ('NiftiImageIOFactory', 'itk::NiftiImageIOFactory', 'itkNiftiImageIOFactory', True),
)
snake_case_functions = ()
