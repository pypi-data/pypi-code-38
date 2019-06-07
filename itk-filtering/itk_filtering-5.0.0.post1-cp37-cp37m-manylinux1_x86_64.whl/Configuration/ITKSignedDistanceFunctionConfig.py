depends = ('ITKPyBase', 'ITKImageFunction', )
templates = (
  ('ShapeSignedDistanceFunction', 'itk::ShapeSignedDistanceFunction', 'itkShapeSignedDistanceFunctionD2', True, 'double,2'),
  ('ShapeSignedDistanceFunction', 'itk::ShapeSignedDistanceFunction', 'itkShapeSignedDistanceFunctionD3', True, 'double,3'),
  ('PCAShapeSignedDistanceFunction', 'itk::PCAShapeSignedDistanceFunction', 'itkPCAShapeSignedDistanceFunctionD2IF2', True, 'double,2,itk::Image< float,2 >'),
  ('PCAShapeSignedDistanceFunction', 'itk::PCAShapeSignedDistanceFunction', 'itkPCAShapeSignedDistanceFunctionD2ID2', True, 'double,2,itk::Image< double,2 >'),
  ('PCAShapeSignedDistanceFunction', 'itk::PCAShapeSignedDistanceFunction', 'itkPCAShapeSignedDistanceFunctionD3IF3', True, 'double,3,itk::Image< float,3 >'),
  ('PCAShapeSignedDistanceFunction', 'itk::PCAShapeSignedDistanceFunction', 'itkPCAShapeSignedDistanceFunctionD3ID3', True, 'double,3,itk::Image< double,3 >'),
)
snake_case_functions = ()
