#!/usr/bin/env python
#################################################################################################
# shelve-tool
# Manages SQLiteShelve databases
# Usage: shelve-tool _command_ [options] [_field1_=value] [_field2_=value] ...
#        commands
#        add-type aNewRegisteredType
#        add --type=_aRegisteredType_  _key_ _field_=value [_field2_=value] ... - add a record of a registered type 
#        update _key_ _field_=newvalue [_field2_=newvalue] ... - update existing record with new field values
#        delete _key_ - remove an entry from the database
#        list - list all the keys in the database
#        show _key_ - shows the contents of record indexed by _key_
# namespace(file='mydb', func=<function add at 0x1013f4050>, key='obj1', keywords=['database=blah', 'count=4'], type='user-object')
##################################################################################################
from . import open as shelve_open
from . import close as shelve_close
import argparse
import os
import sys
import configparser
import datetime
import getpass

def parse_keywords(keywords):
    """
      Returns a dictionary for valid key=value strings
    """

    d = {}
    try:
       d = dict([x.split('=',1) for x in keywords])
    except ValueError as e:
       for kw in keywords:
          if '=' not in kw:
             print("Keyword: %s is invalid" % kw)
       print("All keywords should be formatted as key=value.")
       

    return d

def add(args):
    """
      Add a new record to the database.
    """
    
    rec = parse_keywords(args.keywords)
    rec['type'] = args.type
    rec['key'] = args.key

    db = shelve_open(args.file)
    
    udt_key = 'UDT_%s' % args.type
    if udt_key in db:
       udt_rec = db[udt_key]
       fieldnames = udt_rec['fieldnames']
       for fn in fieldnames:
           if fn not in rec:
              rec[fn] = None

    
    if args.key in db:
       print("Record with key: %s already exists." % args.key)
       return

    created_ts = str(datetime.datetime.now())
    create_user = getpass.getuser()
    rec['created_ts'] = created_ts
    rec['create_user'] = create_user
 
    db[args.key] = rec
    db.close() #commits changes    
    print('Entry %s added.' % args.key)

def add_type(args):
    """
      Add a new user-defined record type to the database.
      A pre-defined record time lets you include metadata information about the fields in a record,
      a which fields are required.  It also enables more convenient searches for information based on type.
      And queries on fields.
    """
    db = shelve_open(args.file)
    user_type_name = 'UDT_' + args.type_name
    if user_type_name in db:
       print("User type %s already exists." % user_type_name)

       return

    rec = {}
    rec['type'] = 'metadata'
    rec['name'] = user_type_name
    rec['fieldnames'] = args.fieldnames
    rec['description'] = args.description
    created_ts = str(datetime.datetime.now())
    create_user = getpass.getuser()
    rec['created_ts'] = created_ts
    rec['create_user'] = create_user
    db[user_type_name] = rec
    db.close()
    print("Record user-type: %s added." % args.type_name)


def list_records(args):
    """
       List the records in a database.
    """
    db = shelve_open(args.file)
    count = 0 
    if args.long:
       header = "%-15s  %-60s" % ('Object Key','Data')
       header2 = '%s  %s' % ('-' * 15, '-' * 60)
       format_str = "%-15s  %-60s"
       footer = '-' * 77
    else:
       header = 'Object Key'
       header2 = '-' * 15
       footer = '-' * 15

    print(header)
    print(header2)
    print()
    for key in db:
        if args.type:
           if args.type != db[key].get('type',''):
              continue

        elif db[key].get('type','') == 'metadata' and not args.show_metadata:
           continue
        
        if args.long:
           print(format_str % (key,db[key]))
        else:
           print(key)
        count += 1
    print(footer)
    print("%d records" % count)

def show(args):
    """
      Show contents of a record.
    """
    db = shelve_open(args.file)
    if args.key in db:
       print("Displaying contents of record: %s" % args.key)
       rec = db[args.key]
       print(rec)      
    else:
       print("No record for key: %s found." % args.key)


def update(args):
    """
      Update a records attributes.
    """
    db = shelve_open(args.file)
    if args.key in db:
       updates = parse_keywords(args.keywords)
       rec_to_update = db[args.key]
       rec_to_update.update(updates)
       last_update_ts = str(datetime.datetime.now())
       last_update_user = getpass.getuser()
       rec_to_update['last_update_ts'] = last_update_ts
       rec_to_update['last_update_user'] = last_update_user
       db[args.key] = rec_to_update
       db.close() #commit changes
       print("Updated record: %s " % args.key)
    else:
       print("Key: %s does not exist." % args.key)

def delete(args):
    """
      Delete a record from the database.
    """
    db = shelve_open(args.file)
    if args.key in db:
       del db[args.key]
       db.close() #commit or delete will not happen
       print("Record for %s deleted." % args.key)
    else:
       print("Cannot delete. Key: %s does not exist" % args.key)
       
    
parser = argparse.ArgumentParser('shelve-tool')
parser.add_argument('--file','-f',help='shelve file',dest='file',default='shelve.db')
subparsers = parser.add_subparsers(help='Command help')

#Add command
parser_add = subparsers.add_parser('add',help='Add Command Help')
parser_add.add_argument('key',help='A string that serves as a name for a new record')
parser_add.add_argument('--type','-t',help='User-defined type for this record. Used to query or list records by a type',dest='type',default='user-object')
parser_add.add_argument('keywords',nargs='*',help='space-separated key=value pairs, corresponding to fields and values in the record')
parser_add.set_defaults(func=add)

#Add-type command
parser_add_type = subparsers.add_parser('add-type',help='Add Type Command Help')
parser_add_type.add_argument('type_name',help='Name of user type')
parser_add_type.add_argument('--fieldnames',nargs='*',help='space-separated fieldnames, which if present, are set with default values of None')
parser_add_type.add_argument('--description',help='Description about the type')
parser_add_type.set_defaults(func=add_type)

#Update command
parser_update = subparsers.add_parser('update',help='Update Command Help')
parser_update.add_argument('key',help='Key identifying the record')
parser_update.add_argument('keywords',nargs='*',help='space-separated key=value pairs, corresponding to fields and values in the record.')
parser_update.set_defaults(func=update)

#Delete command
parser_delete = subparsers.add_parser('delete',help="Delete Command Help")
parser_delete.add_argument('key',help='Key identifying record')
parser_delete.set_defaults(func=delete)

#List command
parser_list = subparsers.add_parser('list',help='List Command Help')
parser_list.add_argument('--type','-t',help='Limit list to --type=USERTYPE',dest='type')
parser_list.add_argument('--long','-l',help='Show long listing',action='store_true')
parser_list.add_argument('--show-metadata','-M',help='displays metadata records along with user-data',dest='show_metadata',action='store_true')
parser_list.set_defaults(func=list_records)

#Show command
parser_show = subparsers.add_parser('show',help='Show Command Help')
parser_show.add_argument('key',help='Key identifying name of record.')
parser_show.set_defaults(func=show)

def cli():
    """
    Execute cli functions
    """

    args = parser.parse_args()

    if len(sys.argv) < 2:
         parser.print_help()
         sys.exit(0)

    args.func(args)
