# grailed-test
Data engineering challenge

The code for this challenge uses the Mercury data engineering toolkit from Binarymachines. In particular,
it uses the `xfile` and `ngst` Python scripts to transform CSV files and send the results to an arbitrary target.


`xfile` employs a configurable type called a Map, along with a pluggable type called a DatasSource. `ngst` uses a plugin type 
called a DataStore. Both scripts employ ServiceObject plugins for two-way communication with external services.

## xfile
A Map is a structured type describing the relationship between an input record (a set of name-value pairs) and an output record.
Each map contains some metadata, a reference to a DataSource, and a collection of fields. The fields comprise a nested dictionary inside
the map where the key is the output field name. Within each field we can have an input field name and a source for that field; that is,
the place we go to find the field's value during a mapping operation. So for example, if we wished to map an input field called `"firstname"`
to an output field called `"first_name"`, we would add to our YAML file a field called "first_name" and specify its source as 
the record itself (meaning the inbound record) and its key as "firstname". The `xfile` script, based on that configuration, will build
the mapping logic to generate an output record with the correct field name and the correct value.

In the case of derived or computed field values, we first write a DataSource class and register it in our YAML config. 
We do this by updating the python module specified in the lookup_source_module global setting 


```yaml  
globals:
    project_home: $GRAILED_HOME
    lookup_source_module: grailed_datasources # <-- create this module and place it on the PYTHONPATH
    service_module: grailed_services
```


and adding an entry under the top-level `sources` key.

```yaml
  sources:
    grdata:
      class: GrailedLookupDatasource  # <-- write this class in the grailed_datasources module 
```

finally we let our map know that its designated datasource is the one we just created:

```yaml
  maps:
    default:
      settings:
          - name: use_default_identity_transform
            value: True

      lookup_source: 
        grdata # <-- this must match the name under which we registered our GrailedLookupDatasource class
``` 
      
 Now, in the individual field specs of our map, we can specify that a given output field will get its value not from the
 input record, but from the datasource:
 
```yaml
  fields:
      - calculated_field_name:
            source: lookup
```     
      
 And `xfile`, on startup, will dynamically load our Datasource and verify that it exposes a method called 
 `lookup_calculated_field_name(...)`, calling that method when it needs to generate the mapped field value. In cases where the name of an output field is not compatible with Python function naming rules, we can specify the lookup function's name explicitly:
 
 ```yaml
  fields:
      - <calculated field name with spaces>:
            source: lookup
            key: <arbitrary_function_name>
```  
 
 
Note that a single YAML initfile can have multiple maps and multiple DataSources, so that operators can select arbitrary mappings simply by specifying the desired map as a command line argument.
 
We run `xfile` by specifying a configuration file, an optional delimiter (the default is a comma), the name of a registered map from the config, and the source CSV file:

`xfile --config <yaml file> --delimiter '\t' --map <map_name> input.csv`

There is also an optional `--limit` setting for testing `xfile` against very large input datasets:

`xfile --config <yaml file> --delimiter '\t' --map <map_name> --limit 5`  <-- only transform the first five records from source 
 
`xfile` outputs JSON records only.
 
 ## ngst
The `ngst` script takes the records emitted by `xfile` and writes them to a specified IngestTarget, which is simply a named destination for output records. Each target consists of a reference to a dynamically loaded DataStore class and a `checkpoint_interval` setting which selects the buffer depth in number of records (a checkpoint interval of 1 selects unbuffered writes to the target). Operators can simply subclass the DataStore base class and implement the `write()` method, then register the plugin in the YAML file under the top-level `datastores` key:
 
 ```yaml
   datastores:
      file:
          class: FileStore
          init_params:
                  - name: filename
                    value: output.txt
```

then, at the command line, specify the target by key. `ngst` will read the input records (either from a file or standard input) and write the output records to the designated DataStore.


A ServiceObject is simply a long-running singleton which is spun up at program start. It is exactly the same type as is used in the 
Binarymachines SNAP (Small Network Applications in Python) microservices library, and it is initialized in exactly the same way
(the YAML config syntax is drop-in compatible). By using ServiceObjects, we can easily inject complex dependencies such as AWS or GCP targets, standalone databases, or any other services required by `xfile` or `ngst`. 


To perform a mapping, issue `pip install -r requirements.txt` to install the dependencies, then run `xfile` (running it without arguments generates a usage string). The YAML initfile parse logic is smart about environment variables, so in the case of plugins which require service logins, you can safely refer to credential strings by prepending $ to an init_param value. 

Starting `ngst` without specifying an input CSV file will cause it to read from standard input, allowing you to pipe data to it from the `xfile` transform script. Using the `-p` flag will cause `ngst` to run in preview mode (it will transform input records but write them to standard out rather than the designated target). For testing against large input datasets, use the `--limit=<N>` option to stop after N records have been processed.
 
 
 
 
 
 
 
      
