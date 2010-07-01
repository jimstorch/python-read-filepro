#------------------------------------------------------------------------------
#   read_filepro/fpmap.py
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
Open and interpret a Filepro Map file.

Not intended for use on files under control of an active Filepro session.
In other words; halt Filepro, copy the data files, use on the copies.
"""

import os
import sys
import string

class FPMap(object):

    def __init__(self, folder):

        fname = os.path.join(folder, 'map')
        map_fp = open(fname, 'r')
        line = map_fp.readline()
   
        if line.startswith('Alien:'):
            print("Not compatible with 'Alien' map file:%s" % fname)
            sys.exit(1)  

        if not line.startswith('map:'):
            print('Not a Filepro MAP file: %s' % fname) 
            sys.exit(1)
    
        data = line.split(':')
        _key_record_length = int(data[1])
        _data_record_length = int(data[2])
        _key_field_count = int(data[3])
        self.pw_checksum = data[4]
        self.encrypted_pw = data[5]

        ## Get the fields contained in the 'key' file

        self.key_fields = []
        self.key_record_length = 0
        self.key_field_count = 0

        for x in range(_key_field_count):
            line = map_fp.readline()            
            data = line.split(':')
            name = ''.join(filter(lambda x:x in string.printable, data[0]))
            ## Some of the fields in the map file are dummys; X::
            if data[1]:
                length = int(data[1])
            else:
                length = 0
            edit_type = data[2]
            self.key_fields.append((name, length, edit_type,))
            self.key_record_length += length 
            self.key_field_count += 1            

        ## Get the fields contained in the 'data' file

        self.data_fields = []
        self.data_record_length = 0
        self.data_field_count = 0

        while True:
            line = map_fp.readline()
            if not line:
                break
            data = line.split(':')
            name = ''.join(filter(lambda x:x in string.printable, data[0]))
            if data[1]:
                length = int(data[1])
            else:
                length = 0
            edit_type = data[2]
            self.data_fields.append((name, length, edit_type,))
            self.data_record_length += length 
            self.data_field_count += 1      

        map_fp.close()

        ## Some sanity checking
        assert _key_record_length == self.key_record_length 
        assert _key_field_count == self.key_field_count
   
