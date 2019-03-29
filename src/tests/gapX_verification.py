# -*- coding: utf-8 -*-
import random;
import statistics;
import os;
import numpy;
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.preambles import *;
from components.addata import *;
from components.attdata import *; 

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

def attRequest(transport, initiator, txData, trace):
    status = le_data_write(transport, initiator.initiator, initiator.handles[0], 0, 0, txData, 100);
    trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
    success = status == 0;
    dataSent = False;

    while success and not dataSent:
        dataSent = has_event(transport, initiator.initiator, 100);
        success = success and dataSent;
        if dataSent:
            event, subEvent, eventData = get_event(transport, initiator.initiator, 100)[1:];
            showEvent(event, eventData, trace);
            dataSent = event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS;

    return dataSent;

def attResponse(transport, initiator, trace):
    success, rxData = True, [];

    while success:
        dataReady = le_data_ready(transport, initiator.initiator, 100);
        success = success and dataReady;
        if dataReady:
            rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, initiator.initiator, 100)[2:];
            trace.trace(6, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
            rxData += rxDataPart;

    return (len(rxData) > 0), rxData;

def discoverService(transport, initiator, serviceUUID, trace):
    services = {};
    services["handles"] = [];
    services["uuids"] = [];
    attData = ATTData();

    success, handle = True, 1;
    while success:
        txData = attData.encode( ATTOpcode.ATT_FIND_BY_TYPE_VALUE_REQUEST, handle, 0xffff, 0x2800, toArray( serviceUUID, 2 if serviceUUID <= 0xFFFF else 16 ) );
        success = attRequest( transport, initiator, txData, trace );
        if success:
            success, rxData = attResponse( transport, initiator, trace );
            if success:
                reply = attData.decode( rxData );
                success = reply["opcode"] == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_RESPONSE;
                if success:
                    services["handles"] += [ reply["handle"] ];
                    services["uuids"] += [ serviceUUID ];
                    handle = reply["handle"][-1] + 1;
                    success = handle < 0x10000;

    return services;

def discoverAllServices(transport, initiator, trace):
    services = {};
    services["handles"] = [];
    services["uuids"] = [];
    attData = ATTData();

    success, handle = True, 1;
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_GROUP_TYPE_REQUEST, handle, 0xffff, 0x2800 );
        success = attRequest( transport, initiator, txData, trace );
        if success:
            success, rxData = attResponse( transport, initiator, trace );
            if success:
                reply = attData.decode( rxData );
                success = reply["opcode"] == ATTOpcode.ATT_READ_BY_GROUP_TYPE_RESPONSE;
                if success:
                    for first, last, uuid in zip(reply["first_handle"], reply["last_handle"], reply["value"]):
                        services["handles"] += [ [ first, last ] ];
                        services["uuids"] += [ toNumber(uuid) ];
                    handle = reply["last_handle"][-1] + 1;
                    success = handle < 0x10000;

    return services;

def discoverCharacteristic(transport, initiator, handles, characteristicUUID, trace):
    characteristic = {};
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, handles[0], handles[1], characteristicUUID );
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = reply["opcode"] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;
            if success:
	        characteristic["handle"] = reply["handle"];
	        characteristic["value"] = reply["value"];

    return success, characteristic;

def discoverAllCharacteristics(transport, initiator, handles, trace):
    characteristics = {};
    characteristics["handle"] = [];
    characteristics["property"] = [];
    characteristics["value_handle"] = [];
    characteristics["uuid"] = [];
    attData = ATTData();

    handle = handles[0];
    success = True;
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, handle, handles[1], 0x2803 );
        success = attRequest( transport, initiator, txData, trace );
        if success:
            success, rxData = attResponse( transport, initiator, trace );
            if success:
                reply = attData.decode( rxData );
                success = reply["opcode"] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;
                if success:
                    for _handle, value in zip(reply["handle"], reply["value"]):
                        characteristics["handle"] += [ _handle ];
                        characteristics["property"] += [ value[0] ];
                        characteristics["value_handle"] += [ toNumber(value[1:3]) ];
                        characteristics["uuid"] += [ toNumber(value[3:]) ];
                    handle = reply["handle"][-1] + 1;

    return characteristics;

