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
