from urlparse import urlparse

url = "http://www.ics.uci.edu/about/visit/bren/index.php"

parsed = urlparse(url)
split = parsed.path.split('.php')

print len(split)