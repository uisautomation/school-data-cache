import json
from unittest import TestCase

from mock import Mock, patch, MagicMock

from cache_school_data.main import cache_school_data
from cache_school_data.settings_ansible import SCHOOL_DATA_CACHE, AWS_STORAGE_BUCKET_NAME


class Capture:
    """
    Captures an argument value from a call on a mock.
    """
    value = None

    def __eq__(self, other):
        self.value = other
        return True


class UtilsTests(TestCase):

    def test_cache_school_data(self):

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

        with patch("cache_school_data.main.contacts_client") as contacts_client:
            contacts_client.return_value = mocked_api

            with patch("cache_school_data.main.s3_client") as s3_client:
                mock = MagicMock()
                s3_client.return_value = mock

                # test
                cache_school_data()

                body_capture = Capture()

                mock.put_object.assert_called_with(
                    Body=body_capture,
                    Bucket=AWS_STORAGE_BUCKET_NAME,
                    Key=SCHOOL_DATA_CACHE,
                    ACL='public-read'
                )

                result = json.loads(body_capture.value)
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
