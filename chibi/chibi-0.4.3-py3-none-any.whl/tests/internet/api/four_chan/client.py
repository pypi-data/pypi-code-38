import datetime
from unittest import TestCase, skip
from chibi.internet.api.four_chan.client import Board
from chibi.internet.api.four_chan.endpoints import Thread
from chibi.internet.api.four_chan import w, wallpaper
from chibi.api.endpoint import Endpoint
from vcr_unittest import VCRTestCase


class Test_threads( VCRTestCase ):
    def test_endpoint_for_threads_should_point_to_wallpapers( self ):
        self.assertEqual(
            w.thread_endpoint.assigned_url,
            'http://a.4cdn.org/w/threads.json' )

    def test_should_get_threads_from_wallpapers( self ):
        response = w.threads()
        self.assertEqual( response.status_code, 200 )
        native_response = response.native
        for thread in native_response:
            self.assertIsInstance( thread, Thread )
            self.assertEqual( thread.parameters[ 'board' ], 'w' )
            self.assertIsInstance( thread.parameters[ 'thread_number' ], int )
            self.assertIsInstance(
                thread.parameters[ 'last_modified' ], datetime.datetime )


    def test_each_tread_should_get_the_post( self ):
        response = w.threads()
        self.assertEqual( response.status_code, 200 )
        native_response = response.native
        for thread in native_response[:5]:
            thread_response = thread.get()
            for post in thread_response.native:
                self.assertIsInstance( post.time, datetime.datetime )
                if post.has_image:
                    self.assertIsInstance( post.image_url, Endpoint )
                else:
                    self.assertIsNone( post.image_url )
