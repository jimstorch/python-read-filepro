#------------------------------------------------------------------------------
#   read_filepro/fpkey.py
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
Open and interpret a Filepro Key file.

Not intended for use on files under control of an active Filepro session.
In other words; halt Filepro, copy the data files, use on the copies.
"""

import os
import sys


_FILEPRO_HEADER_SIZE = 20


class FPKey(object):

    def __init__(self, folder, fpmap):

        self.fields = []
        self.records = []
        self.deletes = []
        self.total_records = 0
        self.active_records = 0
        self.deleted_records = 0

        _record_length = fpmap.key_record_length + _FILEPRO_HEADER_SIZE
        fname = os.path.join(folder, 'key')

        ## I have files that were copied from SCO Unix to Windows to Linux
        ## and picked up erroneous linefeed conversions, so we'll check
        ## that KEY file size is evenly divisible by record_length.
        data = os.stat(fname)
        size = data[6]
        if size % _record_length:
            print("\n\nProblem with the file '%s'." % fname)
            print("Error: file size is NOT a multiple of the record size.")
            print("See the README on DOS/UNIX linefeeds for possible fix.")
            sys.exit(1)            

        ## Construct a list of slice points by field widths
        cuts = []
        for field in fpmap.key_fields:
            ## Filter out reserved/dummy fields with 0 width
            if field[1]:
                self.fields.append(field)    
                cuts.append(field[1])                       

        key_fp = open(fname, 'rb')  
        count_active = 0

        while True:
            block = key_fp.read(_record_length)
            if len(block) == 0:
                break

            ## Filepro uses a 20 byte preamble/header on key records
            ## Header offset 0 == 0x00 for deleted record, 0x01 for active.
            deleted = not bool(ord(block[0]))
            self.deletes.append(deleted)
            if not deleted:
                count_active += 1                                 

            data = block[20:]
            #print data
            row = []
            last_cut = 0
            ## Slice out field values
            for cut in cuts:
                row.append(data[last_cut:last_cut + cut].strip())
                last_cut += cut
            self.records.append(row)
        
        key_fp.close()
        self.total_records = len(self.records)        
        self.active_records = count_active
        self.deleted_records = self.total_records - count_active

