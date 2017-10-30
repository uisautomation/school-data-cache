import json
from unittest import TestCase

import callee
from mock import Mock, patch, MagicMock

from cache_school_data.main import cache_school_data, settings


class UtilsTests(TestCase):

    @patch('cache_school_data.main.contacts_client')
    @patch('cache_school_data.main.s3_client')
    def test_cache_school_data(self, s3_client, contacts_client):

        mocked_api = Mock()
        mocked_api.bind.return_value = mocked_api

        mocked_api.GetSchoolsJSON.return_value = """
            [{"SchoolName": "Non-School", "SchoolCode": "O"},
             {"SchoolName": "School of Arts and Humanities", "SchoolCode": "A"},
             {"SchoolName": "School of Clinical Medicine", "SchoolCode": "C"},
             {"SchoolName": "School of Technology", "SchoolCode": "T"},
             {"SchoolName": "School of the Biological Sciences", "SchoolCode": "B"},
             {"SchoolName": "School of the Humanities and Social Sciences", "SchoolCode": "H"},
             {"SchoolName": "School of the Physical Sciences", "SchoolCode": "P"}]
        """

        def side_effect(**kwargs):
            if kwargs['schoolCode'] == 'O':
                return """[
                    {"DeptCode": "GHAG", "DeptName": "Anglo Saxon, Norse and Celtic"},
                    {"DeptCode": "GCAG", "DeptName": "Architecture"},
                    {"DeptCode": "GUAG", "DeptName": "Asian and Middle Eastern Studies"}
                ]"""
            elif kwargs['schoolCode'] == 'A':
                return """[
                     {"DeptCode": "GZAG", "DeptName": "Centre for the Future of Intelligence"},
                     {"DeptCode": "GEAG", "DeptName": "Classics and Classical Archaeology"},
                     {"DeptCode": "GMAG", "DeptName": "Italian"}
                ]"""
            elif kwargs['schoolCode'] == 'C':
                return """[
                     {"DeptCode": "DCGA", "DeptName": "Kettle's Yard"},
                     {"DeptCode": "GVAG", "DeptName": "Philosophy"},
                     {"DeptCode": "GAAG", "DeptName": "School of Arts and Humanities"}
                ]"""
            return "[]"

        mocked_api.GetDepartmentsJSON.side_effect = side_effect

        contacts_client.return_value = mocked_api

        mock_s3 = MagicMock()
        s3_client.return_value = mock_s3

        # test
        cache_school_data()

        body_captor = callee.general.Captor()

        mock_s3.put_object.assert_called_with(
            Body=body_captor,
            Bucket=settings.AWS_STORAGE_BUCKET_NAME,
            Key=settings.SCHOOL_DATA_CACHE,
            ACL='public-read'
        )

        result = json.loads(body_captor.arg)
        self.assertEqual(len(result), 7)
        self.assertEqual(result[0]['SchoolCode'], 'O')
        self.assertEqual(result[0]['SchoolName'], 'Non-School')
        self.assertEqual(len(result[0]['departments']), 3)
        self.assertEqual(result[0]['departments'][0]['DeptCode'], 'GHAG')
        self.assertEqual(result[0]['departments'][0]['DeptName'], 'Anglo Saxon, Norse and Celtic')
        self.assertEqual(result[0]['departments'][2]['DeptCode'], 'GUAG')
        self.assertEqual(result[0]['departments'][2]['DeptName'], 'Asian and Middle Eastern Studies')
        self.assertEqual(result[0]['SchoolName'], 'Non-School')
        self.assertEqual(result[6]['SchoolCode'], 'P')
        self.assertEqual(result[6]['SchoolName'], 'School of the Physical Sciences')
        self.assertEqual(len(result[6]['departments']), 0)
