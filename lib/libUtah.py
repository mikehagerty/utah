
import sys
import os
import numpy
import pprint
from datetime import *
from calendar import *

import collections
import math
import json

from liblog import getLogger

logger = getLogger()

def x_to_a(field_len, x):

    if abs(x) >= math.pow(10., field_len - 1):
        ndec = 0
    elif abs(x) >= 1:
        ndec = field_len - int(math.log10(abs(x))) - 2
        if ndec == 0:
            ndec = 1
    else:
        ndec = field_len - 1

    #if x < 0:
        #ndec -= 1

    xx = "%.*f" % (ndec, x)
    a  = str(xx)

    if x < 1:
        a = a.replace('0', '', 1)
    if len(a) > field_len:
        a = a[0:field_len]

    if len(a) != field_len:
        raise Exception
    else:
        return a

def new_y2k_line(y2kformat):
    d=collections.OrderedDict()
    for key, value in y2kformat.iteritems():
        d[key] = None
        #d[key] = printf("%*s" % (value['len'], ' '))
    return d


def read_amps_scnl_map(file):
    '''
YMR EAST  YMR HHE WY 01
YMR NORTH YMR HHN WY 01
YMR AVE   YMR HHH WY 01
YFT EAST  YFT HHE WY 01
YFT NORTH YFT HHN WY 01
YFT AVE   YFT HHH WY 01
    '''
    fname = 'read_amps_scnl_map'
    try:
        f=open(file, 'r')
        lines=f.readlines()
    except (OSError, IOError) as e:
        logger.error("%s.%s: Attempt to read amps_scnl_map file=[%s] gives error=[%s]" % (__name__, fname, file, e))
        raise

    if len(lines) == 0:
        logger.error("%s.%s: amps_scnl_map file=[%s] appears to be empty!" % (__name__, fname, file))
        exit(2)

    d = {}
    for line in lines:
        try:
            (staIn, chanIn, sta, chan, net, loc) = line.split()
        except ValueError:
            logger.error("%s.%s: amps_scnl_map file=[%s] line=[%s] incorrect!" % (__name__, fname, file, line))
            raise

        key = staIn + "-" + chanIn
        dd = {}
        dd['sta'] = sta
        dd['chan']= chan
        dd['net'] = net
        dd['loc'] = loc
        dd['scnl'] = sta + "." + chan + "." + net + "." + loc
        d[key] = dd
    return d


def write_coda_shadow(val, yyyymmddhhmi):
    '''
Use the following format for the shadow line, which is similar to the format in which these data are stored in the modified UW1-format files.

Columns Format  Description
3-14     I4, 4I2  Reference date-time in the form YYYYMMDDHHMM where YYYY, MM, DD, HH, MM are 
                    the UTC year, month, day, hour, and minute
16-20    F5.2     Alpha (called Qfree by Jiggle), which is the decay constant in the coda 
                    decay function A0(t-tp)-alpha, where t is time and tp is the P-wave arrival time
22-26    F5.2     log(A0) (called Afree by Jiggle), where A0 is the amplitude constant in 
                    the coda decay function
28-30    I3       Begin time for coda-decay analysis in seconds relative to the reference time
32-34    I3       End time for coda-decay analysis in seconds relative to the reference time

12345678901234
$ 201112131506  1.50  4.31  75  94
    '''

    #print '123456789012345678901234567890123456789012345678901234567890'
    #for sta, val in duw1.iteritems():
        #printf("%14s %5.2f %5.2f %3d %3d" % (yyyymmddhhmi, val['alpha'], val['logA0'], val['beg'], val['end'])) 
        #printf("\n") 

    printf("$ %12s %5.2f %5.2f %3d %3d\n" % (yyyymmddhhmi, val['alpha'], val['logA0'], val['beg'], val['end'])) 

    '''
    if sta in duw1:
        val = duw1[sta]
        printf("%14s %5.2f %5.2f %3d %3d" % (yyyymmddhhmi, val['alpha'], val['logA0'], val['beg'], val['end'])) 
        printf("\n") 
    else:
        print("sta=[%s] not found in duw1 dict!" % sta)
    '''

    return



def read_json_scnl_map(file):
    fname = 'read_json_scnl_map'
    with open(file) as json_data:
        d = json.load(json_data)
        keys = d.keys()
        value = d[keys[0]]
        if type(value) is dict:
            pass
        elif type(value) is list: # convert list-stype json map to dict
            dd = {}
            for key in keys:
                dd[key]=d[key][0]
            d = dd
        else:
            e = 'Attempt to read json_map file=[%s]. Map is not dict or list but unknown type!' % (file)
            logger.error("%s.%s: %s" % (__name__, fname, e))
            raise Exception(e)

    return d

def read_magfile(file):
    fname = 'read_magfile'
    '''
Event: 11121315063p

STA      EAST       NORTH      AVE       MAG
YMR      0.18318    0.30294    0.24306   1.30
YFT      1.21361    1.54573    1.37967   1.94
YNR      0.21966    0.22756    0.22361   2.10
YPP    177.54710  112.07440  144.81075   3.14
    '''
    try:
        f=open(file, 'r')
        header = f.readline().strip()
        f.readline()
        f.readline()
        lines=f.readlines()
    except (OSError, IOError) as e:
        logger.error("%s.%s: Attempt to read amp file=[%s] gives error=[%s]" % (__name__, fname, file, e))
        raise

    if len(lines) == 0:
        logger.error("%s.%s: amp file=[%s] appears to be empty!" % (__name__, fname, file))
        exit(2)

    d = {}
    for line in lines:
        line = line.rstrip('\n\r')
        try:
            #(sta, amp_east, amp_north, amp_ave, mag) = line.split()
            fields = line.split()
            if len(fields) == 5:
                (sta, amp_east, amp_north, amp_ave, mag) = fields
            else:
                (sta, amp_east, amp_north, amp_ave) = fields
                mag = -999 # Flag no mag in amp file
            amp_east  = float(amp_east)
            amp_north = float(amp_north)
            amp_ave   = float(amp_ave)
            mag       = float(mag)
            dd = {}
            dd['amp_east'] = amp_east
            dd['amp_north']= amp_north
            dd['amp_ave']  = amp_ave
            dd['mag'] = mag
            d[sta.strip()] = dd 
        except Exception as e:
            raise

    return d


