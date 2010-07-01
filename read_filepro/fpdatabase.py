#------------------------------------------------------------------------------
#   read_filepro/database.py
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
Open and interpret a Filepro database directory.

Not intended for use on files under control of an active Filepro session.
In other words; halt Filepro, copy the data files, use on the copies.
"""

from read_filepro.fpmap import FPMap
from read_filepro.fpkey import FPKey
from read_filepro.fpdata import FPData


class FPDatabase(object):

    def __init__(self, folder):
        self.fpmap = FPMap(folder)
        self.fpkey = FPKey(folder, self.fpmap)
        self.fpdata = FPData(folder, self.fpmap, self.fpkey)

    def is_deleted(self, index):
        """
        Given a record number, returns True if that record is marked as 
        deleted.
        """
        return self.fpkey.deletes[index]

    def get_total_record_count(self):
        """
        Return the total number of records, including deleted ones.
        """
        return self.fpkey.total_records

    def get_active_record_count(self):
        """
        Return the number of active records; i.e. total - deleted. 
        """
        return self.fpkey.active_records

    def get_deleted_record_count(self):
        """
        Return the number of deleted records.
        """
        return self.fpkey.deleted_records

    def get_field_count(self):
        """
        Return the number of fields/columns in the database.
        Omits dummy/placeholder fields with zero length.
        """
        return len(self.get_field_names())

    def get_field_names(self):
        """
        Return the name of all fields/columns in the database.
        Merges key file and data file field names.
        Omits dummy/placeholder fields with zero length.
        """
        key_fields = [ d[0] for d in self.fpkey.fields ]
        data_fields = [ d[0] for d in self.fpdata.fields ]
        return key_fields + data_fields

    def get_all_records(self):
        """
        Return a list of all records, including deleted.
        """
        records = []
        for x in range(self.fpkey.total_records):
            row = self.fpkey.records[x] + self.fpdata.records[x]
            records.append(row)
        return records

    def get_active_records(self):
        """
        Return a list of active records, omitting deleted ones.
        """
        records = []
        for x in range(self.fpkey.total_records):
            if not self.is_deleted(x):
                row = self.fpkey.records[x] + self.fpdata.records[x]
                records.append(row)
        return records

    def get_deleted_records(self):
        """
        Return a list of deleted records, omitting active ones.
        """
        records = []
        for x in range(self.fpkey.total_records):
            if self.is_deleted(x):
                row = self.fpkey.records[x] + self.fpdata.records[x]
                records.append(row)
        return records

    def get_record(self, index):
        """
        Given an integer value, returns the corresponding record merges from
        the key and data files.
        """
        return self.fpkey.records[index] + self.fpdata.records[index]

    def get_record_dict(self, index):
        """
        Given an integer value, returns a dictionary of field names mapped
        to record values.
        """ 
        fields = self.get_field_names()
        columns = self.get_record(index)
        combo = zip(fields, columns)
        return dict(combo)

    def get_field_types(self):
        """
        Scans all values in each database column to see if they are numeric
        or string values.

        Returns a table containing 'number' or 'string' for each column.
        The purpose of this is determining whether to quote when 
        exporting to CSV files.   
        """
        column_types = []
        for i in range(self.get_field_count()):
            this_type = 'number'
            for record in self.get_all_records():
                entry = record[i]
                if entry:
                    try:
                        foo = float(entry)
                    except ValueError:
                        this_type = 'string'
            column_types.append(this_type)
        return column_types


