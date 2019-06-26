depends = ('ITKPyBase', 'ITKMesh', 'ITKCommon', )
templates = (
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMSS2', True, 'itk::Mesh< signed short,2 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMUC2', True, 'itk::Mesh< unsigned char,2 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMUS2', True, 'itk::Mesh< unsigned short,2 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMF2', True, 'itk::Mesh< float,2 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMD2', True, 'itk::Mesh< double,2 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMSS3', True, 'itk::Mesh< signed short,3 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMUC3', True, 'itk::Mesh< unsigned char,3 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMUS3', True, 'itk::Mesh< unsigned short,3 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMF3', True, 'itk::Mesh< float,3 >'),
  ('MeshToPolyDataFilter', 'itk::MeshToPolyDataFilter', 'itkMeshToPolyDataFilterMD3', True, 'itk::Mesh< double,3 >'),
  ('PolyData', 'itk::PolyData', 'itkPolyDataSS', True, 'signed short'),
  ('PolyData', 'itk::PolyData', 'itkPolyDataUC', True, 'unsigned char'),
  ('PolyData', 'itk::PolyData', 'itkPolyDataUS', True, 'unsigned short'),
  ('PolyData', 'itk::PolyData', 'itkPolyDataF', True, 'float'),
  ('PolyData', 'itk::PolyData', 'itkPolyDataD', True, 'double'),
)
snake_case_functions = ('mesh_to_poly_data_filter', )
