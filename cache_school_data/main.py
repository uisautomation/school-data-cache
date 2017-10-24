import json

import boto3
import zeep

from cache_school_data.secrets import *
from cache_school_data.settings_ansible import *


def cache_school_data():
    """
    This is a scheduled task that retrieves the school and department data from the Contacts API at regular intervals
    and caches the data in an S3 json file.
    """
    service = contacts_client().bind(service_name='Contacts', port_name='ContactsSoap12')
    get_schools_results = service.GetSchoolsJSON(username=RESEARCH_PORTAL_API_USERNAME,
                                                 password=RESEARCH_PORTAL_API_PASS)
    school_data = []
    for school in json.loads(get_schools_results):
        school_data.append(school)
        get_departments_results = service.GetDepartmentsJSON(username=RESEARCH_PORTAL_API_USERNAME,
                                                             password=RESEARCH_PORTAL_API_PASS,
                                                             schoolCode=school['SchoolCode'])
        school['departments'] = json.loads(get_departments_results)

    school_data_string = json.dumps(school_data)

    s3_client().put_object(
        Body=school_data_string,
        Bucket=AWS_STORAGE_BUCKET_NAME,
        Key=SCHOOL_DATA_CACHE,
        ACL='public-read'
    )
    print('FIXME')


def s3_client():
    """
    :return: an AWS S3 soap client (easy to patch)
    """
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_S3_REGION_NAME
    )


def contacts_client():
    """
    :return: a Contacts API soap client
    """
    return zeep.Client(CONTACTS_API_URL)


if __name__ == '__main__':
    cache_school_data()
