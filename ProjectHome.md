# read\_filepro for Python #

Python source for extracting map, key, and data records from an ancient filePro database.  Reads the raw files so a copy of filePro is not required.

July 1, 2010

## Background ##

Recently, I was asked to extract the data from over four hundred filePro
databases created by an office over a nine year period.  To hopefully spare
someone else this hassle, I'm posting my findings and code.  I copied 544mb in
filePro stuff and ended up with 109mb in .CSV files.  They were using filePro
version 5.0.09, however, I did not use filePro itself for any step of this
conversion.

I'm capitalizing for discussion only.  The code expects all filenames to be in
lowercase. My coding/conversion platform was Linux using Python 2.6.  I did not
have access to the filePro application itself.

Filepro is not the same thing as F,I,L,E,M,A,K,E,R, ,P,R,O.  I'll try not to
waylay googlers.


## filePro ##

Filepro stores data in three files; MAP, DATA, and KEY.

There are other files for indexing, screens, and whatnot.  We don't care, our
goal is get the data out.


### Map File ###

You could call this the schema.  The first line holds six segments separated by
colons.  Here they are;

  1. The string literal 'map'.  If it starts with 'Alien:' then it's some kind of external data reference (??).  I had two and ignored them.
  1. The size in bytes of one record in the KEY file.  If the record represents five fields that are 10 bytes wide, this would be 50. Note that filepro tacks on a 20 byte header to each record in the KEY file, so the real KEY record size would be 70.
  1. The size in bytes of one record in the DATA file.  No header.  May be zero if all columns are kept in the KEY file.
  1. Number of fields that are in the KEY file.  All fields beyond this count are kept in the DATA file.
  1. Eight byte checksum for the encoded password.  We don't care.
  1. The encoded password.  Again, we don't care.  It's only used by filePro to permit changes.  All the actual data is in cleartext.

The second through last lines contain details of each column in the database.
Again, columns are usually broken across the KEY and DATA files.

Each line contains three segments separated by colons:

  1. The name of the fields.  Sometimes empty, sometimes has weird characters.
  1. The width in bytes of the field. Sometimes empty for dummy or placeholder fields.  Not really sure why.  I ignored all fields with a blank width.
  1. The edit type.  I think this is used by filePro when validating a field value.  Seemed ok to ignore since everything was stored as non-terminated ASCII sequences, even numbers.

Ref: https://www.fptech.com/Products/Docs/FPFormat/ftmap.shtml


### Key File ###

The KEY file is a flat file.  It should always be record\_count X record\_size long.  The record size is the width of all the key fields plus a 20 byte 'deleted' and 'used' headers.

The only byte in the header I care about is at offset 0:
  * 0x00 = this is a deleted record
  * 0x01 = this is an active record

The database column in the KEY file are apparently those that filePro has built indexes for.  All other columns are stored in the DATA file.  It is possible for all columns to be in KEY and have a DATA file 0 bytes long.

Filepro does not shrink the file as you deleted records.  It maintains a chain of deleted records as uses those as slots for saving new ones.

Ref: https://www.fptech.com/Products/Docs/FPFormat/ftkey.shtml


### Data File ###

As stated above, the DATA files seems to be "other half" of the fields outlined
in the MAP file -- that are not indexed(?).  It's a flatfile that seems
to match the KEY file, record for record, but does not use a
record header so it's length is equal to ((sum of field widths) X number of
records)).

If all columns are indexed, then the map file is empty because all columns are
in KEY.


## DOS/UNIX Line Endings ##

WARNING: This is not a step.  If you don't understand what I'm talking about,
don't do this.

I was lucky enough to find the FTP daemon running on the SCO box I needed to
grab data from.  I copied the entire filePro directory to a Windows PC and then
burned it to CD.  Sadly, I forgot to set the mode to binary and most of my KEY
files got messed up because Filezilla was trying to convert line endings from
UNIX to DOS/Windows style.

It took me a while to realize because I was also trying to figure out how
filePro stored its data. Some of the files were evenly divisible by record
size and some weren't.

I was able to fix some using the 'flip' utility:
```
$ sudo apt-get install flip
$ flip -u -b -v appl/filepro/A_FOLDER/key
```

If you have a bunch, you can batch convert them with:
```
$ cd appl
$ find . -name key -exec flip -u -b -v {} \;
```

My success rate was about around 75%.  We ended up re-FTP'ing the files in
binary mode and all worked fine.


## The Code ##

First, a couple disclaimers:

  * Copy your data and only work with a disposable copy!
  * Do not run filePro on the database while trying to read it from Python. Which wont happen because you're working on a disposable copy, right?
  * It only reads from filePro databases, it does not write to them.
  * It slurps the entire database into memory.  It may choke on giant sets. OTOH, I don't expect there are a lot of giant filePro sets.
  * The folder you pass must contain a 'map', 'key', and 'data' file -- with lowercase names.  It will bomb on an empty folder.
  * The MAP file cannot be an Alien pointer (for reading external ASCII files?).
  * This code is not highly tested.  I worked on it until I got all my files converted.

