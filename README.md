# Cache School Data Application

This is a project for a scheduled task that retrieves the school and department data from the ROO Contacts API 
on a daily basis and caches the data in an S3 json file. At the writing of this README the json file is only 
consumed by the PI Dashboard.

To set up the development environment:

```bash
virtualenv -p python3 venv
. venv/bin/activate
pip install -r test-requirements.txt
```

To run the tests:

```bash
. venv/bin/activate
python -m unittest
```

To select which settings file to use:

```bash
export APP_ENV={test|production}
```

To build the docker container:

```bash
docker build -t cache-school-data .
```

To run the docker container:

```bash
docker run --name cache-school-data-$APP_ENV --rm -e "APP_ENV=$APP_ENV" cache-school-data
```
