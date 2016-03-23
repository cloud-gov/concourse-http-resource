from helpers import cmd


def test_in(httpbin, tmpdir):
    """Test downloading versioned file."""

    source = {
        'uri': httpbin + '/range/{version}',
    }

    in_dir = tmpdir.mkdir('work_dir')

    output = cmd('in', source, [str(in_dir)], {'version': '9'})

    assert output == {'version': {'version': '9'}, 'metadata': []}

    assert in_dir.join('9').exists()
    assert len(in_dir.join('9').read()) == 9
    assert in_dir.join('version').exists()
    assert in_dir.join('version').read() == '9'

def test_in_filename(httpbin, tmpdir):
    """Test downloading versioned file with predetermined filename."""

    source = {
        'uri': httpbin + '/range/{version}',
        'filename': 'filename_{version}',
    }

    in_dir = tmpdir.mkdir('work_dir')

    output = cmd('in', source, [str(in_dir)], {'version': '9'})

    assert output == {'version': {'version': '9'}, 'metadata': []}

    assert in_dir.join('filename_9').exists()
    assert len(in_dir.join('filename_9').read()) == 9

def test_in_unversioned_filename(httpbin, tmpdir):
    """Test downloading unversioned file with predetermined filename."""

    source = {
        'uri': httpbin + '/range/9',
        'filename': 'filename',
    }

    in_dir = tmpdir.mkdir('work_dir')

    output = cmd('in', source, [str(in_dir)], {'version': '9'})

    assert output == {'version': {'version': '9'}, 'metadata': []}

    assert in_dir.join('filename').exists()
    assert len(in_dir.join('filename').read()) == 9
