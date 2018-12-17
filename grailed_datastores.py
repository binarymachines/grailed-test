#!/usr/bin/env python


import json
from snap import common
from ngst_tools import DataStore


class FileStore(DataStore):
    def __init__(self, service_object_registry, **kwargs):
        DataStore.__init__(self, service_object_registry, **kwargs)
        kwreader = common.KeywordArgReader('filename')
        kwreader.read(**kwargs)
        self.filename = kwreader.get_value('filename')


    def write(self, records, **kwargs):
        with open(self.filename, 'a') as f:
            for record in records:
                f.write(record)
                f.write('\n')

