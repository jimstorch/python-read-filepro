#!/usr/bin/env python
#------------------------------------------------------------------------------
#   batch_convert.py
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
Given a path to the 'appl/filepro' directory of databases, attempts to
open each and convert then into Comma Separated Value (CSV) files.
"""


import os
import sys
import csv
from time import strftime

from read_filepro import FPDatabase

## Set to the location of your /appl directory
APPL_PATH = "./appl/filepro"

## Set to the location where you want the .CVS files to go
CVS_PATH = './tmp'


def timestamp_filename(base=''):
    """
    Return a CSV filename derived from the base path + timestamp.
    If no basepath is provided, you get timestamp only.
    """
    ## strip all but letters and digits
    s = ''.join([x for x in base if x.isalpha() or x.isdigit()])
    ## timestamp in the format YYYYmmddHHMMSS
    return s + strftime("_%Y%m%d%H%M%S.csv")


def filepro_to_csv(source_dir, target_dir):
    """
    Given a filePro directory name, copies all the data with headers
    to a .CSV file in the target directory.
    """
    base = os.path.basename(source_dir)
    csv_fname = os.path.join(target_dir, timestamp_filename(base))
    db = FPDatabase(source_dir)
    csv_fp = open(csv_fname, 'w')
    writer = csv.writer(csv_fp, quoting=csv.QUOTE_MINIMAL)
    writer.writerow(db.get_field_names())
    writer.writerows(db.get_active_records())
    csv_fp.close()


if __name__ == '__main__':

    print '\n\n'
    names = os.listdir(APPL_PATH)
    names.sort() 
    for name in names:
        target = os.path.join(APPL_PATH, name)
        if os.path.isdir(target):
            print target
            filepro_to_csv(target, CVS_PATH)
    
        

