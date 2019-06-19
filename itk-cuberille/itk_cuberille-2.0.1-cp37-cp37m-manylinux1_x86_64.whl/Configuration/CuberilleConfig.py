depends = ('ITKPyBase', 'ITKMesh', 'ITKImageGradient', 'ITKImageFunction', 'ITKCommon', )
templates = (
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterIF2MF2', True, 'itk::Image< float,2 >, itk::Mesh< float,2 >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterID2MD2', True, 'itk::Image< double,2 >, itk::Mesh< double,2 >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterIF3MF3', True, 'itk::Image< float,3 >, itk::Mesh< float,3 >'),
  ('CuberilleImageToMeshFilter', 'itk::CuberilleImageToMeshFilter', 'itkCuberilleImageToMeshFilterID3MD3', True, 'itk::Image< double,3 >, itk::Mesh< double,3 >'),
)
snake_case_functions = ('mesh_source', 'cuberille_image_to_mesh_filter', 'image_to_mesh_filter', )
