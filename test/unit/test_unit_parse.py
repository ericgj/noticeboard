from hypothesis import given, settings

from main import parse_value
from test.unit.util.parse import request_examples


@given(request=request_examples())
@settings(deadline=None)
def test_(request):
    _ = parse_value(request)
    assert True
