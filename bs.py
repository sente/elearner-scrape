import BeautifulSoup
import ConfigParser
import requests
import hashlib
import sys
import os

mappings = {}

mappings['subject'] = {}
mappings['subject']['parent_tag'] = 'subject'
mappings['subject']['keys'] = ['name','value']

mappings['degree'] = {}
mappings['degree']['parent_tag']='degree'
mappings['degree']['keys']=['id','title','id_school','description']

mappings['school'] = {}
mappings['school']['parent_tag']='school'
mappings['school']['keys']=['id','name','description','partner']


def make_json(xml,mapping):
    if len(xml) < 200 and os.path.exists(xml):
        xml = open(xml,'r').read()

    parent_tag = mapping['parent_tag']
    keys = mapping['keys']

    print '%s -> %s' % (parent_tag, ','.join(keys))
    bs = BeautifulSoup.BeautifulStoneSoup(xml)
    elements = bs.findAll(parent_tag)
    print len(elements)
    ar = []
    for i,s in enumerate(elements):
        cg = s.findAll()
        element = {}
        for el in cg:
            element[el.name] = el.text
        ar.append(element)
    return ar




def get_all_subjects():
    res = requests.post("http://api.elearners.com/directoryws.asmx/GetAllSubjects",data={'sourcecode':'5B4857'})

    xml = res.content
    bs = BeautifulSoup.BeautifulStoneSoup(xml)

    subjects = bs.findAll('subject')

    ar = []
    for i,s in enumerate(subjects):
        cg = s.findAll()
        subject = {}
        for el in cg:
            subject[el.name] = el.text
        ar.append(subject)
    return ar

def get_schools_by_code():
    res = requests.post("http://api.elearners.com/directoryws.asmx/GetAllSchoolsByCode",data={'sourcecode':'5B4857'})

    xml = res.content
    bs = BeautifulSoup.BeautifulStoneSoup(xml)

    schools = bs.findAll('school')

    ar = []
    for i,s in enumerate(schools):
        cg = s.findAll()
        school  = {}
        for el in cg:
            school[el.name] = el.text

        ar.append(school)
    return ar



def get_all_degrees_by_code(degree):
    res = requests.post("http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode",data={'sourcecode':'5B4857','Subject':degree})
    return res.content


def test_json():
    xml = open('GetAllDegreesByCode.raw').read()
    foo = make_json(xml,mappings['degree'])
    print foo

#test_json()
#
#sys.exit(0)


def getit(url):
    cachefile = 'cache/%s' % url.replace('/','_')
    if os.path.exists(cachefile):
        print 'READING\n%s\n%s\n' % (url, cachefile)
        o = open(cachefile,'r')
        content = o.read()
        o.close()
        return content
    else:
        res = requests.get(url)
        if res.status_code == 200:
            content = res.content
            o = open(cachefile,'w')
            o.write(content)
            o.close()
            print 'SAVING\n%s\n%s\n' % (url, cachefile)
            return content

        else:
            print "ERROR ERROR"
            res.content



class ELearnerAPI(object):
    apidict = {}
    xml = {}
    subjects = []

    def __init__(self):
        self.apidict['SUBJECT']=''

    def load_cfg(self, cfg_file):
        config = ConfigParser.RawConfigParser()
        config.read(cfg_file)

        self.SOURCECODE = config.get('main','SOURCECODE')
        self.apidict['SOURCECODE'] = self.SOURCECODE
        self.rawhash = {}
        self.rawlist = []

        for key,url in config.items('raw'):
            self.rawhash[key] = url
            self.rawlist.append((key,url))

    def get_raw(self):
        for tup in self.rawlist:
            key = tup[0]
            url = tup[1] % self.apidict

            print 'saving %s' % url
            content = getit(url)
            print len(content)
            self.xml[key] = content



    def get_all_subjects(self):
        content = self.xml['getallsubjects']
        soup = BeautifulSoup.BeautifulStoneSoup(content)
        self.subjects = []
        for subject in soup.findAll('subject'):
            for name in subject.find('name'):
                self.subjects.append(name)

        return self.subjects

    def get_all_degrees_by_code(self):
        subjects = self.get_all_subjects()
        for s in subjects:
            self.apidict['SUB'] = s

            url = "http://api.elearners.com/directoryws.asmx/GetAllDegreesByCode?sourcecode=%(SOURCECODE)s&subject=%(SUB)s" % self.apidict
            url = url.replace(' ','+')
            getit(url)


if __name__ == '__main__':


    #subjects = make_json('GetAllSubjects.raw',mappings['subject'])
    #schools = make_json('GetAllSchoolsByCode.raw',mappings['school'])
    #degrees = make_json('GetAllDegreesByCode.raw',mappings['degree'])

    api = ELearnerAPI();
    api.load_cfg('bs.cfg')
    api.get_raw()
    api.get_all_degrees_by_code()

