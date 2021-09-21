from django.contrib.sessions.serializers import JSONSerializer
from hashid_field import Hashid


class HashidJSONEncoder(JSONSerializer):
    def default(self, o):
        if isinstance(o, Hashid):
            return str(o)
        return super().default(o)
