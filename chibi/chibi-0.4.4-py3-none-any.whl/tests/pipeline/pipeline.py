from unittest import TestCase
from chibi.snippet import is_type
from chibi.pipeline import Pipeline
from chibi.pipeline.pipeline import Pipeline_manager
import copy

class Test_pipeline( TestCase ):

    def test_or_create_a_manager( self ):
        p1 = Pipeline()
        p2 = Pipeline()
        m = p1 | p2
        self.assertIsInstance( m, Pipeline_manager )

    def test_or_of_the_class_should_create_a_manager( self ):
        p1 = Pipeline
        p2 = Pipeline
        m = p1 | p2
        self.assertIsInstance( m, Pipeline_manager )


class Test_pipeline_manager( TestCase ):
    def test_should_no_modified_the_childen_of_the_previews_pipelines( self ):
        p1 = Pipeline()
        p2 = Pipeline()
        p3 = Pipeline()
        m1 = p1 | p2
        m2 = p3 | m1

        self.assertEqual( 3, len( m2.children ) )
        self.assertEqual( 2, len( m1.children ) )