def read_modUW1_file(file):
    '''
     PING-FILE FORMAT FOR UUSS PHASE FILES
     Reference Time (line 1)

     Column    Format    Description
     2-3       I2        Year (last two digits)
     4-5       I2        Month (UTC)
     6-7       I2        Day (UTC)
     8-9       I2        Hour (UTC)
     10-11     I2        Minute (UTC)

     Picks (post July 15, 1987, format)
     Column    Format    Description
     1-4       A4        Station Name
     6                   A1Polarity of 1st Motion (C,D,+, or, -)
     10        I1        P-Quality (0-4)
     12-17     F6.2      P-arrival (seconds after reference minute)
     19        I1        S-Quality (0-4)
     21-26     F6.2      S-arrival (seconds after reference minute)
     27-30     I4        Duration in sec (I3 format before March 14, 2001)
     32-36     F5.2      Alpha (constant in decay function Ao(t-tp)^-alpha)
     38-42     F5.2      log(Ao) (constant in decay function Ao(t-tp)^-alpha)
     44-46     I3        Begin time for coda-decay analysis
     48-50     I3        End time for coda-decay analysis (maximum value of
                         80 sec after begin time before Feb. 12, 1996, and
                         999 sec thereafter)
     52-56     I5        Peak-to-peak amplitude (in counts)
    '''
    fname = 'read_modUW1_file'

    try:
        f=open(file, 'r')
        header = f.readline().strip()
        lines=f.readlines()
    except (OSError, IOError) as e:
        logger.error("%s.%s: Attempt to read modUW1 file=[%s] gives error=[%s]" % (__name__, fname, file, e))
        raise

    if len(lines) == 0:
        logger.error("%s.%s: modUW1 file=[%s] appears to be empty!" % (__name__, fname, file))
        exit(2)

    try:
        yy    = int(header[0:2])
        if yy >= 80 and yy <= 99:
            year = 1900 + yy
        else:
            year = 2000 + yy
        month = int(header[2:4])
        day   = int(header[4:6])
        hour  = int(header[6:8])
        minute= int(header[8:10])
        #print("UW Header: %4d-%02d-%02d %02d:%02d" % (year, month, day, hour, minute))
        yyyymmddhhmi = '%4d%02d%02d%02d%02d' % (year, month, day, hour, minute)
    except Exception as e:
        raise

    d = {}

    for line in lines:
        line = line.rstrip('\n\r')
        #print line
#123456789012345678901234567890123456789012345678901234567890
#MCID ?   0  64.38 0   0.00 393  1.84  5.47  70  90     0
        if line[0:2] == 'c ':    # Comment lines start with 'c '
            continue
        sta   = line[0:4].strip()
        Ptime = line[11:17]
        if not any(str.isdigit(c) for c in Ptime):
            continue
        else:
            duration = 0
            alpha = 0
            logA0 = 0
            beg = 0
            end = 0
            try:
                Ptime = float(Ptime)
                buf = line[26:30]
                if any(str.isdigit(c) for c in buf):
                    duration = int(buf)
                buf = line[31:36]
                if any(str.isdigit(c) for c in buf):
                    alpha = float(buf)
                buf = line[37:42]
                if any(str.isdigit(c) for c in buf):
                    logA0 = float(buf)
                buf = line[43:46]
                if any(str.isdigit(c) for c in buf):
                    beg = int(buf)
                buf = line[47:50]
                if any(str.isdigit(c) for c in buf):
                    end = int(buf)

                if logA0 > 0:
                    dd = {}
                    dd['Ptime']    = Ptime
                    dd['duration'] = duration
                    dd['alpha']    = alpha
                    dd['logA0']    = logA0
                    dd['beg']      = beg
                    dd['end']      = end
                    d[sta] = dd
            except Exception as e:
                raise
            
    return (d, yyyymmddhhmi)

def write_y2000_phase(dformat, arrival):

    #print '1234567890123456789012345678901234567890123456789012345678901234567890'

    #for key, arrival in dphases.iteritems():

    for k, val in dformat.iteritems():

            format = dformat[k]['format']
            w  = dformat[k]['len']

            #print "key=%s k=%s val=%s format=%s width=%d" % (key, k, val, dformat[k]['format'], w)

            if k[0:5] == 'blank' or arrival[k] is None or arrival[k] == '':
                printf("%-*s" % (w, ' '))
            else:
                if format[0:1] == 'A' or format[0:1] == 'I':
                    if val['align'] == 'R':
                        printf("%*s" % (w, str(arrival[k])))
                    else:
                        printf("%-*s" % (w, str(arrival[k])))

                elif format[0:1] == 'F':
                    (field_len, ndec) = format[1:4].split('.')
                    #print "format=%s field_len=%s ndec=%s" % (format, field_len, ndec)
                    field_len = int(field_len)
                    ndec = int(ndec)

                    if k == 'Amp': 
                        printf("%*s" % (w, x_to_a(field_len, arrival[k])))
                        '''
                        amp = float(arrival[k])
                        if amp >= 1000. :
                            printf("%7.2f" % (float(arrival[k])))
                        elif amp >= 100. :
                            printf("%7.3f" % (float(arrival[k])))
                        elif amp >= 10. :
                            printf("%7.4f" % (float(arrival[k])))
                        else :
                            printf("%7.5f" % (float(arrival[k])))
                        #printf("%7.2f" % (w, (data)))
                        '''
                    else: 
                        data = float(arrival[k])*math.pow(10., ndec)
                        #print "k=[%s] arrival[k]=[%s] data=%.0f" % (k, arrival[k], data)
                        if val['align'] == 'R':
                            #printf("%*s" % (w, string))
                            a = "%*.0f" % (w, (data))
                            if len(a) > field_len:
                                #print "Houston we have a problem a=[%s]" % a
                                printf("%*s" % (w, x_to_a(field_len, arrival[k])))
                            else:
                                printf("%*.0f" % (w, (data)))
                        else:
                            #printf("%-*s" % (w, string))
                            a = "%-*.0f" % (w, (data))
                            if len(a) > field_len:
                                #print "Houston we have a problem a=[%s]" % a
                                printf("%*s" % (w, x_to_a(field_len, arrival[k])))
                            else:
                                printf("%-*.0f" % (w, (data)))
            #print
        #print string
        #exit()

    printf("\n")
    return

