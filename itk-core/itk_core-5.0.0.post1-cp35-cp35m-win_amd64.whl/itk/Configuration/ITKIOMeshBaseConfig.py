depends = ('ITKPyBase', 'ITKVoronoi', 'ITKQuadEdgeMesh', 'ITKMesh', 'ITKIOImageBase', 'ITKCommon', )
templates = (
  ('MeshIOBase', 'itk::MeshIOBase', 'itkMeshIOBase', True),
  ('MeshIOFactory', 'itk::MeshIOFactory', 'itkMeshIOFactory', True),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMSS2', True, 'itk::Mesh< signed short,2 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMUC2', True, 'itk::Mesh< unsigned char,2 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMUS2', True, 'itk::Mesh< unsigned short,2 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMF2', True, 'itk::Mesh< float,2 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMD2', True, 'itk::Mesh< double,2 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMSS3', True, 'itk::Mesh< signed short,3 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMUC3', True, 'itk::Mesh< unsigned char,3 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMUS3', True, 'itk::Mesh< unsigned short,3 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMF3', True, 'itk::Mesh< float,3 >'),
  ('MeshFileReader', 'itk::MeshFileReader', 'itkMeshFileReaderMD3', True, 'itk::Mesh< double,3 >'),
  ('MeshFileWriter', 'itk::MeshFileWriter', 'itkMeshFileWriterMF2', True, 'itk::Mesh< float,2 >'),
  ('MeshFileWriter', 'itk::MeshFileWriter', 'itkMeshFileWriterMD2', True, 'itk::Mesh< double,2 >'),
  ('MeshFileWriter', 'itk::MeshFileWriter', 'itkMeshFileWriterMF3', True, 'itk::Mesh< float,3 >'),
  ('MeshFileWriter', 'itk::MeshFileWriter', 'itkMeshFileWriterMD3', True, 'itk::Mesh< double,3 >'),
)
snake_case_functions = ('mesh_file_writer', 'mesh_file_reader', )
