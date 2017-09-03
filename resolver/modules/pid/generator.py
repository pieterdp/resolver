# -*- coding: utf-8 -*-
from resolver import app
import re
from unidecode import unidecode
import urlparse
import uuid
import hashlib
import base64


##
# Max size of the ID is 64 characters (ID_MAX)
class PidGenerator:

    def __init__(self, original_id, override_domain=None):
        self.original_id = original_id
        self.domain = override_domain
        if not override_domain:
            self.domain = self.__domain()
        self.identifier = u'pid://{0}/{1}'.format(self.domain, self.original_id)

    def uuid(self):
        # 36 characters
        return uuid.uuid3(uuid.NAMESPACE_URL, self.identifier.encode('utf-8'))

    def hash(self):
        # We're limited to sha256, as the resulting hash must be <= 64 characters
        return hashlib.sha1(self.identifier.encode('utf-8')).hexdigest()

    def base64(self):
        return base64.b64encode(self.identifier.encode('utf-8'))

    def legacy(self):
        _clean_re = re.compile(r'[\t !"#$%&\'()*/<=>?@\[\\\]^`{|}]+')
        patterns = [
            # Exceptions
            ('- ', '-'), (' -', '-'), ('\)+$', ''), ('\]+$', ''), ('\°+$', ''),
            # Simple replacements
            ('\.', '_'), (' ', '_'), ('\(', '_'), ('\)', '_'), ('\[', '_'), ('\]', '_'),
            ('\/', '_'), ('\?', '_'), (',', '_'), ('&', '_'), ('\+', '_'), ('°', '_'),
            # Replace 1 or more underscores by a single underscore
            ('_+', '_')]
        partial = reduce(lambda str, t: re.sub(t[0], t[1], str),
                         patterns,
                         self.original_id)
        # For safety, let's give it another scrub.
        result = []
        for word in _clean_re.split(partial):
            result.extend(unidecode(word).split())

        return unicode(''.join(result))

    def __domain(self):
        url = urlparse.urlparse(app.config['BASE_URL'])
        return url.netloc

