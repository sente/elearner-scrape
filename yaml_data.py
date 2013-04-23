import yaml
import glob
import os
import urlparse

SOURCECODE = open('apikey.txt').read().strip()

def get_degree_status(degreeId, sourcecode):

    URI = "http://api.elearners.com/directoryws.asmx/GetDegreeStatus?sourcecode=%(sourcecode)s&degreeId=%(degreeId)s"

    url = URI % {'degreeId': degreeId, 'sourcecode': sourcecode}
    return url



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
    dataset = []
    for file in files:
        stream = open(file)
        data = yaml.load(open(file, "r"))
        dataset.append(data)
    return dataset


def process_yaml_record(data):
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

    for yaml_obj in yaml_objects:
        # yaml_obj represents a single file, which contains 1 or more top level
        # 'college' blocks

        programs = process_yaml_record(yaml_obj)

        for p in programs:

            print p['college']
            print p['program']
            print p['url']
            print p['degID']



#        print len(yaml_obj)
#        print len(d), len(process_yaml_record(d))
#        foo = process_yaml_record(d)



#    for d in dataset:
#        print len(d)
#        for record in d
#            print process_yaml_record(record)
#            for records in process_yaml_record(d):
#            pass
#            print records
#            print '\n'
#            print len(records)
#            for r in records:
#                print(type(r))
#            for record in records:
#                print record['college']