def read_phases(file, dformat):
    fname = 'read_phases'
    d=collections.OrderedDict()
    try:
        f=open(file, 'r')
        origin = f.readline().rstrip('\n\r')
        lines=f.readlines()
    except (OSError, IOError) as e:
        logger.error("%s.%s: Attempt to read phase file=[%s] gives error=[%s]" % (__name__, fname, file, e))
        raise

    if len(lines) == 0:
        logger.error("%s.%s: phase file=[%s] appears to be empty!" % (__name__, fname, file))
        exit(2)

    for line in lines:
        line = line.rstrip('\n\r')
        if not line:
            continue
        dd = collections.OrderedDict()
        for key, value in dformat.iteritems():
            i1 = value['start']-1
            i2 = i1 + value['len']
            data = line[i1:i2]
            form = value['format']
            #print "Scan key=[%s] value=[%s] line[%d:%d] = %s" % (key, value, i1, i2, data)
            if form[0] == 'A':
                dd[key] = data.strip()
                #pass
            elif form[0] == 'I':
                #print "key=[%s] data=[%s] len=[%d] " % (key, data, len(data))
                if not any(str.isdigit(c) for c in data):
                    #print "No int to Convert!"
                    continue
                else:
                    try:
                        data = int(data)
                        dd[key] = data
                    except ValueError as e:
                        raise

            elif form[0] == 'F':
#MTH: What to do if field is empty in original y2000 file ?  Flag with -9 and then don't print it ??
                if not any(str.isdigit(c) for c in data):
                    dd[key] = 0
                    #continue
                else:
                    (foo, ndec) = form.split('.')
                    try:
                        if '.' in data: # Try to read in float directly 
                            data = float(data)
                            #print "Got float=%f" % data
                        else:           # Read in int and convert using format specifier
                            ndec = int(ndec)
                            data = float(data)/math.pow(10., ndec)
                        dd[key] = data
                    except Exception as e:
                        raise

            #print "Scan key=[%s] data=[%s]" % (key, data)
        #print("key on dd['sta']=[%s]" % dd['sta'])
        #dd['y2kline'] = line
        d[dd['sta']] = dd

    return d, origin


def read_format(file):
    d=collections.OrderedDict()
    f=open(file, 'r')
    #Skip first 4 lines
    lines=f.readlines()[4:]
    nblank=1
    for line in lines:
        line = line.rstrip('\n\r')
        parsedLine = line.split()
        if len(parsedLine) < 5:
            print("Error with line=[%s]" % line)
        else:
            try:
                col_start = int(parsedLine[0])
                col_len   = int(parsedLine[1])
                col_format= parsedLine[2]
                col_align = parsedLine[3]
                col_field = parsedLine[4]
                if col_field == 'blank':
                    col_field = 'blank%d' % nblank
                    nblank += 1
                    #continue
                #else:
                dd = {}
                dd['start'] = col_start
                dd['len']   = col_len
                dd['format']= col_format
                dd['align'] = col_align
                d[col_field] = dd
            except:
                print "Exception!"

    return d

"""
station_channel class holds the data for a hypoinverse line 
    and has a function to parse the line into the class parse_hinv_line()
"""

class station_data:
  def __init__(self):
    self.net=''
    self.sta=''
    self.lat=0.0
    self.lon=0.0
    self.elev=0.0
    self.ondate='1996/01/01 00:00'
    self.offdate='3000/01/01 00:00'
    self.word_32 = 3210
    self.word_16 = 10
  def get_sta_dict(self):
    return self.__dict__
#    return {'net':self.net, 'sta':self.sta, 'lat':self.lat, 'lon':self.lon, 
#               'ondate':self.ondate, 'offdate':self.offdate, 'word_32':self.word_32,
#               'word_16':self.word_16}


class station_channel(station_data):
  def __init__(self):
    self.seedchan=''
    self.location='  '
    station_data.__init__(self)

  def parse_hinv_line(self, line):
# AB01  XX  EHZ  18 14.8864S125  1.3684E 1200.0     0.00  0.00  0.00  0.00    0.0001
    element_list=line.split()
    self.net=element_list[1]
    self.sta=element_list[0]
    self.seedchan=element_list[2]
    self.location=line[80:82]
    self.lat_deg = int(line[15:17])
    self.lat_min = float(line[18:25])
    self.lat = self.lat_deg + self.lat_min/60.0
    self.lat_char=line[25]
    self.lon_deg= int(line[26:29])
    self.lon_min= float(line[30:37])
    self.lon = self.lon_deg + self.lon_min/60.
    self.lon_char=line[37]
    self.elev = int(line[38:42])

    if self.lon_char == 'W' or self.lon_char == ' ':
      self.lon *= -1.0
    if self.lat_char == 'S':
      self.lat *= -1.0
