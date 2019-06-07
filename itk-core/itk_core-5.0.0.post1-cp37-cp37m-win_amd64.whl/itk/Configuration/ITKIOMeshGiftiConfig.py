depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (
  ('GiftiMeshIO', 'itk::GiftiMeshIO', 'itkGiftiMeshIO', True),
  ('GiftiMeshIOFactory', 'itk::GiftiMeshIOFactory', 'itkGiftiMeshIOFactory', True),
  ('MapContainer', 'itk::MapContainer', 'itkMapContainerIstring', False, 'int, std::string'),
  ('MapContainer', 'itk::MapContainer', 'itkMapContainerIRGBAF', False, 'int, itk::RGBAPixel< float >'),
)
snake_case_functions = ()
