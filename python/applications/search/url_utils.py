import urllib
from urlparse import urlparse
from urlparse import urljoin
from bs4 import BeautifulSoup


def extractLinkFromPage(content, scheme, netloc, stack, originURL):
    res = set()
    # temp = list(stack)
    for link in BeautifulSoup(content, "lxml").findAll('a'):
        url = link.get('href')
        url = urljoin(originURL, url)

        # if url == None or url == '':
        #     continue
        # if url.startswith("http") or url.startswith("https"):
        #     url = url
        # # process relative path
        # elif url.startswith('../'):
        #     newUrl, stepBack = getRelPath(url, temp)
        #     absolutePath = getAbsolutePath(temp, stepBack, newUrl)
        #     url = scheme + "://" + netloc + absolutePath
        # elif url.startswith('/'):
        #     url = scheme + "://" + netloc + url
        # elif url.startswith("mailto") or url == "#":
        #     continue
        # else:
        #     url = scheme + "://" + netloc + "/" + url
        res.add(url)

    return res


def getRelPath(url, stack):
    # if url[0] == '/':
    #     # find the common dictory
    #     eles = url.split('/')
    #     # find the first non-empty ele
    #     for e in eles:
    #         if e != None and e != '':
    #             try:
    #                 index = stack.index(e)
    #                 return url, len(stack) - index
    #             except:
    #                 return url, 0
    #     return url, 0
    stepBack = (len(url) - len(url.replace('../', ''))) / 3
    newUrl = url.replace('../', '')
    return "/" + newUrl, stepBack

def getPathStack(path):
    stack = []
    for ele in path.split('/'):
        if ele != None and ele != '' and not (ele.endswith('.php') or ele.endswith('.html')):
            stack.append(ele)
    return stack


def getAbsolutePath(stack, backSteps, relPath):
    res = ""
    for i in range(backSteps):
        if len(stack) != 0:
            stack.pop()

    for ele in stack:
        res = res + "/" + ele
    return res + relPath


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html


# url = "http://www.ics.uci.edu/about/about/about"
# html = getHtml(url)
# parsed = urlparse(url)
# page = extractLinkFromPage(html, parsed.scheme, parsed.netloc, getPathStack(parsed.path), url)
# print page
#
urljoin('http://www.cwi.nl/%7Eguido/Python.html', 'FAQ.html')


# https://foofish.net/python-crawler-html2pdf.html