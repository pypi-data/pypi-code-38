depends = ('ITKPyBase', 'ITKTransform', 'ITKDisplacementField', 'ITKCommon', )
templates = (
  ('TransformFileReaderTemplate', 'itk::TransformFileReaderTemplate', 'itkTransformFileReaderTemplateF', False, 'float'),
  ('TransformFileWriterTemplate', 'itk::TransformFileWriterTemplate', 'itkTransformFileWriterTemplateF', False, 'float'),
  ('TransformIOBaseTemplate', 'itk::TransformIOBaseTemplate', 'itkTransformIOBaseTemplateF', False, 'float'),
)
snake_case_functions = ()