# debug info
#    print line
#    self.print_sta()

  def print_sta(self):
    print "%s.%s.%s.%s  lat=%f lon=%f elev=%dm\n" % \
		(self.net, self.sta, self.seedchan, self.location, self.lat, self.lon, self.elev)

#    except:
#      sys.stderr.write("problem parsing lat/lon in line: %s\n" % line)

  def kml_station_header(self):
    return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2">
  <Document>
    """
  def kml_station_tail(self):
    return """
       </Document></kml>
    """

  def kml_station(self):
    return """
      <Placemark>
        <name>%s</name>
        <visibility>1</visibility>
        <Style>
          <IconStyle>
            <color>ff00ff00</color>
            <colorMode>normal</colorMode>
            <scale>  1.10</scale>
            <Icon>
              <href>
                http://maps.google.com/mapfiles/kml/shapes/triangle.png                         
              </href>
            </Icon>
          </IconStyle>
        </Style>
        <Point>
          <coordinates>%f,  %f,0,</coordinates>
        </Point>
      </Placemark>""" % (self.sta, self.lon, self.lat)


""" just a simple file parser of hypoinverse lines """

class channel_data(station_channel):
  def __init__(self, chancode):
    self.azimuth=0.0
    self.dip=-90.0       # vertical
    self.samprate=250.0
    if chancode[2]=='N':
      self.dip=0.0
    if chancode[2]=='E':
      self.dip=0.0
      self.azimuth=90.0
    station_channel.__init__(self)

def parse_hinv_file(file):
  station_chans = []
  f=open(file, 'r')
  lines=f.readlines()
  for line in lines:
    sc = station_channel()
    sc.parse_hinv_line(line)
    station_chans.append(sc)
  return station_chans

def get_station_data_dict(station_channels):
  station_data_dict = {}
  for i in station_channels:
    # truncate sta's to 3 chars for Pioneer data
    net_sta = "%s.%s" % (i.net, i.sta)
    if not net_sta in station_data_dict.keys():
      station_data_dict[net_sta] = i
      #print "%s (%f, %f)" % (i.sta, i.lat, i.lon)
  return station_data_dict

class hypo:
  def __init__(self):
    self.evid=0
    self.epoch=0
    self.year=0
    self.month=0
    self.day=0
    self.hour=0
    self.min=0
    self.sec=0.0
    self.fracsec=0.0
    self.lat=0.0
    self.lat_deg=0
    self.lat_min=0.0
    self.lat_char='N'
    self.lon=0.0
    self.lon_deg=0
    self.lon_min=0.0
    self.lon_char='W'
    self.dep=0.0
    self.arrivals=[]
    self.traces=[]
    self.quality='D'
    self.npha=0
    self.mag=0.0
    self.debug=False

  def parse_arc_summary_line(self, line):
    """ for now just get the origin + lat, lon, elevation, we don't care about anything else yet """
# ARC summary
#                                 dep  
#012345678901234567890123456789012345678901234567890
#201311021912007640 1345 81W1222  325  0 10188  2   1 8064  8825025  35  0     21    5  38  79  0  00  00  0  0Ohi    D 10    0 00   0 00         0   0  00V  0  000 XR01

#201407171040428137  687 97W4778  435  0 13187  5   212377  6133210  35  0     15    5  34  59 15  00  00  0  0KAN      23    0 00   0 00  70023113   0  00   0  00  GS01

    self.year=int(line[0:4])
    self.month=int(line[4:6])
    self.day=int(line[6:8])
    self.hour=int(line[8:10])
    self.min=int(line[10:12])
    self.isec=int(line[12:16])
    self.sec=self.isec/100.
    self.isec=int(self.sec)
    self.evid=int(line[136:146])
    if self.isec >= 60:
        self.min +=1
	self.sec -= 60.
        self.isec -= 60
    self.fracsec=self.sec - self.isec
    self.epoch=timegm(datetime(self.year, self.month, self.day, self.hour, self.min, self.isec).timetuple()) + self.fracsec

    self.lat=int(line[16:18])+int(line[19:23])/100.0/60.
    self.lat_deg=int(line[16:18])
    self.lat_min=int(line[19:23])/100.0
    self.lat_char=line[18]
    if self.lat_char == 'S':
        self.lat = self.lat * -1.0
    self.lon_char=line[26]
    self.lon=(int(line[23:26])+float(line[27:31])/100.0/60.0)
    if self.lon_char == 'W':
        self.lon = self.lon * -1.0
    self.lon_deg = int(line[23:26])
    self.lon_min = float(line[27:31])/100.0
    self.dep=float(line[32:36])/100.0
    self.quality='A'
    self.rms = float(line[48:52])/100.
    self.gap = int(line[42:45])
    self.errh = int(line[85:89])/100.
    self.errz = int(line[89:93])/100.
    self.errh = int(line[85:89])/100.
    self.errz = int(line[89:93])/100.
#    self.npha = int(line[51:53])
    self.npha = int(line[118:121])

    if self.debug:
      self.print_origin()


  def arc2kml_string(self):
