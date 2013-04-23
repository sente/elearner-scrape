# -*- coding: utf-8 -*-
import BeautifulSoup
import urlparse
import requests
import pprint
import yaml
import glob
import os


sourcecode = open('apikey.txt').read().strip()


def get_degree_status(degreeId):
    """
    return True, False or None (if the api call fails for some reason)
    for a given degreeId.
    """ 

    global sourcecode

    URI = "http://api.elearners.com/directoryws.asmx/GetDegreeStatus?sourcecode=%(sourcecode)s&degreeId=%(degreeId)s"

    url = URI % {'degreeId': degreeId, 'sourcecode': sourcecode}
    resp = requests.get(url)

    if resp.status_code == 200:
        # resp.content should look something like:
        #   <?xml version="1.0" encoding="utf-8"?>
        #   <boolean xmlns="http://elearners.com/">true</boolean>

        soup = BeautifulSoup.BeautifulStoneSoup(resp.content)
        txt = soup.find('boolean').getText()

        if txt == 'true':
            return True
        elif txt == 'false':
            return False
    else:
        return None



def get_query_args(url):
    """
    given a url like: 
        http://nursingdegreesguide.elearners.com/cu.htm?&degID=10268&foo=bar
    returns a dictionary:
        {'degID': 10268, 'foo': 'bar'}
    """

    return dict(urlparse.parse_qsl(url))


def find_yaml_files(path):
    """
    recursively search the filesystem starting at <path>
    for any '*.yaml' files, return an array of all *.yaml
    files that were found
    """

    yaml_files = []
    for (root,dir,files) in os.walk('./'):
        for f in files:
            if f.endswith('.yaml'):
                full_filepath = os.path.join(root,f)
                yaml_files.append(full_filepath)

    return yaml_files



def parse_yaml_files(files):
    """
    input: a list of YAML files
    output: a list of data, as parsed from the YAML files
    """

    dataset = []
    for file in files:
        stream = open(file)
        data = yaml.load(open(file, "r"))
        dataset.append(data)
    return dataset


def process_yaml_data(data):
    """
    processes a YAML file and returns an array of 'program' hashes filtering
    out all programs which have 'hide: true' set at the program level or at the
    parent (college) level.


        capella-university:
           name:  Capella University
           image: http://www.nursingdegreeguide.com/images/logos/online-colleges-logo-cu.png
           accreditation: CCNE accredited
           programs:
             - name: MSN - Nurse Educator
               url: http://nursingdegreesguide.elearners.com/cu.htm?&degID=11629
               hide: false
             - name: MSN - Gerontology
               url: http://nursingdegreesguide.elearners.com/cu.htm?&degID=14779
               hide: false
             - name: PhD - Nursing Education
               url: http://nursingdegreesguide.elearners.com/cu.htm?&degID=10268
               hide: false
           note:
           hide: false
    """

    res = []
    for college, cdata in data.items():
        if cdata.get('hide'):
            pass
        else:
            for pdata in cdata.get('programs', []):
                if pdata.get('hide'):
                    pass
                else:

                    url = pdata.get('url')
                    program = pdata.get('name')
                    degID = get_query_args(url)['degID']

                    record = {'college': college,
                              'program': program,
                              'url': url,
                              'degID': degID}

                    res.append(record)
    return res

if __name__ == '__main__':
    yaml_files = find_yaml_files('./')
    yaml_objects = parse_yaml_files(yaml_files)
    # yaml_objects is an array, each array element contains one YAML files'
    # worth of data

    for yaml_obj in yaml_objects:
        # A single YAML file might contain multiple colleges, each with
        # multiple degrees, or it may contain only a single college with one
        # degree.

        degrees = process_yaml_data(yaml_obj)

        # TODO: Some cleanup and then SEND EMAIL to Dale

        for degree in degrees:

            degree_status = get_degree_status(degree['degID'])
            print [degree_status, degree['college'], degree['program']]









        # note: there could be more than one degree per college, and more than
        # one college per yaml_obj.  example 'degrees' list:
        #   [
        #     {
        #       "url": "http://nursingdegreesguide.elearners.com/drx.htm?&degID=8211",
        #       "program": "Post-Bachelor Certificate - Nursing Ed & Faculty",
        #       "college": "drexel-university-online",
        #       "degID": "8211"
        #     },
        #     {
        #       "url": "http://nursingdegreesguide.elearners.com/drx.htm?&degID=8212",
        #       "program": "Post-Bachelor Certificate - Innovation Adv Nursing",
        #       "college": "drexel-university-online",
        #       "degID": "8212"
        #     },
        #     {
        #       "url": "http://nursingdegreesguide.elearners.com/chap.htm?&degID=13844",
        #       "program": "Certificate - Mother-Baby",
        #       "college": "brandman-university",
        #       "degID": "13844"
        #     }
        #   ]



