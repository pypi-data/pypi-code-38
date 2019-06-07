depends = ('ITKPyBase', 'ITKImageIntensity', 'ITKFiniteDifference', 'ITKCurvatureFlow', )
templates = (
  ('BandNode', 'itk::BandNode', 'itkBandNodeI2SS', False, 'itk::Index<2>, signed short'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI2UC', False, 'itk::Index<2>, unsigned char'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI2US', False, 'itk::Index<2>, unsigned short'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI2F', False, 'itk::Index<2>, float'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI3SS', False, 'itk::Index<3>, signed short'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI3UC', False, 'itk::Index<3>, unsigned char'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI3US', False, 'itk::Index<3>, unsigned short'),
  ('BandNode', 'itk::BandNode', 'itkBandNodeI3F', False, 'itk::Index<3>, float'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI2SS', True, 'itk::BandNode< itk::Index<2>, signed short>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI2UC', True, 'itk::BandNode< itk::Index<2>, unsigned char>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI2US', True, 'itk::BandNode< itk::Index<2>, unsigned short>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI2F', True, 'itk::BandNode< itk::Index<2>, float>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI3SS', True, 'itk::BandNode< itk::Index<3>, signed short>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI3UC', True, 'itk::BandNode< itk::Index<3>, unsigned char>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI3US', True, 'itk::BandNode< itk::Index<3>, unsigned short>'),
  ('NarrowBand', 'itk::NarrowBand', 'itkNarrowBandBNI3F', True, 'itk::BandNode< itk::Index<3>, float>'),
  ('NarrowBandImageFilterBase', 'itk::NarrowBandImageFilterBase', 'itkNarrowBandImageFilterBaseIF2IF2', True, 'itk::Image< float,2 >, itk::Image< float,2 >'),
  ('NarrowBandImageFilterBase', 'itk::NarrowBandImageFilterBase', 'itkNarrowBandImageFilterBaseIF3IF3', True, 'itk::Image< float,3 >, itk::Image< float,3 >'),
)
snake_case_functions = ('narrow_band_image_filter_base', )
