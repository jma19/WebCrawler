import logging

import requests
from datamodel.search.datamodel import ProducedLink, OneUnProcessedGroup, robot_manager
from spacetime_local.IApplication import IApplication
from spacetime_local.declarations import Producer, GetterSetter, Getter
# from lxml import html,etree
import re, os
from time import time
import url_utils

try:
    # For python 2
    from urlparse import urlparse, parse_qs
except ImportError:
    # For python 3
    from urllib.parse import urlparse, parse_qs

logger = logging.getLogger(__name__)
LOG_HEADER = "[CRAWLER]"
url_count = (set()
             if not os.path.exists("successful_urls.txt") else
             set([line.strip() for line in open("successful_urls.txt").readlines() if line.strip() != ""]))
MAX_LINKS_TO_DOWNLOAD = 3000

TRAP_POOL = {"calendar.ics.uci.edu", "drzaius.ics.uci.edu/cgi-bin/cvsweb.cgi/", "flamingo.ics.uci.edu/releases/"
    , "fano.ics.uci.edu/", "ironwood.ics.uci.edu", "djp3-pc2.ics.uci.edu/LUCICodeRepository/",
             "archive.ics.uci.edu/ml", "www.ics.uci.edu/~xhx/project/MotifMap/"}


#
#
# http://calendar.ics.uci.edu
# https://duttgroup.ics.uci.edu/
# http://djp3-pc2.ics.uci.edu/LUCICodeRepository/
# https://archive.ics.uci.edu/ml/datasets.html
# http://drzaius.ics.uci.edu/cgi-bin/cvsweb.cgi/
# http://flamingo.ics.uci.edu/releases/
# http://fano.ics.uci.edu/ca/
# http://ironwood.ics.uci.edu/
# http:www.ics.uci.edu/~xhx/project/MotifMap/

@Producer(ProducedLink)
@GetterSetter(OneUnProcessedGroup)
class CrawlerFrame(IApplication):
    def __init__(self, frame):
        self.starttime = time()
        # Set app_id <student_id1>_<student_id2>...
        self.app_id = "29846938_35888463_47927446"
        # Set user agent string to IR W17 UnderGrad <student_id1>, <student_id2> ...
        # If Graduate studetn, change the UnderGrad part to Grad.
        self.UserAgentString = "IR W17 Grad 29846938,35888463,47927446"

        self.frame = frame
        assert (self.UserAgentString != None)
        assert (self.app_id != "")
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def initialize(self):
        self.count = 0
        l = ProducedLink("http://www.ics.uci.edu", self.UserAgentString)
        print l.full_url
        self.frame.add(l)

    def update(self):
        for g in self.frame.get(OneUnProcessedGroup):
            print "Got a Group"
            outputLinks, urlResps = process_url_group(g, self.UserAgentString)
            for urlResp in urlResps:
                if urlResp.bad_url and self.UserAgentString not in set(urlResp.dataframe_obj.bad_url):
                    urlResp.dataframe_obj.bad_url += [self.UserAgentString]
            for l in outputLinks:
                if is_valid(l) and robot_manager.Allowed(l, self.UserAgentString):
                    lObj = ProducedLink(l, self.UserAgentString)
                    self.frame.add(lObj)
        if len(url_count) >= MAX_LINKS_TO_DOWNLOAD:
            self.done = True

    def shutdown(self):
        print "downloaded ", len(url_count), " in ", time() - self.starttime, " seconds."
        pass


def save_count(urls):
    global url_count
    urls = set(urls).difference(url_count)
    url_count.update(urls)
    if len(urls):
        with open("successful_urls.txt", "a") as surls:
            surls.write(("\n".join(urls) + "\n").encode("utf-8"))


def process_url_group(group, useragentstr):
    rawDatas, successfull_urls = group.download(useragentstr, is_valid)
    save_count(successfull_urls)
    return extract_next_links(rawDatas), rawDatas