def readCharacteristic(transport, initiator, handle, trace):
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_REQUEST, handle );
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = reply["opcode"] == ATTOpcode.ATT_READ_RESPONSE;

    return success, reply["value"] if success else [];

def readStringCharacteristic(transport, initiator, handle, trace):
    success, data = readCharacteristic(transport, initiator, handle, trace);

    return success, ''.join([chr(_) for _ in data]).decode('utf-8') if success else '';

def writeCharacteristic(transport, initiator, handle, data, trace):
    attData = ATTData();
    reply = { "opcode", ATTOpcode.ATT_WRITE_RESPONSE };

    txData = attData.encode( ATTOpcode.ATT_WRITE_REQUEST, handle, data );
    success = attRequest( transport, initiator, txData, trace );
    """
        Normally there is no Response to a ATT_WRITE_REQUEST, but we could get an ATT_ERROR_RESPONSE...
    """
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            success = False;

    return success, reply;

def valueHandle(characteristics, uuid):
    handle = -1;
    for value_handle, char_uuid in zip(characteristics["value_handle"], characteristics["uuid"]):
        if char_uuid == uuid:
            handle = value_handle;
            break;
    return handle;

def peerAddress(transport, upperTester, trace):
    success, addressType, address = False, SimpleAddressType.PUBLIC, [ 0 for _ in range(6) ];
    
    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);
        """
            Start Scanner to obtain address of peer
        """
        success = scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        """
            Obtain address of Advertiser
        """
        if success:
            addressType, address = advertiseReport(scanner.reportData)[2:4];

    except Exception as e: 
        trace.trace(3, "Failed to obtain peer Address: %s" % str(e));
        success = False;

    return success, addressType, address;

