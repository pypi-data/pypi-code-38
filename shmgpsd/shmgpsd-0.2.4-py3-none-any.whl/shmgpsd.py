import ctypes as ct
import sys

GPSD_SHM_KEY = 0x47505344
SHM_RDONLY   = 0x010000

MAXCHANNELS  = 120
MAXUSERDEVS  =   4
GPS_PATH_MAX = 128
HEXDATA_MAX  = 512

gpsd    = ct.CDLL( '/usr/local/lib/libgps.so' )
librt   = ct.CDLL( 'librt.so', use_errno=True )

gps_mask_t  = ct.c_uint64
timestamp_t = ct.c_double

class ecef_t( ct.Structure ):
  _fields_ = [ ( "x",    ct.c_double ),
               ( "y",    ct.c_double ),
               ( "z",    ct.c_double ),
               ( "pAcc", ct.c_double ),
               ( "vx",   ct.c_double ),
               ( "vy",   ct.c_double ),
               ( "vz",   ct.c_double ),
               ( "vAcc", ct.c_double ) ]

class gps_fix_t( ct.Structure ):
  _fields_ = [ ( "time",           timestamp_t    ),
               ( "mode",           ct.c_int       ),
               ( "ept",            ct.c_double    ),      
               ( "latitude",       ct.c_double    ),
               ( "epy",            ct.c_double    ),
               ( "longitude",      ct.c_double    ),
               ( "epx",            ct.c_double    ),
               ( "altitude",       ct.c_double    ),
               ( "epv",            ct.c_double    ), 
               ( "track",          ct.c_double    ),
               ( "epd",            ct.c_double    ),
               ( "speed",          ct.c_double    ), 
               ( "eps",            ct.c_double    ),
               ( "climb",          ct.c_double    ),
               ( "epc",            ct.c_double    ),
               ( "magnetic_track", ct.c_double    ),
               ( "ecef",           ecef_t         ) ]

class dop_t( ct.Structure ):
  _fields_ = [ ( "xdop", ct.c_double ),
               ( "ydop", ct.c_double ),
               ( "pdop", ct.c_double ),
               ( "hdop", ct.c_double ),
               ( "vdop", ct.c_double ),
               ( "tdop", ct.c_double ),
               ( "gdop", ct.c_double ) ]

class satellite_t( ct.Structure ):
  _fields_ = [ ( "ss",        ct.c_double ),
               ( "used",      ct.c_bool ),
               ( "PRN",       ct.c_short ),
               ( "elevation", ct.c_short ),
               ( "azimuth",   ct.c_short ),
               ( "gnssid",    ct.c_ubyte ),
               ( "svid",      ct.c_ubyte ),
               ( "sigid",     ct.c_ubyte ),
               ( "freqid",    ct.c_ubyte ) ]

class devconfig_t( ct.Structure ):
  _fields_ = [ ( "path",        ct.c_char * GPS_PATH_MAX ),
               ( "flags",       ct.c_int                 ),
               ( "driver",      ct.c_char * 64           ),
               ( "subtype",     ct.c_char * 96           ),
               ( "hexdata",     ct.c_char * HEXDATA_MAX  ),
               ( "activated",   ct.c_double              ),
               ( "baudrate",    ct.c_uint                ),
               ( "stopbits",    ct.c_uint                ),
               ( "parity",      ct.c_char                ),
               ( "cycle",       ct.c_double              ),
               ( "minicycle",   ct.c_double              ),
               ( "driver_mode", ct.c_int                 ) ]

class gps_policy_t( ct.Structure ):
  _fields_ = [ ( "watcher",  ct.c_bool                ),
               ( "json",     ct.c_bool                ),
               ( "nmea",     ct.c_bool                ),
               ( "raw",      ct.c_int                 ),
               ( "scaled",   ct.c_bool                ),
               ( "timing",   ct.c_bool                ),
               ( "split24",  ct.c_bool                ),
               ( "pps",      ct.c_bool                ),
               ( "loglevel", ct.c_int                 ),
               ( "devpath",  ct.c_char * GPS_PATH_MAX ),
               ( "remote",   ct.c_char * GPS_PATH_MAX ) ]

class devices_t( ct.Structure ):
  _fields_ = [ ( "time",     timestamp_t ),
               ( "ndevices", ct.c_int ),
               ( "list",     devconfig_t * MAXUSERDEVS ) ]

class gps_data_t( ct.Structure ):
  _fields_ = [ ( "set",                gps_mask_t                ),
               ( "online",             timestamp_t               ), 
               ( "gps_fd",             ct.c_void_p               ),
               ( "fix",                gps_fix_t                 ),
               ( "separation",         ct.c_double               ),
               ( "status",             ct.c_int                  ),
               ( "satellites_used",    ct.c_int                  ),
               ( "dop",                dop_t                     ),
               ( "epe",                ct.c_double               ),
               ( "skyview_time",       timestamp_t               ),
               ( "satellites_visible", ct.c_int                  ),
               ( "skyview",            satellite_t * MAXCHANNELS ),
               ( "dev",                devconfig_t               ),
               ( "policy",             gps_policy_t              ),
               ( "devices",            devices_t                 ),
               ( "gps_data_union",     ct.c_byte * 6240          ), 
               ( "privdata",           ct.c_void_p               ) ]

class shmexport_t( ct.Structure ):
  _fields_ = [ ( "bookend1", ct.c_int  ),
               ( "gpsdata",  gps_data_t), 
               ( "bookend2", ct.c_int  ) ]

def SHM():
  librt.shmget.restype  = ct.c_int
  librt.shmget.argtypes = [ ct.c_int, ct.c_size_t, ct.c_int ]
  librt.shmat.restype  = ct.c_void_p
  librt.shmat.argtypes = [ ct.c_int, ct.c_void_p, ct.c_int ]

  shmexport_p = ct.POINTER( shmexport_t )

  # We just need to read so no permissions needed.
  shmid = librt.shmget( GPSD_SHM_KEY, 0, 0 )
  if shmid == -1:
    c_errno = ct.get_errno()
    print( "shmget failed with errno: {0}".format( c_errno ) )
    sys.exit( c_errno )
  shm = librt.shmat( shmid, 0, SHM_RDONLY )
  if shm == -1:
    c_errno = ct.get_errno()
    print( "shmat failed with errno: {0}".format( c_errno ) )
    sys.exit( c_errno )

  # Both shared memory functions worked, so let's cast it.
  cast_p = ct.cast( shm, shmexport_p )

  # Return this so we don't have to type the whole struct down
  # to get information.
  return cast_p.contents.gpsdata
