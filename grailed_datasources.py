#!/usr/bin/env python

import json
from snap import common



class GrailedLookupDatasource(object):
    def __init__(self, service_object_registry):
        pass

    def lookup_domestic_ship_price(self, target_field_name, source_record, field_value_map):
        #print('### unpacking "shipping" field...')
        #print(common.jsonpretty(json.loads(source_record['shipping'])))
        return 0.0
