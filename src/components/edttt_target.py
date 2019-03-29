#PTT Transport driver for target/bridge
# Any PTT Transport shall implement the following API:
#   __init__(args)
#   connect()
#   send(idx, message)
#   recv(idx, number_bytes, timeout)
#   wait(time)
#   close() 
#   get_time()
#   n_devices : Number of devices it is connected to

import struct;
import os;
import signal;
import stat;
import time

def create_dir(folderpath):
    if not os.path.exists(folderpath):
        if ( os.mkdir( folderpath , stat.S_IRWXG | stat.S_IRWXU ) != 0 ) \
            and ( os.access( folderpath, os.F_OK ) == False ):
          raise Exception("Cannot create folder %s"% folderpath);

def create_com_folder(session_id):
    import getpass
    Com_path = "/tmp/ptt_" + getpass.getuser();
    create_dir(Com_path);
    Com_path = Com_path + "/" + session_id;
    create_dir(Com_path);
    return Com_path;

def Create_FIFO_if_not_there(FIFOName):
    #we try to create a fifo which may already exist, and/or that some other
    #program may be racing to create at the same time
    if ( os.access( FIFOName, os.F_OK ) == False ) \
       and ( os.mkfifo(FIFOName,  stat.S_IRWXG | stat.S_IRWXU) != 0) \
       and ( os.access( FIFOName, os.F_OK ) == False ):
      raise Exception("Could not create FIFO %s", FIFOName);

class PTTT_target_bridge:
    n_devices = 0
    devices = [None, None, None]

    def __init__(self, args, TraceClass):
        self.args  = args
        self.Trace = TraceClass
        self.num_devices = int(self.args.num_devices)
    
    def connect(self):
        for nbr in range(self.num_devices):
            self.args.bridge_device_nbr = nbr
            self.devices[nbr] = PTTT_target(self.args, self.Trace)
            self.devices[nbr].connect()
            self.n_devices += 1 if self.devices[nbr].Connected else 0

    def send(self, idx, message):
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i" %idx);
        self.devices[idx].send(message)

    def recv(self, idx, number_bytes, to=None):
        if (idx > self.n_devices -1):
            raise Exception("Trying to access unconnected device %i" %idx);
        return self.devices[idx].recv(number_bytes, to)

    def wait(self, delay_in_ms):
        time.sleep(delay_in_ms/1000)

    def close(self):
        for nbr in range(self.num_devices):
            self.devices[nbr].close()

    def get_time(self):
        # TODO: Implement time keeping if needed
        return 0


class PTTT_target:
    IDX_IN  = 0
    IDX_OUT = 1
    FIFOs = [-1, -1]
    FIFOnames = [ "" , "" ]
    verbosity = 0
    Connected = False
    Cleaned = False
    n_devices = 0

    def __init__(self, args, TraceClass):

        self.Trace = TraceClass;
        #TODO: add some nice check and raise a proper error if an arg is missing 
        self.device_nbr = args.bridge_device_nbr;
        self.sim_id = args.sim_id;

    def connect(self):
        Com_path = create_com_folder(self.sim_id);

        self.Trace.trace(3,"Connecting to PTT proxy for device %s..."% self.device_nbr)

        #Note that python ignores SIGPIPE by default

        self.FIFOnames[self.IDX_IN] = \
            Com_path + "/device" + str(self.device_nbr) + ".in";
        self.FIFOnames[self.IDX_OUT] = \
            Com_path + "/device" + str(self.device_nbr) + ".out";

        Create_FIFO_if_not_there(self.FIFOnames[self.IDX_IN]);
        Create_FIFO_if_not_there(self.FIFOnames[self.IDX_OUT]);

        self.FIFOs[self.IDX_OUT] = os.open(self.FIFOnames[self.IDX_OUT], os.O_WRONLY);
        self.FIFOs[self.IDX_IN] = os.open(self.FIFOnames[self.IDX_IN], os.O_RDONLY);

        if (self.FIFOs[self.IDX_OUT] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.IDX_OUT]);

        if (self.FIFOs[self.IDX_IN] == -1):
            raise Exception("Could not open FIFO %s"% self.FIFOnames[self.IDX_IN]);

        self.Connected = True;
        self.Trace.trace(4,"Connected");

    def cleanup(self):
        if self.Cleaned:
            return
        self.Trace.trace(4,"Cleaning up transport");
        try:
            os.close(self.FIFOs[self.IDX_OUT]);
            self.Trace.trace(9,"Closed out FIFO");
            os.close(self.FIFOs[self.IDX_IN]);
            self.Trace.trace(9,"Closed in FIFO");
            os.remove(self.FIFOnames[self.IDX_OUT]);
            os.remove(self.FIFOnames[self.IDX_IN]);
            self.Cleaned = True
        except OSError:
            self.Trace.trace(9,"(minor) Error closing FIFO (most likely file does not exist yet)")

    def disconnect(self):
        if self.Connected:
            #self.Trace.trace(4,"Disconnecting bridge")
            #self.ll_send(struct.pack('<B', self.COM_DISCONNECT));
            self.Connected = False;

    def close(self):
        self.disconnect();
        self.cleanup();

    def ll_send(self, content):
        try:
            written = os.write(self.FIFOs[self.IDX_OUT], content);
            if written != len(content):
                raise;
        except:
            self.Trace.trace(4,"The PTT bridge disapeared when trying to write "
                             "to it");
            self.cleanup();
            raise Exception("Disconnected");

    def ll_recv(self, nbytes):
        try:
            pkt = os.read(self.FIFOs[self.IDX_IN], nbytes);
            if len(pkt) == 0:
                raise;
            return pkt;
        except:
           self.Trace.trace(4,"The PTT bridge disapeared when trying to read "
                              "from it");
           self.cleanup();
           raise Exception("Disconnected");

    def send(self, message):
        # send the packet
        self.ll_send(message)
        # a send is immediate (no time advance)

    def read(self, nbytes):
      received_nbytes = 0;
      packet ="";
      #print "Will try to pick " + str(nbytes) + " bytes"
      while ( len(packet) < nbytes):
        packet += self.ll_recv(nbytes - received_nbytes);
        #print "Got so far " + str(len(packet)) + " bytes"
        #print 'packet: "' + repr(packet) + '"' 
      return packet;

    def recv(self, number_bytes, to=None):
        #print ("PTT: ("+str(idx)+") request rcv of "+ str(number_bytes) + " bytes; to = " + str(to));
        if to == None:
            to = self.default_to
        if ( number_bytes == 0 ):
          return ""

        packet = self.read(number_bytes)
        if (len(packet) != number_bytes):
          raise Exception("very weird..")
        #print "packet itself =" + repr(packet)

        return packet
