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


class RedshiftDatastore(DataStore):
    def __init__(self, service_object_registry, **kwargs):
        DataStore.__init__(self, service_object_registry, **kwargs)
        
    

    def write(self, records, **kwargs):
        db_svc = self.service_object_registry.lookup('redshift_svc')        
        Listing = db_svc.Base.classes.grailed_listings

        for record in records:
            print('>>> placeholder Redshift data write operation:')
            db_record = json.loads(record)
            with db_svc.txn_scope() as session:
                listing = Listing()
                for key, value in db_record.items():
                    if value == 'True':
                        setattr(listing, key, True)
                    elif value == 'False':
                        setattr(listing, key, False)
                    else:
                        setattr(listing, key, value)
                session.add(listing)
                session.commit()
            print(common.jsonpretty(json.loads(record)))

