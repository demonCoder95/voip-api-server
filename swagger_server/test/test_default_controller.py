# coding: utf-8

from __future__ import absolute_import

from flask import json
from six import BytesIO

from swagger_server.models.cdr import CDR  # noqa: E501
from swagger_server.test import BaseTestCase


class TestDefaultController(BaseTestCase):
    """DefaultController integration test stubs"""

    def test_calls_cdr_id_get(self):
        """Test case for calls_cdr_id_get

        Return a list of Call Data Records (CDRs).
        """
        response = self.client.open(
            '/calls/{cdr-id}'.format(cdr_id=2),
            method='GET')
        self.assert200(response,
                       'Response body is : ' + response.data.decode('utf-8'))


if __name__ == '__main__':
    import unittest
    unittest.main()
