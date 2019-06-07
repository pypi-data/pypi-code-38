depends = ('ITKPyBase', 'ITKSpatialObjects', 'ITKMesh', )
templates = (
  ('SpatialObjectReader', 'itk::SpatialObjectReader', 'itkSpatialObjectReader2', True, '2'),
  ('SpatialObjectReader', 'itk::SpatialObjectReader', 'itkSpatialObjectReader3', True, '3'),
  ('SpatialObjectWriter', 'itk::SpatialObjectWriter', 'itkSpatialObjectWriter2', True, '2'),
  ('SpatialObjectWriter', 'itk::SpatialObjectWriter', 'itkSpatialObjectWriter3', True, '3'),
)
snake_case_functions = ()
