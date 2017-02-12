import urllib
from urlparse import urlparse

from bs4 import BeautifulSoup

def extractLinkFromPage(content, scheme, netloc, stack):
    res = list()
    temp = list(stack)
    for link in BeautifulSoup(content, "lxml").findAll('a'):
        url = link.get('href')
        if url == None or url == '':
            continue
        # process relative path
        if url.startswith("/") or url.startswith('../'):
            newUrl, stepBack = getRelPath(url)
            absolutePath = getAbsolutePath(temp, stepBack, newUrl)
            url = scheme + "://" + netloc + absolutePath
        res.append(url)
    return res


def getRelPath(url):
    if url[0] == '/':
        return url, 0
    stepBack = (len(url) - len(url.replace('../', ''))) / 3
    newUrl = url.replace('../', '')
    return stepBack, "/" + newUrl


def getPathStack(path):
    stack = []
    for ele in path.split('/'):
        if ele != None and ele != '' and not (ele.endswith('.php') or ele.endswith('.html')):
            stack.append(ele)
    return stack


def getAbsolutePath(stack, backSteps, relPath):
    res = ""
    for i in range(backSteps):
        stack.pop()

    for ele in stack:
        res = res + "/" + ele
    return res + relPath


def getHtml(url):
    page = urllib.urlopen(url)
    html = page.read()
    return html


url = "http://www.ics.uci.edu/about/brenhall/ugrad/index.php"
html = getHtml(url)
parsed = urlparse(url)
page = extractLinkFromPage(html, parsed.scheme, parsed.netloc, getPathStack(parsed.path))
print page
