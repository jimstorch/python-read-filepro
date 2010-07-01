#!/usr/bin/env python
#------------------------------------------------------------------------------
#   demo.py
#   Copyright 2010 Jim Storch
#   Licensed under the Apache License, Version 2.0 (the "License"); you may
#   not use this file except in compliance with the License. You may obtain a
#   copy of the License at http://www.apache.org/licenses/LICENSE-2.0
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#   WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#   License for the specific language governing permissions and limitations
#   under the License.
#------------------------------------------------------------------------------
"""
== List of methods ==

    db.get_field_count()
    db.get_field_names()
    db.get_field_types()

    db.get_total_record_count()
    db.get_active_record_count()
    db.get_deleted_record_count()

    db.get_all_records()
    db.get_active_records()
    db.get_deleted_records()

    db.is_deleted(index)
    db.get_record(index)
    db.get_record_dict(index)
"""

from read_filepro import FPDatabase

## Set this to the path of a FP Database
DB_PATH = './appl/filepro/zip'


print("--> Loading the database...")
db = FPDatabase(DB_PATH)
print("--> Database Loaded")

field_count = db.get_field_count()
print("--> There are %d fields in the database." % field_count)  

field_names = db.get_field_names()
print("--> The field names are: %s" % str(field_names))
  
total_record_count = db.get_total_record_count()
print("--> There are %d total records." % total_record_count)

active_record_count = db.get_active_record_count()
print("--> There are %d active records." % active_record_count)

deleted_record_count = db.get_deleted_record_count()
print("--> There are %d deleted records." % deleted_record_count)

if total_record_count > 0:
    print("--> The first record is: ")
    print(str(db.get_record(0)))
    if db.is_deleted(0):
        print("--> That record is marked as deleted.")
    else:
        print("--> That record is not marked as deleted.")

    print("--> Here it is again as a dictionary:")
    print(str(db.get_record_dict(0)))

else:
    print("--> No data to show.")    



