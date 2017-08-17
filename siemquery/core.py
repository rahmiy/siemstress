#!/usr/bin/env python

#_MIT License
#_
#_Copyright (c) 2017 Dan Persons (dpersonsdev@gmail.com)
#_
#_Permission is hereby granted, free of charge, to any person obtaining a copy
#_of this software and associated documentation files (the "Software"), to deal
#_in the Software without restriction, including without limitation the rights
#_to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#_copies of the Software, and to permit persons to whom the Software is
#_furnished to do so, subject to the following conditions:
#_
#_The above copyright notice and this permission notice shall be included in all
#_copies or substantial portions of the Software.
#_
#_THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#_IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#_FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#_AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#_LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#_OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#_SOFTWARE.

from siemstress import __version__
#import logdissect.parsers
#import time
#from datetime import datetime
#import re
#import sys
#import os
#import MySQLdb as mdb
from argparse import ArgumentParser
import ConfigParser
import siemquery



class QueryCore:

    def __init__(self):
        """Initialize live parser"""

        self.args = None
        self.arg_parser = ArgumentParser()
        self.config = None

        #self.parser = None
        #self.parsername = None
        self.server = None
        self.user = None
        self.password = None
        self.database = None
        self.table = None
        self.queryfields = None



    def get_args(self):
        """Set argument options"""

        self.arg_parser.add_argument('--version', action = 'version',
                version = '%(prog)s ' + str(__version__))
        self.arg_parser.add_argument('--clear',
                action = 'store_true', dest = 'clearsiem',
                help = ('delete the SQL table for selected section'))
        #self.arg_parser.add_argument('-q',
        #        action = 'store_true', dest = 'querysiem',
        #        help = ('query the SQL table for selected section'))
        self.arg_parser.add_argument('-c',
                action = 'store', dest = 'config',
                default = '/etc/siemstress/siemstress.conf',
                help = ('set the config file'))
        self.arg_parser.add_argument('-s',
                action = 'store', dest = 'section',
                default = 'default',
                help = ('set the config section'))
        #self.arg_parser.add_argument('-z',
        #        action = 'store', dest = 'tzone',
        #        help = ("set the offset to UTC (e.g. '+0500')"))
        self.arg_parser.add_argument('--last',
                action = 'store', dest = 'last', default = '24h',
                help = ("set the preceeding time range (5m, 24h, etc)"))
        self.arg_parser.add_argument('--shost',
                action = 'store', dest = 'shost', default = None,
                help = ("match a source host"))
        self.arg_parser.add_argument('--process',
                action = 'store', dest = 'process', default = None,
                help = ("match a source process"))
        self.arg_parser.add_argument('--grep',
                action = 'store', dest = 'grep', default = None,
                help = ("match a pattern"))

        self.args = self.arg_parser.parse_args()



    def get_config(self):
        """Read the config file"""

        config = ConfigParser.ConfigParser()
        if os.path.isfile(self.args.config):
            myconf = (config)
        else: myconf = 'config/siemstress.conf'
        config.read(myconf)

        self.server = config.get('siemstress', 'server')
        self.user = config.get('siemstress', 'user')
        self.password = config.get('siemstress', 'password')
        self.database = config.get('siemstress', 'database')
        self.table = config.get(self.args.section, 'table')
        #self.parsername = config.get(self.args.section, 'parser')
        self.queryfields = [int(x) for x in config.get(
            'default', 'queryfields').split(',')]


        #if self.parsername == 'syslogbsd':
        #    self.parser = logdissect.parsers.syslogbsd.ParseModule()
        #elif self.parsername == 'syslogiso':
        #    self.parser = logdissect.parsers.syslogiso.ParseModule()
        #elif self.parsername == 'nohost':
        #    self.parser = logdissect.parsers.nohost.ParseModule()
        #elif self.parsername == 'tcpdump':
        #    self.parser = logdissect.parsers.tcpdump.ParseModule()



    def clear_siem(self):
        """Clear SQL table specified in section"""

        con = mdb.connect(self.server, self.user, self.password,
                self.database)

        with con:
            cur = con.cursor()

            cur.execute('DROP TABLE IF EXISTS ' + self.table)



    def query_siem(self):
        """Query SQL database for log events"""
        

        query = siemquery.SiemQuery(server = self.server, user = self.user,
                password = self.password, database = self.database)

        desc, rows = query.simple_query(table = self.table,
                last = self.args.last, shost = self.args.shost,
                process = self.args.process, grep = self.args.grep)

        #con = mdb.connect(self.server, self.user, self.password,
        #        self.database)
        
        #with con: 
        
        #    cur = con.cursor()
        #    cur.execute("SELECT * FROM " + self.table + \
        #                " WHERE DateStamp >= timestamp(date_sub(now(), " + \
        #                "interval 24 hour))")

        #    rows = cur.fetchall()
    
        #    desc = cur.description

        print "%7s %20s %10s %10s %7s %s" % (
                desc[self.queryfields[0]][0],
                desc[self.queryfields[1]][0],
                desc[self.queryfields[2]][0],
                desc[self.queryfields[3]][0],
                desc[self.queryfields[4]][0],
                desc[self.queryfields[5]][0])

        for row in rows:
            print "%7s %20s %10s %10s %7s %s" % (
                    row[self.queryfields[0]],
                    row[self.queryfields[1]],
                    row[self.queryfields[2]],
                    row[self.queryfields[3]],
                    row[self.queryfields[4]],
                    row[self.queryfields[5]])



    def run_query(self):
        # try:
        try:
            self.get_args()
            self.get_config()
            #if self.args.clearsiem:
            #    self.clear_siem()
            #else
            self.query_siem()
            #else:
            #    self.parse_entries()

        except KeyboardInterrupt:
            pass
        # except Exception as err:
        #     print('Error: ' + str(err))

    
    
def main():
    query = QueryCore()
    query.run_query()


if __name__ == "__main__":
    query = QueryCore()
    query.run_query()