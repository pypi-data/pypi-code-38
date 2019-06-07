depends = ('ITKPyBase', 'ITKTransform', 'ITKOptimizers', 'ITKImageGrid', 'ITKDisplacementField', 'ITKCommon', )
templates = (
  ('GradientDescentOptimizerBasev4Template', 'itk::GradientDescentOptimizerBasev4Template', 'itkGradientDescentOptimizerBasev4TemplateD', False, 'double'),
  ('GradientDescentOptimizerBasev4Template', 'itk::GradientDescentOptimizerBasev4Template', 'itkGradientDescentOptimizerBasev4TemplateF', False, 'float'),
  ('GradientDescentOptimizerv4Template', 'itk::GradientDescentOptimizerv4Template', 'itkGradientDescentOptimizerv4TemplateD', False, 'double'),
  ('GradientDescentOptimizerv4Template', 'itk::GradientDescentOptimizerv4Template', 'itkGradientDescentOptimizerv4TemplateF', False, 'float'),
  ('ObjectToObjectMetric', 'itk::ObjectToObjectMetric', 'itkObjectToObjectMetric22', True, '2,2'),
  ('ObjectToObjectMetric', 'itk::ObjectToObjectMetric', 'itkObjectToObjectMetric33', True, '3,3'),
  ('ObjectToObjectMetricBaseTemplate', 'itk::ObjectToObjectMetricBaseTemplate', 'itkObjectToObjectMetricBaseTemplateD', False, 'double'),
  ('ObjectToObjectMetricBaseTemplate', 'itk::ObjectToObjectMetricBaseTemplate', 'itkObjectToObjectMetricBaseTemplateF', False, 'float'),
  ('ObjectToObjectOptimizerBaseTemplate', 'itk::ObjectToObjectOptimizerBaseTemplate', 'itkObjectToObjectOptimizerBaseTemplateF', False, 'float'),
  ('ObjectToObjectOptimizerBaseTemplate', 'itk::ObjectToObjectOptimizerBaseTemplate', 'itkObjectToObjectOptimizerBaseTemplateD', False, 'double'),
  ('OptimizerParameterScalesEstimatorTemplate', 'itk::OptimizerParameterScalesEstimatorTemplate', 'itkOptimizerParameterScalesEstimatorTemplateD', False, 'double'),
  ('OptimizerParameterScalesEstimatorTemplate', 'itk::OptimizerParameterScalesEstimatorTemplate', 'itkOptimizerParameterScalesEstimatorTemplateF', False, 'float'),
  ('QuasiNewtonOptimizerv4Template', 'itk::QuasiNewtonOptimizerv4Template', 'itkQuasiNewtonOptimizerv4TemplateF', False, 'float'),
  ('RegularStepGradientDescentOptimizerv4', 'itk::RegularStepGradientDescentOptimizerv4', 'itkRegularStepGradientDescentOptimizerv4D', True, 'double'),
  ('RegularStepGradientDescentOptimizerv4', 'itk::RegularStepGradientDescentOptimizerv4', 'itkRegularStepGradientDescentOptimizerv4F', True, 'float'),
  ('SingleValuedCostFunctionv4Template', 'itk::SingleValuedCostFunctionv4Template', 'itkSingleValuedCostFunctionv4TemplateD', False, 'double'),
  ('SingleValuedCostFunctionv4Template', 'itk::SingleValuedCostFunctionv4Template', 'itkSingleValuedCostFunctionv4TemplateF', False, 'float'),
)
snake_case_functions = ()
