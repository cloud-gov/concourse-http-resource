from helpers import cmd


def test_check(httpbin):
    """Test if check returns latest version number."""

    source = {
        'index': httpbin + '/links/10',
        'regex': "href='/links/10/(?P<version>[0-9]+)'",
    }

    output = cmd('check', source)

    assert output == [{'version': '9'}]

def test_check_with_version(httpbin):
    """Test if check returns newer version numbers."""

    source = {
        'index': httpbin + '/links/10',
        'regex': "href='/links/10/(?P<version>[0-9]+)'",
    }

    version = {
        'version': '7',
    }

    output = cmd('check', source, version=version)

    assert output == [
        {'version': '8'},
        {'version': '9'},
    ]

def test_check_etag(httpbin):
    """Test if check returns latest version number."""

    source = {
      'index': httpbin + '/response-headers?Etag=abc123',
      'etag': 'true'
    }

    output = cmd('check', source)

    assert output == [{'version': 'abc123'}]

def test_check_etag_with_matching_version(httpbin):
    """Test if check returns latest version number."""

    source = {
      'index': httpbin + '/response-headers?Etag=abc123',
      'etag': 'true'
    }

    version = {
        'version': 'abc123'
    }

    output = cmd('check', source, version=version)

    assert output == []

def test_check_etag_with_different_version(httpbin):
    """Test if check returns latest version number."""

    source = {
      'index': httpbin + '/response-headers?Etag=abc123',
      'etag': 'true'
    }

    version = {
        'version': 'xyz789'
    }

    output = cmd('check', source, version=version)

    assert output == [{'version': 'abc123'}]
