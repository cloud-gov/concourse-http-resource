#!/usr/bin/env python3

import json
import logging as log
import os
import re
import sys
import tempfile
from distutils.version import LooseVersion

import requests


class HTTPResource:
    """HTTP resource implementation."""

    def check_etag(self, source, version, response):
        """Check for new version(s) based on an etag header."""
        etag = response.headers.get('etag')

        if etag is None:
            raise Exception('Resource missing ETag')

        # With etags, there is no sense of continuity. Either the tag
        # matches or it is a new version.
        new_version = [{'version': etag}]
        if version == new_version[0]:
            new_version = []
        return new_version

    def check_regex(self, source, version, response):
        """Check for new version(s) based on a version regex."""

        regex = re.compile(source['regex'])

        # extract versions
        index_response = response.text
        versions = regex.findall(index_response)
        versions.sort(key=lambda x: LooseVersion(x))
        versions = [{'version': v} for v in versions]

        # if version is specified get only newer versions
        if version:
            current_version = version
            new_versions = versions[versions.index(current_version):]
            new_versions.pop(0)
        else:
            # otherwise only get the current version
            new_versions = [versions[-1]]

        return new_versions

    def check(self, source, version):
        """Check for new version(s)."""

        index = source['index']
        ssl_verify = source.get('ssl_verify', True)

        if isinstance(ssl_verify, bool):
            verify = ssl_verify
        elif isinstance(ssl_verify, str):
            verify = str(tempfile.NamedTemporaryFile(delete=False, prefix='ssl-').write(verify))

        # request index
        response = requests.request('GET', index, verify=verify)
        response.raise_for_status()

        # Currently supports two types of http versioning.
        # Etag-based versioning requires the site to have an 'etag'
        #  (https://en.wikipedia.org/wiki/HTTP_ETag) defined.
        # Regex-based versioning expects an index document that lists
        #  the available versions in a regex-able fashion
        if source.get('etag'):
            return self.check_etag(source, version, response)
        else:
            return self.check_regex(source, version, response)

    def in_cmd(self, target_dir, source, version):
        """Download specific version to target_dir."""

        uri = source['uri']
        file_name = source.get('filename')
        ssl_verify = source.get('ssl_verify', True)

        if isinstance(ssl_verify, bool):
            verify = ssl_verify
        elif isinstance(ssl_verify, str):
            verify = str(tempfile.NamedTemporaryFile(delete=False, prefix='ssl-').write(verify))

        # insert version number into URI
        uri = uri.format(**version)

        response = requests.get(uri, stream=True, verify=verify)
        response.raise_for_status()

        if file_name:
            file_name = file_name.format(**version)
        else:
            file_name = uri.split('/')[-1]

        file_path = os.path.join(target_dir, file_name)
        version_file_path = os.path.join(target_dir, 'version')

        with open(file_path, 'wb') as f:
            for block in response.iter_content(1024):
                print('.', end='', file=sys.stderr)
                f.write(block)
            print()

        with open(version_file_path, 'wb') as f:
            f.write(version['version'].encode())


        return {
            'version': version,
            'metadata': [],
        }

    def run(self, command_name, json_data, command_argument):
        """Parse input/arguments, perform requested command return output."""

        with tempfile.NamedTemporaryFile(delete=False, prefix=command_name + '-') as f:
            f.write(bytes(json_data, 'utf-8'))

        data = json.loads(json_data)

        # allow debug logging to console for tests
        if os.environ.get('RESOURCE_DEBUG', False) or data.get('source', {}).get('debug', False):
            log.basicConfig(level=log.DEBUG)
        else:
            logfile = tempfile.NamedTemporaryFile(delete=False, prefix='log')
            log.basicConfig(level=log.DEBUG, filename=logfile.name)
            stderr = log.StreamHandler()
            stderr.setLevel(log.INFO)
            log.getLogger().addHandler(stderr)

        log.debug('command: %s', command_name)
        log.debug('input: %s', data)
        log.debug('args: %s', command_argument)
        log.debug('environment: %s', os.environ)

        # combine source and params
        source = data.get('source', {})
        version = data.get('version', {})

        if command_name == 'check':
            response = self.check(source, version)
        elif command_name == 'in':
            response = self.in_cmd(command_argument[0], source, version)
        else:
            response = {}

        return json.dumps(response)

print(HTTPResource().run(os.path.basename(__file__), sys.stdin.read(), sys.argv[1:]))