def save_extract_links(urls):
    global url_count
    url_count += len(urls)
    with open("successful_extracts.txt", "a") as surls:
        surls.write("\n".join(urls) + "\n")


#######################################################################################
'''
STUB FUNCTIONS TO BE FILLED OUT BY THE STUDENT.
'''


def extract_next_links(rawDatas):
    '''
        rawDatas is a list of objs -> [raw_content_obj1, raw_content_obj2, ....]
        Each obj is of type UrlResponse  declared at L28-42 datamodel/search/datamodel.py
        the return of this function should be a list of urls in their absolute form
        Validation of link via is_valid function is done later (see line 42).
        It is not required to remove duplicates that have already been downloaded.
        The frontier takes care of that.

        Suggested library: lxml
        '''

    outputLinks = list()

    # rawData is tupe
    for ele in rawDatas:
        if ele.http_code != 200 or (ele.error_message != None and ele.error_message != '') or ele.is_redirected:
            ele.bad_url = True
            continue
        ele.bad_url = False
        originUrl = ele.url
        parse_result = urlparse(originUrl)

        # extractLinkFromPage()
        stack = url_utils.getPathStack(parse_result.path)
        links = url_utils.extractLinkFromPage(ele.content, parse_result.scheme, parse_result.netloc, stack, originUrl)
        print "extract page get links size: %s" % len(links)
        for lnk in links:
            ele.out_links.add(lnk)
            if is_valid(lnk):
                print "----------- valid %s" % lnk
                outputLinks.append(lnk)

    print "return output links %d" % len(outputLinks)
    return outputLinks


def splitIntoAbs(url):
    url.split("/..")