#  note mag and nearest station are set to 0.0 above for now
       # <name>%4d.%02d.%02d %02d:%02d:%02d </name>
    return """
        <Placemark>
        <styleUrl>#pointStyleMap</styleUrl>
        <ExtendedData>
        <SchemaData schemaUrl="#HypoSummary">
                <SimpleData name="Evid"> %d </SimpleData>
                <SimpleData name="Origin">%4d.%02d.%02d %02d:%02d:%02d</SimpleData>
                <SimpleData name="Lat">%f</SimpleData>
                <SimpleData name="Long">%f</SimpleData>
                <SimpleData name="Depth">%f</SimpleData>
                <SimpleData name="MAG"> %4.1f</SimpleData>
                <SimpleData name="Number_Picks">%d</SimpleData>
                <SimpleData name="Azimuthal_Gap">%d</SimpleData>
                <SimpleData name="Nearest_Station">%5.1f</SimpleData>
                <SimpleData name="RMS"> %4.2f</SimpleData>
                <SimpleData name="Error_H">  %5.2f</SimpleData>
                <SimpleData name="Error_Z">  %5.2f</SimpleData>
                <SimpleData name="Quality"> %s </SimpleData>
        </SchemaData>
        </ExtendedData>
        <Point>
                <coordinates> %f, %f </coordinates>
        </Point>
        </Placemark> """ % (\
	   self.evid, self.year, self.month, self.day, self.hour, self.min, self.isec, self.lat, self.lon, \
           self.dep, 0.0, self.npha, self.gap, 0.0, self.rms, self.errh, self.errz, self.quality, self.lon, self.lat)
   
        #</Placemark> """ % (self.year, self.month, self.day, self.hour, self.min, self.isec, \

  def parse_summary_line(self, line):
    """ for now just get the origin + lat, lon, elevation, we don't care about anything else yet """
# eylon file example (NOT ARC)
#111221 0508 14.36 37 32.75 104 51.10   5.09   1.66 14 334 34.4 0.04  2.6  4.5 D -         0
    self.year=int(line[0:2])+2000
    self.month=int(line[2:4])
    self.day=int(line[4:6])
    self.hour=int(line[7:9])
    self.min=int(line[9:11])
    self.sec=float(line[12:17])

    self.lat=int(line[18:20])+float(line[21:26])/60.0
    self.lon=-1.0*(int(line[27:30])+float(line[31:36])/60.0)
    self.dep=float(line[38:43])
    self.quality=line[78]
    self.rms = float(line[64:68])
    self.gap = int(line[54:58])
    self.npha = int(line[51:53])

    if self.debug:
      self.print_origin()

  def print_origin(self):
    print "%4d/%02d/%02d %02d:%02d %5.2f lat=%7.4f lon=%8.4f depth=%5.2f gap=%3d rms=%4.2f npha=%2d qual=%s epoch=%s %f evid=%d" % \
	(self.year, self.month, self.day, self.hour, self.min, self.sec, self.lat, self.lon, self.dep, \
	self.gap, self.rms, self.npha, self.quality, self.epoch, self.fracsec, self.evid)


  def moment_magnitude_message(self):
    # takes an event, and each phase with a moment determined (using external tools)
    # moment is in dyne-cm
    # magnitude is filled in 
    # mag_type is 'Mw'
    # returns a TYPE_MAGNITUDE message suitable for EW
    # mag type for Mw in EW is 2

    sta_dict = {}
    Mw = []

    for arrival in self.arrivals:
      sta_dict[arrival.sta+arrival.net] = 1
      if hasattr(arrival, 'magnitude'):
        Mw.append( arrival.magnitude )
      else:
        arrival.magnitude = -99.0
    nsta = len(sta_dict.keys())
    nchan = len(Mw)
    std_dev = numpy.std(Mw, ddof=1)
    med = numpy.median(Mw)
    msg = "%d MAG 2 MW %5.2f MED %d %d %f 1.00 -1.00 -1 014024255:028055255 1 0\n" % \
		(self.evid, med, nsta, nchan, std_dev)
    for arrival in self.arrivals:
      if arrival.magnitude != -99.0:
        msg = msg + "%s.%s.%s.%s %5.2f %6.2f 0.0 %e %f -1.0  -1.0 -1.0 -1.0\n" % \
	           (arrival.sta, arrival.chan, arrival.net, arrival.loc, arrival.magnitude, \
	            arrival.dist, arrival.moment, arrival.epoch)
    return msg

