depends = ('ITKPyBase', 'ITKCommon', )
templates = (
  ('FrequencyBandImageFilter', 'itk::FrequencyBandImageFilter', 'itkFrequencyBandImageFilterICF2', True, 'itk::Image< std::complex< float >,2 >'),
  ('FrequencyBandImageFilter', 'itk::FrequencyBandImageFilter', 'itkFrequencyBandImageFilterICF3', True, 'itk::Image< std::complex< float >,3 >'),
  ('UnaryFrequencyDomainFilter', 'itk::UnaryFrequencyDomainFilter', 'itkUnaryFrequencyDomainFilterICF2', True, 'itk::Image< std::complex< float >,2 >'),
  ('UnaryFrequencyDomainFilter', 'itk::UnaryFrequencyDomainFilter', 'itkUnaryFrequencyDomainFilterICF3', True, 'itk::Image< std::complex< float >,3 >'),
)
snake_case_functions = ('frequency_band_image_filter', 'unary_frequency_domain_filter', )
