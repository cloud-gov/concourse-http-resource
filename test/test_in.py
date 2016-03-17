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