class arrival:
  def __init__(self):
    self.year=0
    self.month=0
    self.day=0
    self.hour=0
    self.min=0
    self.sec=0.0
    self.fracsec=0.0
    self.epoch=0
    self.net=""
    self.sta=""
    self.chan=""
    self.loc=""
    self.type="P"
    self.weight=0 # 0,1,2,3 with 0 being best (this is really an inverse quality)
    self.residual=0.0
    self.dist=0.0
    self.azi=-1
    self.toa=-900
    self.polarity=' '
    self.debug=True
    #self.debug=False

  def parse_eylon_phase_line(self, line):
    #sta Phase sec residual dist azi   ?
    #TP3 P  20.65   0.01  34.4  164   59
    self.sta = line[0:3].strip()
    self.sec = float(line[7:12])
    self.weight = 0
    self.type= line[4]
    self.residual= float(line[14:19])
    self.dist= float(line[21:25])
    if self.debug:
      self.print_phase()

  def parse_arc_phase_line(self, line):
    # example arc line:
    #O53A TA  BHZ P  0201310020001 2920  -8147    0   0   0      0 0  0   0   0  3111801  0 13.0 34104  0 558   0 D -- 0     
 
    self.sta = line[0:5].strip()
    print "parse_arc_phase_line: sta=[%s]" % self.sta
    if not self.sta:
      return False
    self.net = line[5:7]
    self.chan = line[9:12]
    self.loc = line[111:113]
    self.weight=int(line[16])
    self.year=int(line[17:21])
    self.month=int(line[21:23])
    self.day=int(line[23:25])
    self.hour=int(line[25:27])
    self.min=int(line[27:29])
    self.residual=float(line[34:38])/100.
    self.dist=float(line[74:78])/10.
    if line[46]=='S' or line[47]=='S':
      self.type='S'
      if not line[49] == ' ': 
        self.weight=int(line[49])
        self.sec=int(line[41:46])/100.
        self.residual=float(line[50:54])/100.
      else:
        self.weight=4
    else:
        # get the P arrival
        self.sec=int(line[29:34])/100.
    self.isec=int(self.sec)
    while self.isec >= 60:
        self.min += 1
        self.sec -= 60.
        self.isec -= 60
        if self.min >= 60:
            self.hour += 1
            self.min -= 60
            if self.hour >= 24:
                self.day+=1
    self.dist = int(line[75:78])/10.
    self.toa=int(line[78:81])
    try:
      self.azi=int(line[91:94])
    except:
      # do nothing
      a=1
    self.polarity=line[15]
    #print "%s.%s %d/%02d/%02d %02d:%02d:%02d" % (self.sta, self.chan, self.year, self.month, self.day, self.hour, self.min, self.isec)
    self.fracsec = self.sec - self.isec
    self.epoch=timegm(datetime(self.year, self.month, self.day, self.hour, self.min, self.isec).timetuple()) + self.fracsec
    if self.debug:
      self.print_phase()
    return True

  def print_phase(self):
    print "%s.%s.%s.%s phase=%s weight=%d residual=%5.2f dist=%6.1f %d/%02d/%02d %02d:%02d %5.2f epoch=%f" % \
	(self.net, self.sta, self.chan, self.loc, self.type, self.weight, self.residual, self.dist, self.year, self.month, self.day, self.hour, self.min, self.sec, self.epoch)
    print "toa=%d azi=%d first motion=%s" % (self.toa, self.azi, self.polarity)




"""
hypoinverse arc format
0123456789012345678901234567890123456789
201001312347357038 4938122 4633  286     8123  1   429379  76135 9  50 66     33    3  49  74  5      10     0       D  8 D 66 10         71034564D 66  10        2FNC01
ACR  BG  DPE    4201001312347             3691ES 2   7          31     -12  18144           34           138J  --
ACR  BG  DPZ IPU0201001312347 3635   1154        0                  -7      18144 5       3 34 22    872    JD --
JKR  BG  DPZ IPD0201001312347 3651  -1154        0                  -1      27131 5       3156 27    926    JD --
SQK  BG  DPZ IPD1201001312347 3648  -9 77        0                  -4      33124 5       5270 68    396    JD --
STY  BG  DPN    4201001312347             3679IS 1  -7          77      -2  13154          214           665J  --
        event.evid = int(line.strip())
STY  BG  DPZ IPU1201001312347 3629  -6 77        0                  -1      13154 5       6214 77     72    JD --
GDXB NC  HHN    4201001312347             3690IS 1   9          77     -32  26132          229           367J  --
GDXB NC  HHZ IPD0201001312347 3635   2154        0                 -18      26132 0       5229 66    560    JD --
                                                                71034564
"""

def parse_hinvarc_file(file):
  f=open(file, 'r')
  lines=f.readlines()
  events=[]
  on_sum=True
  on_phase=False
  for line in lines:
    print "processing line %s" % line
    if line[0] == '$':
      continue
    if on_sum:
      #print "as summary"
      event = hypo()
      event.parse_arc_summary_line(line)
      on_phase=True
      on_sum=False
      events.append(event)
      continue
    if on_phase:
      #print "as phase"
      phase=arrival()
      if phase.parse_arc_phase_line(line):
        event.arrivals.append(phase)
        continue
      else:
        # we reached the last line that contains the EVID as dbselect outputs it
        event.evid = int(line.strip())
        on_sum=True
        on_phase=False
  return events
    
def parse_eylon_summary_file(file):
  f=open(file, 'r')
  lines = f.readlines()
  event = hypo()
  event.parse_summary_line(lines[0])
  for phase_line in lines[1:]:
    phase=arrival()
    phase.parse_eylon_phase_line(phase_line)
    event.arrivals.append(phase)
  return event

def parse_pfile(ev, file):
  # parse the P file to get the weight for each phase used in the D file
  lines = open(file, 'r').readlines()
  for line in lines[1:]:
    # get the sta phase and weight
    #  A01  p    10.530  0.050 D
    if len(line) < 3:
      continue
    sta = line[1:4]
    phase = line[6].upper()
    wt = float(line[20:25])
    #print "sta=%s phase=%s wt=%5.3f" % (sta, phase, wt)
    for arrival in ev.arrivals:
      if arrival.sta == sta and arrival.type == phase:
         #print "match found for %s phase %s wt set at %f" % (sta, phase, wt)
         arrival.weight=wt
         break

    
def parse_pick_dir(dir):
  # only reads in those events that have D files (were located events)
  events=[]
  files=os.listdir(dir)
  for file in files:
    if file[-1:]=='d':
      e = parse_eylon_summary_file(dir+'/'+file)
      #print dir+'/'+file
      events.append(e)
      # now get the P file for weights
      parse_pfile(e, dir+'/'+file[:-1]+'p')
  return events

def find_S_phase(arrivals, sta):
  # returns arrival or None if no matching found
  for ph in arrivals:
    if sta == ph.sta and ph.type == 'S':
      return ph
  return None

def bayes_loc_arrivals(events):
  evid = 1
  for e in events:
    for ph in e.arrivals:
      print "%04d %4s %1s %9.2f" %\
        (evid, ph.sta, ph.type, ph.epoch)
    evid += 1

def bayes_loc_origin(events):
  evid = 1
  for e in events:
    print "%04d %f %f %f %f" % (evid, e.lat, e.lon, e.dep, e.epoch)
    evid += 1

