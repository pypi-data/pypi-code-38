depends = ('ITKPyBase', 'ITKImageIntensity', 'ITKImageGrid', )
templates = (
  ('TimeVaryingVelocityFieldTransform', 'itk::TimeVaryingVelocityFieldTransform', 'itkTimeVaryingVelocityFieldTransformD2', True, 'double,2'),
  ('TimeVaryingVelocityFieldTransform', 'itk::TimeVaryingVelocityFieldTransform', 'itkTimeVaryingVelocityFieldTransformD3', True, 'double,3'),
  ('BSplineExponentialDiffeomorphicTransform', 'itk::BSplineExponentialDiffeomorphicTransform', 'itkBSplineExponentialDiffeomorphicTransformD2', True, 'double,2'),
  ('BSplineExponentialDiffeomorphicTransform', 'itk::BSplineExponentialDiffeomorphicTransform', 'itkBSplineExponentialDiffeomorphicTransformD3', True, 'double,3'),
  ('BSplineSmoothingOnUpdateDisplacementFieldTransform', 'itk::BSplineSmoothingOnUpdateDisplacementFieldTransform', 'itkBSplineSmoothingOnUpdateDisplacementFieldTransformD2', True, 'double,2'),
  ('BSplineSmoothingOnUpdateDisplacementFieldTransform', 'itk::BSplineSmoothingOnUpdateDisplacementFieldTransform', 'itkBSplineSmoothingOnUpdateDisplacementFieldTransformD3', True, 'double,3'),
  ('ConstantVelocityFieldTransform', 'itk::ConstantVelocityFieldTransform', 'itkConstantVelocityFieldTransformD2', True, 'double,2'),
  ('ConstantVelocityFieldTransform', 'itk::ConstantVelocityFieldTransform', 'itkConstantVelocityFieldTransformD3', True, 'double,3'),
  ('DisplacementFieldJacobianDeterminantFilter', 'itk::DisplacementFieldJacobianDeterminantFilter', 'itkDisplacementFieldJacobianDeterminantFilterIVF22F', True, 'itk::Image< itk::Vector< float,2 >,2 >, float'),
  ('DisplacementFieldJacobianDeterminantFilter', 'itk::DisplacementFieldJacobianDeterminantFilter', 'itkDisplacementFieldJacobianDeterminantFilterIVF33F', True, 'itk::Image< itk::Vector< float,3 >,3 >, float'),
  ('DisplacementFieldTransform', 'itk::DisplacementFieldTransform', 'itkDisplacementFieldTransformD2', True, 'double,2'),
  ('DisplacementFieldTransform', 'itk::DisplacementFieldTransform', 'itkDisplacementFieldTransformD3', True, 'double,3'),
  ('GaussianExponentialDiffeomorphicTransform', 'itk::GaussianExponentialDiffeomorphicTransform', 'itkGaussianExponentialDiffeomorphicTransformD2', True, 'double,2'),
  ('GaussianExponentialDiffeomorphicTransform', 'itk::GaussianExponentialDiffeomorphicTransform', 'itkGaussianExponentialDiffeomorphicTransformD3', True, 'double,3'),
  ('GaussianSmoothingOnUpdateDisplacementFieldTransform', 'itk::GaussianSmoothingOnUpdateDisplacementFieldTransform', 'itkGaussianSmoothingOnUpdateDisplacementFieldTransformD2', True, 'double,2'),
  ('GaussianSmoothingOnUpdateDisplacementFieldTransform', 'itk::GaussianSmoothingOnUpdateDisplacementFieldTransform', 'itkGaussianSmoothingOnUpdateDisplacementFieldTransformD3', True, 'double,3'),
  ('GaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransform', 'itk::GaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransform', 'itkGaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransformD2', True, 'double,2'),
  ('GaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransform', 'itk::GaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransform', 'itkGaussianSmoothingOnUpdateTimeVaryingVelocityFieldTransformD3', True, 'double,3'),
  ('VelocityFieldTransform', 'itk::VelocityFieldTransform', 'itkVelocityFieldTransformD2', True, 'double,2'),
  ('VelocityFieldTransform', 'itk::VelocityFieldTransform', 'itkVelocityFieldTransformD3', True, 'double,3'),
)
snake_case_functions = ('displacement_field_jacobian_determinant_filter', )
