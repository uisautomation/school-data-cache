import json
import logging

import boto3
import os
import zeep

from cache_school_data.secrets import *

if os.environ.get('APP_ENV', 'test') == 'production':
    import cache_school_data.settings_production as settings
else:
    import cache_school_data.settings_test as settings

FORMAT = '%(levelname)s %(asctime)s %(pathname)s:%(lineno)d %(funcName)s "%(message)s"'
logging.basicConfig(level=logging.INFO, format=FORMAT)

logger = logging.getLogger('tcpserver')


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
        Bucket=settings.AWS_STORAGE_BUCKET_NAME,
        Key=settings.SCHOOL_DATA_CACHE,
        ACL='public-read'
    )
    logger.info('%s transferred to %s' % (settings.SCHOOL_DATA_CACHE, settings.AWS_STORAGE_BUCKET_NAME))


def s3_client():
    """
    :return: an AWS S3 soap client (easy to patch)
    """
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_S3_REGION_NAME
    )


def contacts_client():
    """
    :return: a Contacts API soap client
    """
    return zeep.Client(settings.CONTACTS_API_URL)


if __name__ == '__main__':
    cache_school_data()
