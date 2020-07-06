import email
import mimetypes
from email.parser import Parser
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

    msg = email.message_from_string(reader.getText())
    body = ""

    if msg.is_multipart():
        html = None
        for part in msg.walk():

            print "%s, %s" % (part.get_content_type(), part.get_content_charset())

            if part.get_content_charset() is None:
                # We cannot know the character set, so return decoded "something"
                text = part.get_payload(decode=True)
                continue

            charset = part.get_content_charset()

            if part.get_content_type() == 'text/plain':
                text = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

            if part.get_content_type() == 'text/html':
                html = unicode(part.get_payload(decode=True), str(charset), "ignore").encode('utf8', 'replace')

        if text is not None:
            body = text.strip()
        else:
            body = html.strip()
    else:
        text = unicode(msg.get_payload(decode=True), msg.get_content_charset(), 'ignore').encode('utf8', 'replace')
        body = text.strip()

    tos = msg.get_all('to', [])
    ccs = msg.get_all('cc', [])
    resent_tos = msg.get_all('resent-to', [])
    resent_ccs = msg.get_all('resent-cc', [])
    all_recipients = email.utils.getaddresses(tos + ccs + resent_tos + resent_ccs)
    all_recipients = ''.join(all_recipients[0])

    flowFile = session.putAttribute(flowFile, 'msgto', all_recipients.decode('utf-8', 'ignore'))
    flowFile = session.putAttribute(flowFile, 'msgbody', body.decode('utf-8', 'ignore'))
    session.transfer(flowFile, ExecuteScript.REL_SUCCESS)
