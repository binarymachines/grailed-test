# grailed-test
Data engineering challenge

The code for this challenge uses the Mercury data engineering toolkit, which is an in-progress work at Binarymachines. In particular,
it uses the ngst Python script to transform CSV files and send the results to an arbitrary target.


ngst employs a metaphor called a Map, along with four pluggable types: DatasSources, IngestTargets, DataStores, and ServiceObjects.

A Map is a structured type describing the relationship between an input record (a set of name-value pairs) and an output record.
Each map contains some metadata, a reference to a DataSource, and a collection of fields. The fields comprise a nested dictionary inside
the map where the key is the output field name. Within each field we can have an input field name and a source for that field; that is,
the place we go to find the field's value during a mapping operation. So for example, if we wished to map an input field called "firstname"
to an output field called "first_name", we would add to our YAML file a field called "first_name" and specify its source as 
the record itself (meaning the inbound record) and its key as "firstname". The ngst script, based on that configuration, will build
the mapping logic to generate an output record with the correct field name and the correct value.

In the case of derived or computed field values, we first write a DataSource class and register it in our YAML config. 
We do this by updating the python module specified in the lookup_source_module global setting 


`  globals:
    project_home: $GRAILED_HOME
    lookup_source_module: grailed_datasources # <-- create this module and place it on the PYTHONPATH
    service_module: grailed_services
    datastore_module: grailed_datastores`


and adding an entry under the top-level `sources` key.

`
  sources:
    grdata:
      class: GrailedLookupDatasource  # <-- write this class in the grailed_datasources module 
`

finally we let our map know that its designated datasource is the one we just created:

`
  maps:
    default:
      settings:
          - name: use_default_identity_transform
            value: True

      lookup_source: 
        grdata # <-- this must match the name under which we registered our GrailedLookupDatasource class
`   
      
 Now, in the individual field specs of our map, we can specify that a given output field will get its value not from the
 input record, but from the datasource:
`
  fields:
      - calculated_field_name:
        source: lookup
`     
      
 And ngst, on startup, will dynamically load our Datasource and make sure it exposes a method called 
 `lookup_calculated_field_name(...)`, calling that method when it needs to generate the mapped field. Note that a single YAML initfile
 can have multiple maps and multiple DataSources, so that operators can select arbitrary mappings simply by specifying the desired map
 as a command line argument.
 
 An IngestTarget is simply a named destination for output records. Each target consists of a reference to a dynamically loaded DataStore
 class and a checkpoint_interval setting which essentially selects buffer depth in number of records (a checkpoint interval of 0 selects unbuffered writes to the target). Operators can simply subclass the DataStore base class and implement the `write()` method, then register the plugin
 in the YAML file under the top-level `datastores` key:
 `
   datastores:
      file:
          class: FileStore
          init_params:
                  - name: filename
                    value: output.csv
`
then, at the command line, specify the target by key. ngst will perform the configured mapping on the input data and write the output
records to the designated DataStore.


A ServiceObject is simply a long-running singleton which is spun up at program start. It is exactly the same type as is used in the 
Binarymachines SNAP (Small Network Applications in Python) microservices library, and it is initialized in exactly the same way
(the YAML config syntax is drop-in compatible).
By using ServiceObjects, we can easily inject complex dependencies such as AWS or GCP targets, standalone databases, and any other
services our record transformer needs to use. 

 
 
 
 
 
 
 
 
 
      