### The Source Files ###

  * read\_filepro/fpmap.py - the FPMap class used to open MAP files.
  * read\_filepro/fpkey.py - the FPKey class used to open KEY files.
  * read\_filepro/fpdata.py - the FPData class used to open DATA files.
  * read\_filepro/fpdatabase.py - the FPDatabase class that wraps the three previous classes to open an entire filePro database.

Using FPDatabase is pretty simple.  Just pass it one argument, the path of the
directory containing a filePro database:
```
from read_filepro import FPDatabase
db = FPDatabase('/tmp/appl/filepro/A_DATABASE')
```

### FPDatabase Methods ###

  * db.get\_field\_count() - returns number of fields in the table
  * db.get\_field\_names() - returns the names of the fields, in column order
  * db.get\_field\_types() - guesses the value type, either 'string' or 'numeric'

  * db.get\_total\_record\_count() - returns number of records in table, including deleted
  * db.get\_active\_record\_count() - returns number of active/non-deleted records
  * db.get\_deleted\_record\_count() - returns number of deleted records

The following methods return a Python list object containing records. Each
record is a Python list object containing strings for every column value.

  * db.get\_all\_records() - returns a list of all records; active + deleted.
  * db.get\_active\_records() - returns a list of non-deleted records
  * db.get\_deleted\_records() - returns a list of deleted records.

  * db.is\_deleted(index) - returns true if index value is a deleted record.
  * db.get\_record(index) - returns the record at index as a Python list.
  * db.get\_record\_dict(index) - returns the record at index as a Python dictionary where key = field name and value = column value.

### Batch Convert ###

I used the script 'batch\_convert.py' to mass convert the filePro databases
into Comma Separated Value (CSV) files.  You'll need to edit it and set
values for APPL\_PATH and CSV\_PATH .  I had to delete a couple source folders
with 'Alien' map files and one empty directory (working from disposable
copies of course).

Good Luck and please me know if you find this code useful or find any bugs or mistakes in my descriptions.

Contact info: jimstorch plus that at-sign symbol then gmail and then add the
TLD for commercial entities.


## Update: Feb 28, 2012 ##

I received the following email from John Esak, writer and editor of numerous works on filePro including **The filePro Cookbook** and **The Guru Magazine**.  John was kind enough to let me share his comments:

> Very nice, you certainly have provided a nifty way for people to extract
> data from filePro databases. Of course, there is a two or three line piece
> of processing that can be used from **within** filePro itself to dump out
> complete .csv files of all the data, but if one has no idea of how to get
> into filePro, write the processing table, few line that it is, and maybe not
> even have a filePro license, that is all irrelevant, and besides your python
> tool is immediately understandable and usable by anyone who has minimum
> database knowledge.  So, thanks, your work is much appreciated. I think it
> was also nice (and smart) of you to disassociate filePro and fileMakerPro
> right at the start of the article.  People are constantly confusing the two
> programs.

> I do a little python programming, and your program was very straightforward,
> so no comments there. Except the db\_get\_field\_type() function would not have
> to "guess" if you employed the third field of the "map" file to determine
> the data type.  You were exactly right, that 3rd field is used by filePro to
> validate data input.  I think for that reason this field became known as the
> EDIT TYPE.  There are an unlimited number of names to be found in this
> field.  However, there are a handful of factory provided edit types (which
> are called system edits) that are internal to filePro and not user developed
> that force the data into 3 data types. String, numeric and date.  I could
> list them all out for you, but it wouldn't be many to include in a simple
> statement which would then nail down your type without guessing.  If the 3rd
> field contains a system edit for numeric, it's numeric. If it is one of the
> variations mask variations for displaying dates, it is date type.  And if it
> is any of the other system edit names, or any user defined edit name, it is
> what you call "other string" type data.

> This of course would be useful to know when translating numeric values and
> especially date values into what they were stored as within filePro.
> Obviously, 010503 in a field would be considered one thing as a string, and
> various different things if it were stored as a date type value. (January 5,
> 2003 or 2001, May 3rd, or lots of other formats as determined by the system
> edit used, i.e., mdy, or ymd, or with slashes mdy/, mdyy/ and so forth.)

> I hope that is helpful to you. I'm fairly sure you only needed your program
> as a one-off for the large dataset you converted, so you may not want to
> incorporate any of this, but you asked for suggestions. :-)  Oh yes, one
> other small mis-statement. You tied indexing to the key or data segment
> fields.  That actually used to be true back until about 1984 or 1985 maybe.
> Since then, any field whether it is in the key segment or the data segment
> can be indexed. The history of why there even is a data segment is very Ur
> and only important to we earliest of filePro users. It was an offshoot of
> total record size limitations and an  efficient usage of the Z80 chip's
> memory capabilities as implemented in the earliest Tandy TRS-80 machines.

> I'll forward a copy of this to Ken Brody who designed most of filePro and he
> can point to one of the many old explanations that exist here and there...
> Or just recount why he had to do it that way... If he cares to reminisce.
> :-) (Ken have you seen this? I'm guessing your periodic sweeps of the net
> for "filePro" must have brought this to you already. But, in case you
> haven't seen it, here it is. Has it been up on the list? Maybe they would
> like to know about it.)

> Anyway, good work, Jim. Thanks.  I wish you had been able to contact a
> filePro programmer back when you wrote this script, he/she might have made
> your effort a lot easier.

