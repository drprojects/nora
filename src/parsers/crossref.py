
# TODO: https://github.com/fabiobatalha/crossrefapi
#  to parse from DOI


from crossref.restful import Works

works = Works()
out = works.doi('10.1007/978-981-19-7580-6_1')
