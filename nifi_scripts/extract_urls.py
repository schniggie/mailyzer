import re
import quopri
import urllib
from org.apache.commons.io import IOUtils
from java.nio.charset import StandardCharsets
from java.io import BufferedReader, InputStreamReader
from org.apache.nifi.processors.script import ExecuteScript
from org.apache.nifi.processor.io import InputStreamCallback
from org.apache.nifi.processor.io import StreamCallback

class PyInputStreamCallback(InputStreamCallback):
    _text = None

    def __init__(self):
        pass

    def getText(self) : 
        return self._text

    def process(self, inputStream):
        self._text = IOUtils.toString(inputStream, StandardCharsets.UTF_8)

flowFile = session.get()
if flowFile is not None :
    reader = PyInputStreamCallback()
    session.read(flowFile, reader)

    separator = '; '
    regex = 'http[s]?://(?:[a-zA-Z]|[0-9]|[#-/@.&+=;:?]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
    urls = re.findall(regex, reader.getText())
    urls = list(dict.fromkeys(urls))
    length = len(urls) 
    for i in range(length):
        urls[i] = quopri.decodestring(urls[i])
        urls[i] = urllib.quote(urls[i], '/:')

    urls = separator.join(urls)

    flowFile = session.putAttribute(flowFile, 'urls', urls)
    session.transfer(flowFile, ExecuteScript.REL_SUCCESS)
