
import sys
import os
import numpy

import collections
import math
import json

from lib.libUtah import *


def main():

  debug = True

  y2000_format_file = 'format.Y2000_station_archive'
  y2000_archive_file = 'example_event/arc2000.ORIG'
  ml_amps_file  = 'example_event/ml_amps.11121315063'
  uw1_pick_file = 'example_event/11121315063p'
  json_mapfile  = 'example_event/channelmap.11121315063.json'
  amps_mapfile  = 'example_event/channelmap.11121315063.amps'

# 1. Read the Hypoinverse Y2000 archive format:
  y2kformat = read_format(y2000_format_file)
# 2. And use it to read in a Y2000 event archive file:
  (y2k, origin)  = read_phases('example_event/arc2000.ORIG', y2kformat)
# 3. Read in amplitude file:
  ml_amps = read_magfile(ml_amps_file)
# 4. Read in modified UW1 pick file:
  (duw1, yyyymmddhhmi)  = read_modUW1_file(uw1_pick_file)
# 5. Read in JSON SCNL Map - used to map original y2k sta to SCNL
  json_map = read_json_scnl_map(json_mapfile)

  coda_scnl=collections.OrderedDict()

# Map the duw1 sta to SCNL:
  for key, value in duw1.iteritems():
    scnl = None
    if key in json_map:
        scnl = json_map[key][0]
    if scnl:
        value['sta'] = scnl['s']
        value['chan']= scnl['c']
        value['net'] = scnl['n']
        value['loc'] = scnl['l']
        value['scnl']= scnl['s'] + "." + scnl['c'] + "." + scnl['n'] + "." + scnl['l']
        coda_scnl[value['scnl']] = value 

  y2k_scnl=collections.OrderedDict()

# Map the y2k sta to SCNL:
  for key, value in y2k.iteritems():
    scnl = None
    if key in json_map:
        scnl = json_map[key][0]
    if scnl:
        value['sta'] = scnl['s']
        value['chan']= scnl['c']
        value['net'] = scnl['n']
        value['loc'] = scnl['l']
        value['scnl']= scnl['s'] + "." + scnl['c'] + "." + scnl['n'] + "." + scnl['l']
        y2k_scnl[value['scnl']] = value 

  amps_map = read_amps_scnl_map(amps_mapfile)

  amps_scnl=collections.OrderedDict()
# Map the amp sta North/East to SCNL:
  for sta, value in ml_amps.iteritems():
    for comp in "NORTH", "EAST", "AVE" :
        k = sta + "-" + comp
        if k in amps_map:
            scnl = amps_map[k]['scnl']
            key = "amp_%s" % comp.lower()
            amps_scnl[scnl] = value[key]

  if debug:
    print '         1         2         3         4         5         6         7         8         9         C         D'
    print '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345'

# Merge amplitude measurements with y2k archive:
  for scnl, value in amps_scnl.iteritems():
    if scnl in y2k_scnl:
        y2k_scnl[scnl]['Amp'] = value
    else:
        #print "amp key=[%s] NOT found in y2k_scnl" % key
        (sta, chan, net, loc) = scnl.split('.')
        y2kline = new_y2k_line(y2kformat)
        y2kline['sta']  = sta
        y2kline['chan'] = chan
        y2kline['net']  = net
        y2kline['loc']  = loc
        y2kline['year'] = origin[0:4] 
        y2kline['moddhhmi'] = origin[4:12] 
        y2kline['Psec'] = 0
        y2kline['Amp'] = value 
        y2kline['AmpCode'] = '0' 
        y2kline['PwtCode'] = '4' 
        #write_y2000_phase(y2kformat, y2kline)
        y2k_scnl[scnl] = y2kline

# Print out y2k lines followed by coda shadow lines for same scnl 
#   iff coda duration > 0 in y2k archive:
  print origin
  for scnl, value in y2k_scnl.iteritems():
    write_y2000_phase(y2kformat, value)
    if value['CodaDur'] > 0 and scnl in coda_scnl:
        write_coda_shadow(coda_scnl[scnl], yyyymmddhhmi)

  exit()

  return

if __name__ == '__main__':
    main()
