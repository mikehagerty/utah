
import sys
import os
import numpy

import collections
import math
import json
import getopt

from lib.libUtah import *
from lib.liblog import getLogger

logger = getLogger()

# If no path is passed in on the cmd line with the -p or --path option, 
#  this default path will be used:
DEFAULT_DATA_DIR_PATH = '/eq/legacy_data/UNGODLY/NEW'

debug = False

def exit_now(msg):
    logger.error(msg)
    exit(2)

def processCmdLine():
    usage = "arc.py -e event_id --path=/path/to/event [-d or --debug] \n     eg. >arc.py -e 11121315063 --path=/eq/legacy_data/UNGODLY/NEW"
    fname = "processCmdLine"
    global debug
    event_id = None
    path = None
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'e:p:dh', ['help', 'debug', 'event_id=', 'path='])
        if len(args) > 0:        # MTH: args is not used here, opts = list[tuple], eg [('-e', 1234567)]
            exit_now(usage)
    except getopt.GetoptError:   # Throw error if opt not in list above
        exit_now(usage)

    for opt, arg in opts:        # MTH: now we split the opts tuple to get opt, arg
        if opt in ('-e', '--event_id'):
            try:
                #event_id = int(arg)
                event_id = arg
            except:
                logger.error("%s: Unable to convert event_id=[%s] to integer" % (fname, arg))
                exit_now(usage)
        elif opt in ('-p', '--path'):
            try:
                path = arg
            except:
                logger.error("%s: Unable to read command line path=[%s]" % (fname, arg))
                exit_now(usage)
        elif opt in ('-d', '--debug'):
            debug = True
            logger.info("%s: Run in debug mode" % (fname))
        elif opt in ('-h', '--help'):
            logger.info("%s: This is where the help message goes" % (fname))
            exit_now(usage)
        else:
            logger.error("%s Unknown cmd line opt=[%s]" % (fname, opt) )
            exit_now(usage)

    if event_id is None:
        logger.error("%s.%s Can't continue without valid event_id" % (__name__, fname) )
        exit_now(usage)
    if path is None:
        path = DEFAULT_DATA_DIR_PATH
        logger.info("%s: No -p or --path cmd line opts --> use default path=[%s]" % (fname, path) )
    if not os.path.exists(path) or not os.path.isdir(path):
        logger.error("%s path=[%s] not a valid directory!" % (fname, path) )
        exit(2)

    return path, event_id

def getFilenames(directory, event_id):
    fname = "getFilenames"
    if directory[-1] == '/':
        directory = directory[:-1]
    #yy = int(str(event_id)[0:2])
    yy = int(event_id[0:2])
    if yy >= 80:
        year = yy + 1900
    else:
        year = yy + 2000

    event_path = '%s/%s/%s' % (directory, year, event_id)

    if not os.path.exists(event_path) or not os.path.isdir(event_path):
        logger.error("%s.%s event_id=[%s] event_path=[%s] is not a valid directory!" % \
                    (__name__, fname, event_id, event_path) )
        exit(2)

    files = {}
    files['arc']  = '%s/arc2000' % (event_path)
    #files['amps'] = '%s/ml_amps.%s' % (event_path, event_id)
    files['uw1']  = '%s/%sp' % (event_path, event_id)
    files['json_map'] = '%s/channelmap.json' % (directory)
    files['amps_map'] = '%s/channelmap.amps' % (directory)

    for key,val in files.iteritems():
        if not os.path.exists(val):
            logger.error("%s key=[%s] file=[%s] not found!" % (fname, key, val) )
            exit(2)

    ampFileExists = False
    ampfile = '%s/ml_amps.%s' % (event_path, event_id)
    if os.path.exists(ampfile):
        files['amps'] = ampfile
        ampFileExists = True

    return files, ampFileExists


def main():

  (path, event_id) = processCmdLine()
  (files, ampFileExists) = getFilenames(path, event_id)

  y2000_format_file = 'format.Y2000_station_archive'

# 1. Read the Hypoinverse Y2000 archive format:
  y2kformat = read_format(y2000_format_file)
# 2. And use it to read in a Y2000 event archive file:
  (y2k, origin)  = read_phases(files['arc'], y2kformat)
# 3. Read in modified UW1 pick file:
  (duw1, yyyymmddhhmi)  = read_modUW1_file(files['uw1'])
# 4. Read in JSON SCNL Map - used to map original y2k sta to SCNL
  json_map = read_json_scnl_map(files['json_map'])

  coda_scnl=collections.OrderedDict()

# Map the duw1 sta to SCNL:
  for key, value in duw1.iteritems():
    scnl = None
    if key in json_map:
        scnl = json_map[key][0]
    else:
        logger.warn("arc.py: Unable to locate uw1 pick station=[%s] in json_map file=[%s]" % (key, files['json_map']))
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
    # [SOW] b. Remove any existing peak-to-peak (p-p) amplitudes in the Y2000 archive file.
    value['Amp'] = 0.0
    scnl = None
    if key in json_map:
        scnl = json_map[key][0]
    else:
        logger.warn("arc.py: Unable to locate y2000 arc station=[%s] in json_map file=[%s]" % (key, files['json_map']))
    if scnl:
        value['sta'] = scnl['s']
        value['chan']= scnl['c']
        value['net'] = scnl['n']
        value['loc'] = scnl['l']
        value['scnl']= scnl['s'] + "." + scnl['c'] + "." + scnl['n'] + "." + scnl['l']
        y2k_scnl[value['scnl']] = value 

# 5. Read in the amplitude file if it exists
  if ampFileExists:
    ml_amps = read_magfile(files['amps'])
    amps_map = read_amps_scnl_map(files['amps_map'])
    amps_scnl=collections.OrderedDict()
# Map the amp sta North/East to SCNL:
    for sta, value in ml_amps.iteritems():
        for comp in "NORTH", "EAST", "AVE" :
            k = sta + "-" + comp
            if k in amps_map:
                scnl = amps_map[k]['scnl']
                key = "amp_%s" % comp.lower()
                amps_scnl[scnl] = value[key]
            else:
                logger.warn("arc.py: Unable to locate [%s] in amps_map file=[%s]" % (k, files['amps_map']))

# Merge amplitude measurements with y2k archive:
    for scnl, value in amps_scnl.iteritems():
        if scnl in y2k_scnl:
            y2k_scnl[scnl]['Amp'] = value
            y2k_scnl[scnl]['AmpMagC'] = '0'    #Amplitude magnitude weight code
            y2k_scnl[scnl]['AmpType'] = '1'    #1=Wood-Anderson
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
            y2kline['AmpMagC'] = '0'    #Amplitude magnitude weight code
            y2kline['AmpType'] = '1'    #1=Wood-Anderson
            #write_y2000_phase(y2kformat, y2kline)
            y2k_scnl[scnl] = y2kline

  if debug:
    print '         1         2         3         4         5         6         7         8         9         C         D'
    print '1234567890123456789012345678901234567890123456789012345678901234567890123456789012345678901234567890123456789012345'

# Print out y2k lines followed by coda shadow lines for same scnl 
#   iff coda duration > 0 in y2k archive:
  print origin
  for scnl, value in y2k_scnl.iteritems():
    write_y2000_phase(y2kformat, value)
    if value['CodaDur'] > 0 and scnl in coda_scnl:
        write_coda_shadow(coda_scnl[scnl], yyyymmddhhmi)
    else:   # Print blank shadow line
        printf("$\n")

  # Shadow Archive terminator lines: blank + single "$" in col 1:
  printf("\n")
  printf("$")

  exit()
  return

if __name__ == '__main__':
    main()
