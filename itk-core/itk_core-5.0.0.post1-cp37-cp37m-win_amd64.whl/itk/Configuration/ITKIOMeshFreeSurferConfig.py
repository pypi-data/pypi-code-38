depends = ('ITKPyBase', 'ITKMesh', 'ITKIOMeshBase', 'ITKCommon', )
templates = (
  ('FreeSurferAsciiMeshIO', 'itk::FreeSurferAsciiMeshIO', 'itkFreeSurferAsciiMeshIO', True),
  ('FreeSurferAsciiMeshIOFactory', 'itk::FreeSurferAsciiMeshIOFactory', 'itkFreeSurferAsciiMeshIOFactory', True),
  ('FreeSurferBinaryMeshIO', 'itk::FreeSurferBinaryMeshIO', 'itkFreeSurferBinaryMeshIO', True),
  ('FreeSurferBinaryMeshIOFactory', 'itk::FreeSurferBinaryMeshIOFactory', 'itkFreeSurferBinaryMeshIOFactory', True),
)
snake_case_functions = ()
