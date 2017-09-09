import requests
import base64
import os
import sys
import logging
import json
import pprint as pp
import urllib

from . import utils


class Promote(object):
    """
    Promote allows you to interact with the Promote API.
    
    Arguments
    =========
    username: str
    apikey: str
    url: str

    Examples
    ========
    >>> p = promote.Promote("colin", "789asdf879h789a79f79sf79s", "https://sandbox.c.yhat.com/")
    >>> p.deploy("HelloModel", promoteModel, testdata=testdata, confirm=True, dry_run=False, verbose=0)
    >>> p.predict("HelloWorld", { "name": "Colin" })
    """
    def __init__(self, username, apikey, url):
        if username is None:
            raise Exception("Specify a username")

        if apikey is None:
            raise Exception("Specify a apikey")

        if url is None:
            raise Exception("Specify a url")

        self.username = username
        self.apikey = apikey
        self.url = url

        self.deployment_file = os.path.realpath(sys.argv[0])
        if not os.path.exists(self.deployment_file):
            raise Exception('The path to your deployment file does not exist: {}'.format(self.deployment_file))

        self.deployment_dir = os.path.dirname(self.deployment_file)
        if not os.path.exists(self.deployment_dir):
            raise Exception('The path to your deployment directory does not exist: {}'.format(self.deployment_dir))


    def _get_function_source_code(self):
        source = ''
        with open(self.deployment_file, 'r') as f:
            source = f.read()
        
        if 'def promoteModel(' not in source:
            raise Exception('Your model needs to implement the `promoteModel` function. Function definition does not appear in {}'.format(self.deployment_file))
        return source
    
    def _get_objects(self):
        pickle_dir = os.path.join(self.deployment_dir, 'pickles')
        if not os.path.exists(pickle_dir):
            logging.info('no pickles directory found in {}'.format(pickle_dir))
            return []
        
        objects = []
        for f in os.listdir(pickle_dir):
            with open(os.path.join(pickle_dir, f), 'rb') as fh:
                obj = fh.read()
                obj = base64.encodebytes(obj).decode('utf-8')
                objects.append(dict(name=f, value=obj))

        return objects

    def _get_requirements(self):
        requirements_file = os.path.join(self.deployment_dir, 'requirements.txt')
        if not os.path.exists(requirements_file):
            logging.info('no requirements file found in {}'.format(requirements_file))
            return ''
        
        with open(requirements_file, 'r') as f:
            requirements = f.read()
        return requirements

    def _get_helper_modules(self):
        helpers_dir = os.path.join(self.deployment_dir, 'helpers')
        if not os.path.exists(helpers_dir):
            loging.info('helpers directory does not exist: {}'.format(helpers_dir))
            return []

        helpers = []
        for filename in os.listdir(helpers_dir):
            helper_file = os.path.join(helpers_dir, filename)

            if not os.path.isfile(helper_file):
                continue

            helpers.append(dict(
                name=os.path.join('helpers', filename),
                contnet=open(helper_file, 'r').read()
            ))
        return helpers

    def _get_bundle(self, modelName):
        bundle = dict(
            modelname=modelName,
            modelName=modelName,
            language="python",
            username=self.username,
            code=None,
            objects={},
            packages=[],
            modules=[],
            image=None, # do we need this anymore?,
            reqs="",
        )

        logging.info('deploying model using file: {}'.format(self.deployment_file))

        # extract source code for function
        bundle['code'] = self._get_function_source_code()
        # get serialized objects
        bundle['objects'] = self._get_objects()
        # get requirements
        bundle['reqs'] = self._get_requirements()
        bundle['modules'] = self._get_helper_modules()

        return bundle

    def _confirm(self):
        response = raw_input("Are you sure you'd like to deploy this model? (y/N): ")
        if response.lower() != "y":
            sys.exit(0)

    def _upload_deployment(self, bundle):
        # TODO: correct this
        deployment_url = urllib.parse.urljoin(self.url, 'deploy')
        bundle = json.dumps(bundle)
        return utils.post_file(deployment_url, (self.username, self.apikey), bundle)

    def deploy(self, modelName, modelFunction, testdata, confirm=False, dry_run=False, verbose=0):
        """
        Arguments
        =========
        modelFunction
        testdata
        confirm=False
        dry_run=False
        verbose=0

        Examples
        ========
        """
        levels = {
            0: logging.WARNING,
            1: logging.INFO,
            2: logging.DEBUG,
        }
        logging.basicConfig(
            format='[%(levelname)s]: %(message)s',
            level=levels.get(verbose, logging.WARNING)
        )

        bundle = self._get_bundle(modelName)

        if confirm==True:
            self._confirm()
        
        pp.pprint(bundle)
        response = self._upload_deployment(bundle)
        return response
    
    def predict(self, modelName, data):
        # TODO: correct this
        prediction_url = urllib.parse.urljoin(self.url, os.path.join(self.username, 'model', modelName))
        headers = {
            "Content-Type": "application/json"
        }
        response = requests.post(
            url=prediction_url,
            headers=headers,
            data=data,
            auth=(self.username, self.apikey)
        )
        return response.json()
    