def is_valid(url):
    '''
    Function returns True or False based on whether the url has to be downloaded or not.
    Robot rules and duplication rules are checked separately.

    This is a great place to filter out crawler traps.
    '''
    # check trap
    for trap in TRAP_POOL:
        if url.__contains__(trap):
            return False

    parsed = urlparse(url)
    path = parsed.path
    split = path.split('.php')
    if len(split) > 2:
        return False

    # filter out dynamatic request url
    if (path.__contains__('.php') and path.__contains__('?')) or (
        path.__contains__('.php') and not path.endswith('.php')):
        return False

    if parsed.scheme not in set(["http", "https"]):
        return False

    # only consider 200, and
    # head = requests.head(url)
    # if head.status_code != 200:
    #     return False
    # build frequency map for path to filter
    # http://www.ics.uci.edu/prospective/en/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/contact/student-affairs/%E2%80%8B
    try:
        return ".ics.uci.edu" in parsed.hostname \
               and not re.match(".*\.(css|js|bmp|gif|jpe?g|ico" + "|png|tiff?|mid|mp2|mp3|mp4" \
                                + "|wav|avi|mov|mpeg|ram|m4v|mkv|ogg|ogv|pdf" \
                                + "|ps|eps|tex|ppt|pptx|doc|docx|xls|xlsx|names|data|dat|exe|bz2|tar|msi|bin|7z|psd|dmg|iso|epub|dll|cnf|tgz|sha1" \
                                + "|thmx|mso|arff|rtf|jar|csv" \
                                + "|rm|smil|wmv|swf|wma|zip|rar|gz" \
                                  "|war|au|apk|db|Z|java|c|py|lif|pov|bib|shar|txt)$",
                                parsed.path.lower()) \
            # and not re.match(".*[\\?@=].*", parsed.path.lower)

    except TypeError:
        print ("TypeError for ", parsed)

        #
        # test = set(['http://www.ics.uci.edu/ugrad/policies/Add_Drop_ChangeOption', 'http://www.ics.uci.edu/bin/pdf/grad/F16-17%20Graduate%20Student%20Handbook.pdf', 'http://www.ics.uci.edu/involved/leadership_council', 'http://www.ics.uci.edu/faculty/centers/', 'http://www.ics.uci.edu/community/alumni/', 'http://www.ics.uci.edu/prospective', 'http://www.webstandards.org/upgrade/', 'http://calendar.ics.uci.edu/calendar.php', 'http://www.ics.uci.edu/about/search/search_graduate_all.php', 'http://www.ics.uci.edu/ugrad/degrees/Minors', 'http://www.ics.uci.edu/community/events/competition/', 'http://www.ics.uci.edu/grad/courses/index', 'https://ucirvine-csm.symplicity.com/index.php/pid700104', 'http://www.uci.edu/', 'http://www.ics.uci.edu/about/brenhall/index.php', 'http://www.ics.uci.edu/ugrad/QA_Graduation', 'http://www.ics.uci.edu/ugrad/index', 'http://www.ics.uci.edu/faculty/highlights/', 'http://www.ics.uci.edu/ugrad/degrees/index.php', 'http://www.ics.uci.edu/community/scholarships/index', 'http://www.ics.uci.edu/grad/funding/index', 'http://www.ics.uci.edu/grad/index', 'http://www.ics.uci.edu/ugrad/', 'http://www.ics.uci.edu/grad/degrees/index', 'http://www.ics.uci.edu/about/about_deanmsg.php', 'http://www.ics.uci.edu/ugrad/policies/Laptop_ComputerUse', 'http://www.stat.uci.edu', 'http://www.ics.uci.edu/about/about_factsfigures.php', 'http://www.ics.uci.edu/grad/resources', 'http://www.ics.uci.edu/faculty/area/', 'http://www.ics.uci.edu/about/search/index.php', 'http://www.ics.uci.edu/computing/account/new', 'http://www.ics.uci.edu/ugrad/QA_Petitions', 'http://www.ics.uci.edu/ugrad/sao/index', 'http://www.ics.uci.edu/community/news/press/', 'http://www.ics.uci.edu/ugrad/policies/Academic_Standing', 'http://www.ics.uci.edu/grad/admissions/Prospective_ApplicationProcess.php', 'http://www.uci.edu/copyright.php', 'http://www.ics.uci.edu/ugrad/sao/SAO_Events.php', 'http://www.ics.uci.edu/about/visit/index.php', 'http://www.ics.uci.edu/involved/', 'http://www.ics.uci.edu/about/equity/', 'http://www.ics.uci.edu/', 'http://www.ics.uci.edu/dept/', 'http://www.ics.uci.edu/about/annualreport/', 'http://www.uci.edu/cgi-bin/phonebook', 'http://www.ics.uci.edu/grad/forms/index', 'http://www.cs.uci.edu', 'http://www.ics.uci.edu//', 'http://www.ics.uci.edu/community/news/', 'http://www.ics.uci.edu/ugrad/policies/Course_Outside_UCI', 'http://www.ics.uci.edu/ugrad/resources/index', 'http://www.ics.uci.edu/faculty/', 'http://www.ics.uci.edu/involved/corporate_partner', 'http://www.ics.uci.edu/about/visit/index', 'http://www.ics.uci.edu/grad/policies/index', 'http://www.ics.uci.edu/about/', 'http://www.ics.uci.edu/about/about_contact.php', 'http://www.informatics.uci.edu', 'http://www.ics.uci.edu/ugrad/policies/Academic_Integrity', 'http://www.uadv.uci.edu/DonaldBrenSchoolOfICSAnnualGiving', 'http://www.ics.uci.edu/ugrad/policies/Grade_Options', 'http://www.ics.uci.edu/ugrad/policies/Withdrawal_Readmission', 'http://intranet.ics.uci.edu/', 'http://www.ics.uci.edu/grad/admissions/index', 'http://www.ics.uci.edu/ugrad/courses/index', 'http://www.ics.uci.edu/involved/project_class'])
        #
        # for ele in test:
        #     print is_valid(ele)
        # u'http://www.ics.uci.edu/spring-2007/'
        # u'http://www.ics.uci.edu/index.html'

        # print is_valid("http://www.ics.uci.edu/spring-2007/")

        #

