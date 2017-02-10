import re
from urlparse import urlparse

import requests

tup = [('physics', "saas"), ('chemistry', "ascas")]

for ele in tup:
    print ele[1]



a = set()
a.add(1)

print  a.__contains__(1)

parsed = urlparse("http://calendar.ics.uci.edu/download.php?calendar=1&category=&fromDate=2017-01-13&toDate=2017-01-13")
print parsed.hostname

head = requests.head("http://calendar.ics.uci.edu/download.php?calendar=1&category=&fromDate=2017-01-13&toDate=2017-01-13")

print head.status_code == 200

a = {"acj", "ascds", "cdcn"}

# page = "http://www.ics.uci.edu/about/visit/index/faculty/" \
#        ">Faculty</a>/grad/policies/index">Policies</a>/grad/policies/index">Policies</a>/grad/forms/index.php"
#
# links = re.findall('"((http|https)s?://.*?)"', page)

TRAP_URL = {"calendar.ics.uci.edu", "drzaius.ics.uci.edu/cgi-bin/cvsweb.cgi/", "flamingo.ics.uci.edu/releases/"
    , "fano.ics.uci.edu/ca/", "ironwood.ics.uci.edu", "djp3-pc2.ics.uci.edu/LUCICodeRepository/",
      "archive.ics.uci.edu/ml", "www.ics.uci.edu/~xhx/project/MotifMap/"}

for trap in TRAP_URL:
    if "http://calendar.ics.uci.edu/download.php".__contains__(trap):
        print "find trap url"


test="%20Average&z=largebreakdown_reports.php./graph_all_periods.php?c=pedigree&h=pedigree-2.ics.uci.edu&r=hour&z=default&jr=&js=&st=1486438790&v=0.06&m=load_one&vl=%20&ti=One%20Minute"

print not re.match(".*[\\?@=].*", test)