"""
    GAP/GAT/BV-01-C [GAP Mandatory Characteristics]
"""
def gap_gat_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-01-C [GAP Mandatory Characteristics]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            attData = ATTData();
            service = discoverService(transport, initiator, 0x1800, trace);
            service["characteristics"] = [];
            """
                Fetch all Characteristics in the Generic Access Service...
            """
            for handles in service["handles"]:
                service["characteristics"] += [ discoverAllCharacteristics(transport, initiator, handles, trace) ];
	     
            for handles, uuid, characteristic in zip(service["handles"], service["uuids"], service["characteristics"]):
                trace.trace(9, "Service with UUID: %s handle-range [%d, %d]" % (attData.uuid(uuid), handles[0], handles[1]));
                for char_handle, property_value, value_handle, char_uuid in zip(characteristic["handle"], characteristic["property"], characteristic["value_handle"], characteristic["uuid"]):
                    trace.trace(9, "   Characteristic handle: %2d property: %2d value handle: %2d UUID: %s" % (char_handle, property_value, value_handle, attData.uuid(char_uuid)));

	    handle = valueHandle(service["characteristics"][0], 0x2A00);
            success = success and (handle > 0);
            if handle > 0:
                success, name = readStringCharacteristic(transport, initiator, handle, trace);
                success = success and (name == 'MFi peripheral');
                trace.trace(6,"Device Name: %s" % name);

            handle = valueHandle(service["characteristics"][0], 0x2A01);
            success = success and (handle > 0);
            if handle > 0:
	        success, data = readCharacteristic(transport, initiator, handle, trace);
                appearance = toNumber( data );
                success = success and (appearance == 833);
                trace.trace(6,"Appearance: %d" % appearance);

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "GAP Mandatory Characteristics test failed: %s" % str(e));
        success = False;

    trace.trace(2, "GAP Mandatory Characteristics test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/GAT/BV-02-C [GAP Peripheral Privacy Flag Characteristic]
"""
def gap_gat_bv_02_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-02-C [GAP Peripheral Privacy Flag Characteristic]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            service = discoverService(transport, initiator, 0x1800, trace);
            """
                Fetch the Peripheral Privacy Flag Characteristic
            """
            success, characteristic = discoverCharacteristic(transport, initiator, service["handles"][0], 0x2A02, trace);
	    if success:
                flag = characteristic["value"][0]            
                trace.trace(6,"Peripheral Privacy Flag: %d" % flag);
            else:
                trace.trace(6,"Peripheral Privacy Flag: Not present!");

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "GAP Peripheral Privacy Flag Characteristic test failed: %s" % str(e));
        success = False;

    trace.trace(2, "GAP Peripheral Privacy Flag Characteristic test " + ("PASSED" if success else "FAILED"));

    return success;

"""
    GAP/GAT/BV-03-C [GAP Reconnection Address Characteristic]
"""
def gap_gat_bv_03_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-03-C [GAP Reconnection Address Characteristic]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            service = discoverService(transport, initiator, 0x1800, trace);
            """
                Fetch the Reconnection Address Characteristic
            """
            success, characteristic = discoverCharacteristic(transport, initiator, service["handles"][0], 0x2A03, trace);
	    if success:
                data = characteristic["value"][0];
                trace.trace(6,"Reconnection Address: %s" % formatAddress( data ));
            else:
                trace.trace(6,"Reconnection Address: Not present!");

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "GAP Reconnection Address Characteristic test failed: %s" % str(e));
        success = False;

    trace.trace(2, "GAP Reconnection Address Characteristic test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/GAT/BV-04-C [Peripheral Preferred Connection Parameters Characteristic]
"""
def gap_gat_bv_04_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-04-C [Peripheral Preferred Connection Parameters Characteristic]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            service = discoverService(transport, initiator, 0x1800, trace);
            """
                Fetch the Peripheral Preferred Connection Parameters Characteristic
            """
            success, characteristic = discoverCharacteristic(transport, initiator, service["handles"][0], 0x2A04, trace);
	    if success:
                data = characteristic["value"][0];
                trace.trace(6,"Peripheral Preferred Connection Parameters:");
                trace.trace(6,"Minimum Connection Interval: %d" % toNumber( data[0:2] ));
                trace.trace(6,"Maximum Connection Interval: %d" % toNumber( data[2:4] ));
                trace.trace(6,"              Slave Latency: %d" % toNumber( data[4:6] ));
                trace.trace(6,"Connection Supervision Timeout Multiplier: %d" % toNumber( data[6:8] ));
            else:
                trace.trace(6,"Peripheral Preferred Connection Parameters: Not present!");

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;
            if not connected:
                """
                    Attempt to reconnect with proposed connection parameters
                """
                initiator.intervalMin = toNumber( data[0:2] );
                initiator.intervalMax = toNumber( data[2:4] );
                initiator.latency     = toNumber( data[4:6] );
                initiator.supervisionTimeout = toNumber( data[6:8] );

                connected = initiator.connect();
                success = success and connected;
                if connected:
                    connected = not initiator.disconnect(0x3E)
                    success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Peripheral Preferred Connection Parameters Characteristic test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Peripheral Preferred Connection Parameters Characteristic test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/GAT/BV-05-C [Writable Device Name]
"""
def gap_gat_bv_05_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-05-C [Writable Device Name]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            service = discoverService(transport, initiator, 0x1800, trace);
            """
                Fetch the Device Name Characteristic
            """
            success, characteristic = discoverCharacteristic(transport, initiator, service["handles"][0], 0x2A00, trace);
	    if success:
                handle = characteristic["handle"][0];
                data = characteristic["value"][0];
                name = ''.join([chr(_) for _ in data]).decode('utf-8');
                trace.trace(6,"Device Name: %s" % name);

                setName = u'Rødgrød & Blåbær med fløde'.encode('UTF-8');
                data = [ ord(_) for _ in setName ];
                success, reply = writeCharacteristic(transport, initiator, handle, data, trace);
                
                if success:
                    success, gotName = readStringCharacteristic(transport, initiator, handle, trace);
                    trace.trace(6,"Device Name: %s" % gotName);
                    success = success and (gotName == setName);
                else:
                    if reply["opcode"] == ATTOpcode.ATT_ERROR_RESPONSE:
                        trace.trace(6,"Failed to write Device Name - error code: %d - %s" % (reply["error"], ATTData().error(reply["error"])) );
                    else:
                        trace.trace(6,"Failed to write Device Name - unknown reply: %d" % reply["opcode"]);
            else:
                trace.trace(6,"Device Name: Not present!");

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Writable Device Name test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Writable Device Name test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/GAT/BX-01-C [Discover All Services]
"""
def gap_gat_bx_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BX-01-C [Discover All Services]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Discover all Services
            """
            attData = ATTData();
            services = discoverAllServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                characteristics = discoverAllCharacteristics(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                    trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover All Services test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Discover All Services test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/IDLE/NAMP/BV-01-C [Name Discovery Procedure GATT Client]
"""
def gap_idle_namp_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/IDLE/NAMP/BV-01-C [Name Discovery Procedure GATT Client]");

    try:
        """
            Obtain address of Advertiser
        """
        success, addressType, address = peerAddress(transport, upperTester, trace);
        if not success:
            raise UnboundLocalError('Failed to obtain peer Address');

        trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
        """
            Initiate connection with Advertiser
        """
        initiator = Initiator(transport, upperTester, None, trace, Address( ExtendedAddressType.PUBLIC ), Address( addressType, address ));
        connected = initiator.connect();
        success = success and connected;
        if connected:
            """
                Lookup the Generic Access Service (0x1800)
            """
            service = discoverService(transport, initiator, 0x1800, trace);
            """
                Fetch the Device Name Characteristic
            """
            success, characteristic = discoverCharacteristic(transport, initiator, service["handles"][0], 0x2A00, trace);
	    if success:
                data = characteristic["value"][0];
                name = ''.join([chr(_) for _ in data]).decode('utf-8');
                trace.trace(6,"Device Name: %s" % name);
            else:
                trace.trace(6,"Device Name: Not present!");

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Name Discovery Procedure GATT Client test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Name Discovery Procedure GATT Client test " + ("PASSED" if success else "FAILED"));
    return success;

__tests__ = { 
    "GAP/GAT/BV-01-C":       gap_gat_bv_01_c,       # [GAP Mandatory Characteristics]
    "GAP/GAT/BV-02-C":       gap_gat_bv_02_c,       # [GAP Peripheral Privacy Flag Characteristic]
    "GAP/GAT/BV-03-C":       gap_gat_bv_03_c,       # [GAP Reconnection Address Characteristic]
    "GAP/GAT/BV-04-C":       gap_gat_bv_04_c,       # [Peripheral Preferred Connection Parameters Characteristic]
    "GAP/GAT/BV-05-C":       gap_gat_bv_05_c,       # [Writable Device Name]
    "GAP/IDLE/NAMP/BV-01-C": gap_idle_namp_bv_01_c, # [Name Discovery Procedure GATT Client]
    "GAP/GAT/BX-01-C":       gap_gat_bx_01_c        # [Discover All Services]
};

def preamble(transport, trace):
    global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

    ok = success = preamble_standby(transport, 0, trace);
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;            
    return ok;          
    
def runTest(test, transport, trace):
    global __tests__;
    
    passed = failed = 0;

    if test.lower() == "all":
        for test in __tests__:
            success = preamble(transport, trace);
            trace.trace(4, "");
            success = success and __tests__[test](transport, 0, trace);

            passed += 1 if success else 0;
            failed += 0 if success else 1;

            trace.trace(4, "");

    elif test in __tests__:
        success = preamble(transport, trace);
        success = success and __tests__[test](transport, 0, trace);
        
        passed += 1 if success else 0;
        failed += 0 if success else 1;

    elif os.path.isfile(test):
        file = open(test, "r");
        for line in file:
            test = line.strip().upper();
            if test in __tests__:
                success = preamble(transport, trace);
                trace.trace(4, "");
                success = success and __tests__[test](transport, 0, trace);

                passed += 1 if success else 0;
                failed += 0 if success else 1;

                trace.trace(4, "");
        file.close();

    else:
        trace.trace(1, "Test '%s' not found!" % test);
        
        failed += 1;

    if (passed + failed) > 1:
        trace.trace(1, "\nSummary:\n\nStatus   Count\n%s" % ('='*14));
        if passed > 0:
            trace.trace(1, "PASS%10d" % passed);
        if failed > 0:
            trace.trace(1, "FAIL%10d" % failed);
        trace.trace(1, "%s\nTotal%9d" % ('='*14, passed + failed));
        
    return (failed == 0);

"""
    Return the specification which contains information about the test suite
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Generic Access Profile (GAP) Test Suite",
                    number_devices = 1,
                    description = "Qualification of GAP.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    success = runTest("all" if args.case is None else args.case, transport, trace);
    return 0 if success else -1;