def compute_vpvs(events):
  events_processed=0
  s_p_list = []
  p_list = []
  for e in events:
    #e.print_origin()
    #print "event has %d arrivals" % len(e.arrivals)
    if e.quality in ['B', 'C', 'D']:
      continue
    events_processed = events_processed+1
    for ph in e.arrivals:
      sta=ph.sta
      if ph.type=='P':
        phS = find_S_phase(e.arrivals, sta)
        if phS and phS.weight <= 0.1:
            # compute S-P and P travel time
            if phS.sec < ph.sec:
              continue
            s_p = phS.sec - ph.sec
            p   = ph.sec - e.sec 
            s_p_list.append(s_p)
            p_list.append(p)
            print "%f  %f %s" % (p, s_p, sta)

  a,b = numpy.polyfit(p_list, s_p_list, 1)
  sys.stderr.write("processed  %d A quality events out of %d total\n" % (events_processed, len(events)))
  sys.stderr.write("processed %d S-P times slope = %f intercept = %f\n" % (len(s_p_list), a, b))
  sys.stderr.write("VP/VS= %f\n" % (a+1))

  full = numpy.polyfit(p_list, s_p_list, 1, full=True)
  #pprint.pprint(full)

def get_residuals(events):
  pout = open("P_dist_vs_residual.txt", "w")
  sout = open("S_dist_vs_residual.txt", "w")
  for e in events:
    for p in e.arrivals:
      fout = pout
      if p.type == 'S':
        fout = sout    
      fout.write("%4.1f %3.2f\n" % (p.dist, p.residual))

def print_delays(res_dict, type):
  import scipy.stats
  print "%s delays" % type
  for SCN in res_dict:
    residuals = res_dict[SCN]
    delay=scipy.stats.tmean(residuals)
    print "%s %f" % (SCN, delay)

def compute_station_delays(events):
  P_resid = {}
  S_resid = {}
  for e in events:
    for p in e.arrivals:
      #key = p.net+'.'+p.sta+'.'+p.chan
      key = p.net+'.'+p.sta
      if p.type == 'S':
        if not key in S_resid:
          S_resid[key]=[]
        S_resid[key].append(p.residual)
      else:
        if not key in  P_resid:
          P_resid[key]=[]
        P_resid[key].append(p.residual)
  print_delays(P_resid, 'raw P')
  print_delays(S_resid, 'raw S')

def compute_weighted_station_delays(events):
  P_wt_resid_sum = {}
  S_wt_resid_sum = {}
  P_wt_count = {}
  S_wt_count = {}
  for e in events:
    for p in e.arrivals:
      #key = p.net+'.'+p.sta+'.'+p.chan
      key = p.net+'.'+p.sta
      wt = 1 - (p.weight * 0.25)
      if p.type == 'S':
        if not key in S_wt_resid_sum:
          S_wt_resid_sum[key] = 0.0
        S_wt_resid_sum[key] += p.residual*wt
        if not key in S_wt_count:
          S_wt_count[key] = 0.0
        S_wt_count[key] += wt
      else:
        if not key in  P_wt_resid_sum:
          P_wt_resid_sum[key]= 0.0
        P_wt_resid_sum[key] += p.residual*wt
        if not key in P_wt_count:
          P_wt_count[key] = 0.0
        P_wt_count[key] += wt
  print_weighted_delays(P_wt_resid_sum, P_wt_count, 'Weighted P')
  print_weighted_delays(S_wt_resid_sum, S_wt_count, 'Weighted S')

