from unittest import TestCase

from stackifyapm.utils.disttracing import TraceParent


class TraceParentTest(TestCase):
    def test_should_successfully_create_trace_parent(self):
        version = 1
        trace_id = 234
        span_id = 567

        trace_parent = TraceParent(version, trace_id, span_id)

        assert trace_parent.version == version
        assert trace_parent.trace_id == trace_id
        assert trace_parent.span_id == span_id

    def test_from_string_should_return_trace_parent(self):
        traceparent_string = '1-234-567'

        trace_parent = TraceParent.from_string(traceparent_string)

        assert trace_parent is not None
        assert isinstance(trace_parent, TraceParent)

    def test_from_string_given_invalid_params(self):
        traceparent_string = ''

        trace_parent = TraceParent.from_string(traceparent_string)

        assert trace_parent is None

    def test_from_string_if_version_is_not_numirical(self):
        traceparent_string = 'version-234-567'

        trace_parent = TraceParent.from_string(traceparent_string)

        assert trace_parent is None

    def test_from_string_should_raise_exception_if_version_is_255(self):
        traceparent_string = '99.5-234-567'

        trace_parent = TraceParent.from_string(traceparent_string)

        assert trace_parent is None