def kml_header():
# returns the kml_header string below
  return """<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2" xmlns:gx="http://www.google.com/kml/ext/2.2" xmlns:kml="http://www.opengis.net/kml/2.2" xmlns:atom="http://www.w3.org/2005/Atom">
<Document>
        <name>Hypoinverse Location</name>
        <Schema name="HypoinverseSummary" id="HypoSummary">
                <SimpleField type="string" name="Evid"><displayName>&lt;b&gt;Evid&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="string" name="Origin"><displayName>&lt;b&gt;Origin&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Lat"><displayName>&lt;b&gt;Lat&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Long"><displayName>&lt;b&gt;Long&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Depth"><displayName>&lt;b&gt;Depth&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="MAG"><displayName>&lt;b&gt;MAG (Md)&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="int" name="Number_Picks"><displayName>&lt;b&gt;Number Picks&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="int" name="Azimuthal_Gap"><displayName>&lt;b&gt;Azimuthal Gap&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Nearest_Station"><displayName>&lt;b&gt;Nearest Station&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="RMS"><displayName>&lt;b&gt;RMS&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Error_H"><displayName>&lt;b&gt;Error-H&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="double" name="Error_Z"><displayName>&lt;b&gt;Error-Z&lt;/b&gt;</displayName>
</SimpleField>
                <SimpleField type="string" name="Quality"><displayName>&lt;b&gt;Quality&lt;/b&gt;</displayName>
</SimpleField>
        </Schema>
        <StyleMap id="pointStyleMap">
                <Pair>
                        <key>normal</key>
                        <styleUrl>#hlightPointStyle</styleUrl>
                </Pair>
                <Pair>
                        <key>highlight</key>
                        <styleUrl>#normPointStyle</styleUrl>
                </Pair>
        </StyleMap>
        <Style id="normPointStyle">
                <IconStyle>
                        <color>ff00ffff</color>
                        <scale>2.0</scale>
                        <Icon>
                                <href>http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png</href>
                        </Icon>
                </IconStyle>
                <BalloonStyle>
                        <text><![CDATA[<table border="0">
  <tr><td><b>Evid</b></td><td>$[HypoinverseSummary/Evid]</td></tr>
  <tr><td><b>Origin</b></td><td>$[HypoinverseSummary/Origin]</td></tr>
  <tr><td><b>Lat</b></td><td>$[HypoinverseSummary/Lat]</td></tr>
  <tr><td><b>Long</b></td><td>$[HypoinverseSummary/Long]</td></tr>
  <tr><td><b>Depth</b></td><td>$[HypoinverseSummary/Depth]</td></tr>
  <tr><td><b>MAG (Md)</b></td><td>$[HypoinverseSummary/MAG]</td></tr>
  <tr><td><b>Number Picks</b></td><td>$[HypoinverseSummary/Number_Picks]</td></tr>
  <tr><td><b>Azimuthal Gap</b></td><td>$[HypoinverseSummary/Azimuthal_Gap]</td></tr>
  <tr><td><b>Nearest Station</b></td><td>$[HypoinverseSummary/Nearest_Station]</td></tr>
  <tr><td><b>RMS</b></td><td>$[HypoinverseSummary/RMS]</td></tr>
  <tr><td><b>Error-H</b></td><td>$[HypoinverseSummary/Error_H]</td></tr>
  <tr><td><b>Error-Z</b></td><td>$[HypoinverseSummary/Error_Z]</td></tr>
  <tr><td><b>Quality</b></td><td>$[HypoinverseSummary/Quality]</td></tr>
</table>
]]></text>
                </BalloonStyle>
                <ListStyle>
                </ListStyle>
        </Style>
        <Style id="hlightPointStyle">
                <IconStyle>
                        <color>ff0000ff</color>
                        <scale>0.6</scale>
                        <Icon>
                                <href>http://maps.google.com/mapfiles/kml/shapes/shaded_dot.png</href>
                        </Icon>
                </IconStyle>
                <BalloonStyle>
                        <text><![CDATA[<table border="0">
  <tr><td><b>Origin</b></td><td>$[HypoinverseSummary/Origin]</td></tr>
  <tr><td><b>Lat</b></td><td>$[HypoinverseSummary/Lat]</td></tr>
  <tr><td><b>Long</b></td><td>$[HypoinverseSummary/Long]</td></tr>
  <tr><td><b>Depth</b></td><td>$[HypoinverseSummary/Depth]</td></tr>
  <tr><td><b>MAG (Md)</b></td><td>$[HypoinverseSummary/MAG]</td></tr>
  <tr><td><b>Number Picks</b></td><td>$[HypoinverseSummary/Number_Picks]</td></tr>
  <tr><td><b>Azimuthal Gap</b></td><td>$[HypoinverseSummary/Azimuthal_Gap]</td></tr>
  <tr><td><b>Nearest Station</b></td><td>$[HypoinverseSummary/Nearest_Station]</td></tr>
  <tr><td><b>RMS</b></td><td>$[HypoinverseSummary/RMS]</td></tr>
  <tr><td><b>Error-H</b></td><td>$[HypoinverseSummary/Error_H]</td></tr>
  <tr><td><b>Error-Z</b></td><td>$[HypoinverseSummary/Error_Z]</td></tr>
  <tr><td><b>Quality</b></td><td>$[HypoinverseSummary/Quality]</td></tr>
</table>
]]></text>
                </BalloonStyle>
                <ListStyle>
                </ListStyle>
        </Style>
"""


def kml_tail():
  return " </Document></kml> "

def print_weighted_delays(res_dict, wt_dict, type):
  import scipy.stats
  print "%s delays" % type
  for SCN in res_dict:
    delay = res_dict[SCN]/wt_dict[SCN]
    Net, Sta = SCN.split('.')
    print "%-5s %-2s %5.2f  " % (Sta, Net, delay)


# format for fpfit.dat, just P arrivals
#  DATE    ORIGIN   LATITUDE LONGITUDE  DEPTH    MAG NO           RMS
# 15 9 4  121  0.47 18s 1.58 124e 43.9    3.6    1.0 23          0.11            
# 
#  STN  DIST  AZ TOA PRMK HRMN  PSEC TPOBS              PRES  PWT
# VS04     1  51 167  P    121  1.8   1.30              0.14  0.50               
# VS03     1 144 167  PD   121  1.8   1.32              0.16  1.00    
def print_fpfit_data(ev):
  print "  DATE    ORIGIN   LATITUDE LONGITUDE  DEPTH    MAG NO           RMS"
  print " %02d%2d%2d %02d%02d %5.2f %2d%c%5.2f %3d%c%5.1f  %5.1f    %3.1f %2d          %4.2f" %\
      (ev.year-2000, ev.month, ev.day, ev.hour, ev.min, ev.sec, \
       ev.lat_deg, ev.lat_char, ev.lat_min, \
       ev.lon_deg, ev.lon_char, ev.lon_min, \
       ev.dep, ev.mag, ev.npha, ev.rms)
  print"\n  STN  DIST  AZ TOA PRMK HRMN  PSEC TPOBS              PRES  PWT"
  for ph in ev.arrivals:
    if ph.type == 'P':
      pol = ' '
      # IMPORTANT note sei2ew inverted polarity, so if using ARC files from sei2ew, flip polarity back for fpfit
      if ph.polarity=='D':
        pol = 'C'
      if ph.polarity=='U':
        pol = 'D'
      
      print " %4s  %4d %3d %3d  P%c  %02d%02d %4.1f  %5.2f             %5.2f  %4.2f" % \
       (ph.sta, int(ph.dist), ph.azi, ph.toa, pol, ph.hour, ph.min, ph.sec, ph.sec-ev.sec,ph.residual, (4-ph.weight)/4.0)


def printf(format, *args):
    sys.stdout.write(format % args)
