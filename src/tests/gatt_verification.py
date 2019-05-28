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
from components.smpdata import *;
from components.pairing import *;
from components.gattdata import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

def attRequest(transport, initiator, txData, trace):
    status = le_data_write(transport, initiator.initiator, initiator.handles[0], 0, 0, txData, 100);
    trace.trace(10, "LE Data Write Command returns status: 0x%02X" % status);
    success = status == 0;
    dataSent = False;

    while success and not dataSent:
        dataSent = has_event(transport, initiator.initiator, 100);
        success = success and dataSent;
        if dataSent:
            event, subEvent, eventData = get_event(transport, initiator.initiator, 100)[1:];
            # showEvent(event, eventData, trace);
            dataSent = event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS;

    return dataSent;

def attResponse(transport, initiator, trace):
    success, rxData = True, [];

    while success:
        dataReady = le_data_ready(transport, initiator.initiator, 100);
        success = success and dataReady;
        if dataReady:
            rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, initiator.initiator, 100)[2:];
            trace.trace(10, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
            rxData += rxDataPart;

    return (len(rxData) > 0), rxData;

def exchangeMTU(transport, initiator, mtuSize, trace):
    attData = ATTData();

    mtuReply = 0;
    txData = attData.encode( ATTOpcode.ATT_EXCH_MTU_REQUEST, mtuSize );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_EXCH_MTU_RESPONSE;
            if success:
                mtuReply = reply['mtu'];

    return success, mtuReply;

def discoverPrimaryService(transport, initiator, serviceUUID, trace):
    services = { 'handles': [], 'uuids': [] };
    attData = ATTData();

    success, handle = True, 1;
    while success:
        txData = attData.encode( ATTOpcode.ATT_FIND_BY_TYPE_VALUE_REQUEST, handle, 0xffff, 0x2800, toArray( serviceUUID, 2 if serviceUUID <= 0xFFFF else 16 ) );
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        success = reply['opcode'] == ATTOpcode.ATT_FIND_BY_TYPE_VALUE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for first, last in zip(reply['handle'][0::2], reply['handle'][1::2]):
            services['handles'] += [ [ first, last ] ];
            services['uuids'] += [ serviceUUID ];

        handle = reply['handle'][-1] + 1;
        if handle > 0xFFFF:
            break;

    return success, services;

def __discoverServices(transport, initiator, first, last, uuid, trace):
    services = { 'handles': [], 'uuids': [] };
    attData = ATTData();

    success, handle = True, first;
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_GROUP_TYPE_REQUEST, handle, last, uuid );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_READ_BY_GROUP_TYPE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for _first, _last, _uuid in zip(reply['first_handle'], reply['last_handle'], reply['value']):
            services['handles'] += [ [ _first, _last ] ];
            services['uuids'] += [ toNumber(_uuid) ];
            
        handle = reply['last_handle'][-1] + 1;
        if handle > last:
            break;

    return success, services;

def discoverPrimaryServices(transport, initiator, trace):
    return __discoverServices(transport, initiator, 0x0001, 0xffff, 0x2800, trace);

def discoverSecondaryServices(transport, initiator, trace):
    return __discoverServices(transport, initiator, 0x0001, 0xffff, 0x2801, trace);

def discoverIncludedServices(transport, initiator, trace):
    services = { 'handles': [], 'uuids': [] };
    attData = ATTData();

    success, handle = True, 1;
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, handle, 0xffff, 0x2802 );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(services['handles']) > 0);
            break;

        for _handle, _value in zip(reply['handle'], reply['value']):
            services['handles'] += [ [ toNumber(_value[:2]), toNumber(_value[2:4]) ] ];
            if len(_value) > 4:
                services['uuids'] += [ toNumber(_value[4:]) ];
            else:
                """
                    NOTE: Test Specification suggest to issue a ATT_READ_REQUEST to get the 128-bit UUID,
                          but the ATT_READ_RESPONSE will only contain the handle range.
                """
                success, _service = __discoverServices(transport, initiator, toNumber(_value[:2]), toNumber(_value[2:4]), 0x2800, trace);
                if success:
                    services['uuids'] += _service['uuids']; 
            
        handle = reply['handle'][-1] + 1;
        if handle > 0xFFFF:
            break;

    return success, services;

def discoverCharacteristic(transport, initiator, handles, characteristicUUID, trace):
    characteristics = { 'handle': [], 'value': [] };
    attData = ATTData();

    success, handle = True, handles[0];
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, handle, handles[1], characteristicUUID );
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        success = reply['opcode'] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(characteristics['handle']) > 0);
            break;

        for _handle, _value in zip(reply['handle'], reply['value']):
            characteristics['handle'] += reply['handle'];
            characteristics['value'] += reply['value'];

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

def discoverCharacteristics(transport, initiator, handles, trace):
    characteristics = { 'handle': [], 'property': [], 'value_handle': [], 'uuid': [] };
    attData = ATTData();

    success, handle = True, handles[0];
    while success:
        txData = attData.encode( ATTOpcode.ATT_READ_BY_TYPE_REQUEST, handle, handles[1], 0x2803 );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_READ_BY_TYPE_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(characteristics['handle']) > 0);
            break;

        for _handle, _value in zip(reply['handle'], reply['value']):
            characteristics['handle'] += [ _handle ];
            characteristics['property'] += [ _value[0] ];
            characteristics['value_handle'] += [ toNumber(_value[1:3]) ];
            characteristics['uuid'] += [ toNumber(_value[3:]) ];

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

def discoverDescriptors(transport, initiator, handles, trace):
    characteristics = { 'handle': [], 'uuid': [] };
    attData = ATTData();

    success, handle, bCharacteristic, bValue, bDescriptor = True, handles[0], False, False, False;
    while success:
        txData = attData.encode( ATTOpcode.ATT_FIND_INFORMATION_REQUEST, handle, handles[1] );
        trace.trace(7, str(attData));
        success = attRequest( transport, initiator, txData, trace );
        if not success:
            break;
        success, rxData = attResponse( transport, initiator, trace );
        if not success:
            break;

        reply = attData.decode( rxData );
        trace.trace(7, str(attData));
        success = reply['opcode'] == ATTOpcode.ATT_FIND_INFORMATION_RESPONSE;
        if not success:
            success = (reply['opcode'] == ATTOpcode.ATT_ERROR_RESPONSE) and (reply['error'] == ATTError.ATT_ERROR_ATTRIBUTE_NOT_FOUND) and (len(characteristics['handle']) > 0);
            break;

        for _handle, _uuid in zip(reply['handle'], reply['uuid']):
            bCharacteristic = _uuid == 0x2803;
            bDescriptor = bDescriptor and not bCharacteristic;
            if bDescriptor:
                characteristics['handle'] += [ _handle ];
                characteristics['uuid'] += [ _uuid ];
            bDescriptor = bDescriptor or bValue;
            bValue = bCharacteristic;

        handle = reply['handle'][-1] + 1;
        if handle > handles[1]:
            break;

    return success, characteristics;

def readCharacteristic(transport, initiator, handle, trace):
    attData = ATTData();

    txData = attData.encode( ATTOpcode.ATT_READ_REQUEST, handle );
    trace.trace(7, str(attData));
    success = attRequest( transport, initiator, txData, trace );
    if success:
        success, rxData = attResponse( transport, initiator, trace );
        if success:
            reply = attData.decode( rxData );
            trace.trace(7, str(attData));
            success = reply['opcode'] == ATTOpcode.ATT_READ_RESPONSE;

    return success, reply['value'] if success else reply['error'];

def readStringCharacteristic(transport, initiator, handle, trace):
    success, data = readCharacteristic(transport, initiator, handle, trace);

    return success, ''.join([chr(_) for _ in data]).decode('utf-8') if success else '';

def writeCharacteristic(transport, initiator, handle, data, trace):
    attData = ATTData();
    reply = { 'opcode', ATTOpcode.ATT_WRITE_RESPONSE };

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
    for value_handle, char_uuid in zip(characteristics['value_handle'], characteristics['uuid']):
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
    Obtain address of peer, connect to peer and exchange MTU sizes
"""
def preambleConnected(transport, idx, trace):
    """
        Obtain address of Advertiser
    """
    success, addressType, address = peerAddress(transport, idx, trace);
    if not success:
        raise UnboundLocalError('Failed to obtain peer Address');

    trace.trace(6, "Advertiser address: %s" % formatAddress(address, addressType));
    """
        Initiate connection with Advertiser
    """
    initiator = Initiator(transport, idx, None, trace, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ), Address( addressType, address ));
    connected = initiator.connect();
    success = success and connected;
    if connected:
        """
            Exchange MTU Size
        """
        success, mtuSize = exchangeMTU(transport, initiator, 512, trace);
        trace.trace(6,"MTU Size: %d" % mtuSize);

    return success, initiator;

"""
    GAP/GAT/BV-01-C [GAP Mandatory Characteristics]
"""
def gap_gat_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-01-C [GAP Mandatory Characteristics]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            pairing = Pairing(transport, trace, initiator, toNumber(upperIRK));
            paired = pairing.pair();
            if paired:
                trace.trace(6,"Link Encrypted!");
                success = pairing.pause();
                if success:
                    trace.trace(6, "Link re-encrypted!");
                else:
                    trace.trace(6, "Failed to re-encrypt link!");

            success = success and paired;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "GAP Mandatory Characteristics test failed: %s" % str(e));
        success = False;

    return success;

"""
    GAP/GAT/BV-02-C [GAP Peripheral Privacy Flag Characteristic]
"""
def gap_gat_bv_02_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-02-C [GAP Peripheral Privacy Flag Characteristic]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Lookup the Generic Access Service (0x1800)
            """
            success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
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


    return success;

"""
    GAP/GAT/BV-03-C [GAP Reconnection Address Characteristic]
"""
def gap_gat_bv_03_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-03-C [GAP Reconnection Address Characteristic]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Lookup the Generic Access Service (0x1800)
            """
            success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
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

    return success;

"""
    GAP/GAT/BV-04-C [Peripheral Preferred Connection Parameters Characteristic]
"""
def gap_gat_bv_04_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-04-C [Peripheral Preferred Connection Parameters Characteristic]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Lookup the Generic Access Service (0x1800)
            """
            success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
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

    return success;

"""
    GAP/GAT/BV-05-C [Writable Device Name]
"""
def gap_gat_bv_05_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BV-05-C [Writable Device Name]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Lookup the Generic Access Service (0x1800)
            """
            success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
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

    return success;

"""
    GAP/GAT/BX-01-C [Discover All Services]
"""
def gap_gat_bx_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/GAT/BX-01-C [Discover All Services]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, characteristics = discoverCharacteristics(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                    trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover All Services test failed: %s" % str(e));
        success = False;

    return success;

"""
    GAP/IDLE/NAMP/BV-01-C [Name Discovery Procedure GATT Client]
"""
def gap_idle_namp_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GAP/IDLE/NAMP/BV-01-C [Name Discovery Procedure GATT Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Lookup the Generic Access Service (0x1800)
            """
            success, service = discoverPrimaryService(transport, initiator, 0x1800, trace);
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

    return success;

"""
    GATT/CL/GAD/BV-01-C [Discover All Primary Services - by Client]
"""
def gatt_cl_gad_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-01-C [Discover All Primary Services - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

            gattData = GATTData();
            success = success and (cmp(services, gattData.primaryServices(2)) == 0);
            
            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover All Primary Services - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAD/BV-02-C [Discover Primary Services by Service UUID - by Client]
"""
def gatt_cl_gad_bv_02_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-02-C [Discover Primary Services by Service UUID - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services with a specific Service UUID
            """
            attData = ATTData();
            gattData = GATTData();
            """
                Iterate over the unique Service UUIDs in the Service set...
            """
            for uuid in list(set(primaryServices(2)['uuids'])):
                found, services = discoverPrimaryService(transport, initiator, uuid, trace);
                if found:
                    for _uuid, handles in zip(services["uuids"], services["handles"]):
                        trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(_uuid), handles[0], handles[1]));

                success = success and found;
                success = success and (cmp(services, gattData.primaryServices(2, uuid)) == 0);
            
            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover Primary Services by Service UUID - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAD/BV-03-C [Find Included Services - by Client]
"""
def gatt_cl_gad_bv_03_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-03-C [Find Included Services - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            found, services = discoverIncludedServices(transport, initiator, trace);
            if found:
                for uuid, handles in zip(services["uuids"], services["handles"]):
                    trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

            gattData = GATTData();
            success = success and found;
            success = success and cmp(services, gattData.includedServices(2)) == 0;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Find Included Services - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAD/BV-04-C [Discover All Characteristics of a Service - by Client]
"""
def gatt_cl_gad_bv_04_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-04-C [Discover All Characteristics of a Service - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            gattData = GATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, characteristics = discoverCharacteristics(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                    trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

                success = success and cmp(characteristics, gattData.characteristics(2, handles[0])) == 0;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover All Characteristics of a Service - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAD/BV-05-C [Discover Characteristics by UUID - by Client]
"""
def gatt_cl_gad_bv_05_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-05-C [Discover Characteristics by UUID - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            gattData = GATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, characteristics = discoverCharacteristics(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                    trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));

                success = success and cmp(characteristics, gattData.characteristics(2, handles[0])) == 0;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover Characteristics by UUID - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAD/BV-06-C [Discover All Characteristic Descriptors - by Client]
"""
def gatt_cl_gad_bv_06_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAD/BV-06-C [Discover All Characteristic Descriptors - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            gattData = GATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, descriptors = discoverDescriptors(transport, initiator, handles, trace);
                for c_uuid, c_handle in zip(descriptors["uuid"], descriptors["handle"]): 
                    trace.trace(6, "    Descriptor %s handle %02X" % (attData.uuid(c_uuid), c_handle));

                success = success and cmp(descriptors, gattData.descriptors(2, handles[0])) == 0;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Discover All Characteristic Descriptors - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BV-01-C [Read Characteristic Value - by Client]
"""
def gatt_cl_gar_bv_01_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BV-01-C [Read Characteristic Value - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Discover all Services
            """
            attData = ATTData();
            gattData = GATTData();
            success, services = discoverPrimaryServices(transport, initiator, trace);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02X, %02X]" % (attData.uuid(uuid), handles[0], handles[1]));

                success, characteristics = discoverCharacteristics(transport, initiator, handles, trace);
                for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                    if (c_property & ATTProperty.ATT_PROP_READ) == ATTProperty.ATT_PROP_READ:
                        trace.trace(6, "    Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
                        success, data = readCharacteristic(transport, initiator, c_vhandle, trace);
                        if len(data) > 0:
                            trace.trace(6, "    Characteristic Value: %s" % formatArray(data));
                        match = data == gattData.characteristicValue(2, c_handle);
                        if not match:
                            trace.trace(6, "    GATT Database  Value: %s" % formatArray(gattData.characteristicValue(2, c_handle)));
                        success = success and match;                        

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Characteristic Value - by Client test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BI-01-C [Read Characteristic Value - Invalid Handle]
"""
def gatt_cl_gar_bi_01_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BI-01-C [Read Characteristic Value - Invalid Handle]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Collect all Services
            """
            prevLast, attData, gattData = 0, ATTData(), GATTData();
            services = gattData.allServices(2);
            for uuid, handles in zip(services["uuids"], services["handles"]):
                trace.trace(6, "Service %s covers [%02d, %02d]" % (attData.uuid(uuid), handles[0], handles[1]));
                
                if handles[0] > (prevLast+1):
                    ok, data = readCharacteristic(transport, initiator, (handles[0] + prevLast)/2, trace);
                    success = success and (not ok) and (data == ATTError.ATT_ERROR_INVALID_HANDLE);
                    trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % ((handles[0] + prevLast)/2, attData.error(data)));
                prevLast = handles[1];

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Characteristic Value - Invalid Handle test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BI-02-C [Read Characteristic Value - Read Not Permitted]
"""
def gatt_cl_gar_bi_02_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BI-02-C [Read Characteristic Value - Read Not Permitted]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Collect all Services
            """
            attData, gattData = ATTData(), GATTData();
            characteristics = gattData.characteristics(2);
            for c_uuid, c_handle, c_property, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["value_handle"]): 
                if (c_property & ATTProperty.ATT_PROP_READ) != ATTProperty.ATT_PROP_READ:
                    trace.trace(6, "Characteristic %s handle %02X value-handle %02X properties %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property)));
                    ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
                    success = success and (not ok) and (data == ATTError.ATT_ERROR_READ_NOT_PERMITTED);
                    trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % (c_vhandle, attData.error(data)));

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Characteristic Value - Read Not Permitted test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BI-03-C [Read Characteristic Value - Insufficient Authorization]

    NOTE: This test cannot be performed against the current version of Zephyr - since Zephyr doesn't support the Authorization Permission
"""
def gatt_cl_gar_bi_03_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BI-03-C [Read Characteristic Value - Insufficient Authorization]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Collect all Services
            """
            attData, gattData = ATTData(), GATTData();
            characteristics = gattData.characteristics(2, None, True);
            for c_uuid, c_handle, c_property, c_permission, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["permission"], characteristics["value_handle"]): 
                if (c_permission & ATTPermission.ATT_PERM_READ_AUTHOR) == ATTPermission.ATT_PERM_READ_AUTHOR:
                    trace.trace(6, "Characteristic %s handle %02X value-handle %02X properties %s permissions %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property), attData.permisison(c_permission)));
                    ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
                    success = success and (not ok) and (data == ATTError.ATT_ERROR_INSUFFICIENT_AUTHORIZATION);
                    trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % (c_vhandle, attData.error(data)));

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Characteristic Value - Insufficient Authorization test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BI-04-C [Read Characteristic Value - Insufficient Authentication]
"""
def gatt_cl_gar_bi_04_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BI-04-C [Read Characteristic Value - Insufficient Authentication]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Collect all Services
            """
            attData, gattData, found = ATTData(), GATTData(), False;
            characteristics = gattData.characteristics(1, None, True);
            for c_uuid, c_handle, c_property, c_permission, c_vhandle in zip(characteristics["uuid"], characteristics["handle"], characteristics["property"], characteristics["permission"], characteristics["value_handle"]): 
                if (c_permission & ATTPermission.ATT_PERM_READ_AUTHEN) == ATTPermission.ATT_PERM_READ_AUTHEN:
                    trace.trace(6, "Characteristic %s handle %02X value-handle %02X properties %s permissions %s" % (attData.uuid(c_uuid), c_handle, c_vhandle, attData.property(c_property), attData.permission(c_permission)));
                    ok, data = readCharacteristic(transport, initiator, c_vhandle, trace);
                    success = success and (not ok) and (data == ATTError.ATT_ERROR_INSUFFICIENT_AUTHENTICATION);
                    trace.trace(6, "Attempted to read Characteristic @ handle %02d - %s" % (c_vhandle, attData.error(data)));
                    found = True;
            
            if not found:
                trace.trace(6, "Didn't find any characteristics that require Authentication for reading...");
            success = success and found;

            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Characteristic Value - Insufficient Authentication test failed: %s" % str(e));
        success = False;

    return success;

"""
    GATT/CL/GAR/BV-03-C [Read Using Characteristic UUID - by Client]
"""
def gatt_cl_gar_bv_03_c(transport, upperTester, trace):
    trace.trace(2, "GATT/CL/GAR/BV-03-C [Read Using Characteristic UUID - by Client]");

    try:
        success, initiator = preambleConnected(transport, upperTester, trace);
        if success:
            """
                Collect all Characteristics
            """
            attData, gattData = ATTData(), GATTData();
            uuids = set(gattData.characteristics(1)['uuid']);
            for uuid in list(uuids):
                trace.trace(6, "Read Characteristics matching %s" % attData.uuid(uuid));
                ok, characteristics = discoverCharacteristic(transport, initiator, [ 0x0001, 0xFFFF ], uuid, trace);
            
                if len(characteristics['handle']) > 0:
                    for c_handle, c_value in zip(characteristics["handle"], characteristics["value"]):
                        trace.trace(6, "    Characteristic %s handle %02X value %s" % (attData.uuid(uuid), c_handle, formatArray(c_value)));
                        match = c_value == gattData.characteristicValue(1, c_handle-1);
                        if not match:
                            trace.trace(6, "    GATT Database  Value: %s" % formatArray(gattData.characteristicValue(1, c_handle-1)));
                        success = success and match;                        
           
            connected = not initiator.disconnect(0x3E)
            success = success and not connected;

    except Exception as e: 
        trace.trace(3, "Read Using Characteristic UUID - by Client test failed: %s" % str(e));
        success = False;

    return success;

_spec = {};

_spec["GAP/GAT/BV-01-C"] = \
    TestSpec(name = "GAP/GAT/BV-01-C", number_devices = 1,
             description = "#[GAPMandatoryCharacteristics]",
             test_private = gap_gat_bv_01_c);
_spec["GAP/GAT/BV-02-C"] = \
    TestSpec(name = "GAP/GAT/BV-02-C", number_devices = 1,
             description = "#[GAPPeripheralPrivacyFlagCharacteristic]",
             test_private = gap_gat_bv_02_c);
_spec["GAP/GAT/BV-03-C"] = \
    TestSpec(name = "GAP/GAT/BV-03-C", number_devices = 1,
             description = "#[GAPReconnectionAddressCharacteristic]",
             test_private = gap_gat_bv_03_c);
_spec["GAP/GAT/BV-04-C"] = \
    TestSpec(name = "GAP/GAT/BV-04-C", number_devices = 1,
             description = "#[PeripheralPreferredConnectionParametersCharacteristic]",
             test_private = gap_gat_bv_04_c);
_spec["GAP/GAT/BV-05-C"] = \
    TestSpec(name = "GAP/GAT/BV-05-C", number_devices = 1,
             description = "#[WritableDeviceName]",
             test_private = gap_gat_bv_05_c);
_spec["GAP/GAT/BX-01-C"] = \
    TestSpec(name = "GAP/GAT/BX-01-C", number_devices = 1,
             description = "#[DiscoverAllServices]",
             test_private = gap_gat_bx_01_c);
_spec["GAP/IDLE/NAMP/BV-01-C"] = \
    TestSpec(name = "GAP/IDLE/NAMP/BV-01-C", number_devices = 1,
             description = "#[NameDiscoveryProcedureGATTClient]",
             test_private = gap_idle_namp_bv_01_c);
_spec["GATT/CL/GAD/BV-01-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-01-C", number_devices = 1,
             description = "#[DiscoverAllPrimaryServices-byClient]",
             test_private = gatt_cl_gad_bv_01_c);
_spec["GATT/CL/GAD/BV-02-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-02-C", number_devices = 1,
             description = "#[DiscoverPrimaryServicesbyServiceUUID-byClient]",
             test_private = gatt_cl_gad_bv_02_c);
_spec["GATT/CL/GAD/BV-03-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-03-C", number_devices = 1,
             description = "#[FindIncludedServices-byClient]",
             test_private = gatt_cl_gad_bv_03_c);
_spec["GATT/CL/GAD/BV-04-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-04-C", number_devices = 1,
             description = "#[DiscoverAllCharacteristicsofaService-byClient]",
             test_private = gatt_cl_gad_bv_04_c);
_spec["GATT/CL/GAD/BV-05-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-05-C", number_devices = 1,
             description = "#[DiscoverCharacteristicsbyUUID-byClient]",
             test_private = gatt_cl_gad_bv_05_c);
_spec["GATT/CL/GAD/BV-06-C"] = \
    TestSpec(name = "GATT/CL/GAD/BV-06-C", number_devices = 1,
             description = "#[DiscoverAllCharacteristicDescriptors-byClient]",
             test_private = gatt_cl_gad_bv_06_c);
_spec["GATT/CL/GAR/BI-01-C"] = \
    TestSpec(name = "GATT/CL/GAR/BI-01-C", number_devices = 1,
             description = "#[ReadCharacteristicValue-InvalidHandle]",
             test_private = gatt_cl_gar_bi_01_c);
_spec["GATT/CL/GAR/BI-02-C"] = \
    TestSpec(name = "GATT/CL/GAR/BI-02-C", number_devices = 1,
             description = "#[ReadCharacteristicValue-ReadNotPermitted]",
             test_private = gatt_cl_gar_bi_02_c);
_spec["GATT/CL/GAR/BI-03-C"] = \
    TestSpec(name = "GATT/CL/GAR/BI-03-C", number_devices = 1,
             description = "#[ReadCharacteristicValue-InsufficientAuthorization]",
             test_private = gatt_cl_gar_bi_03_c);
_spec["GATT/CL/GAR/BI-04-C"] = \
    TestSpec(name = "GATT/CL/GAR/BI-04-C", number_devices = 1,
             description = "#[ReadCharacteristicValue-InsufficientAuthentication]",
             test_private = gatt_cl_gar_bi_04_c);
_spec["GATT/CL/GAR/BV-01-C"] = \
    TestSpec(name = "GATT/CL/GAR/BV-01-C", number_devices = 1,
             description = "#[ReadCharacteristicValue-byClient]",
             test_private = gatt_cl_gar_bv_01_c);
_spec["GATT/CL/GAR/BV-03-C"] = \
    TestSpec(name = "GATT/CL/GAR/BV-03-C", number_devices = 1,
             description = "#[ReadUsingCharacteristicUUID-byClient]",
             test_private = gatt_cl_gar_bv_03_c);

"""
    Return the test spec which contains info about all the tests
    this test module provides
"""
def get_tests_specs():
    return _spec;

def preamble(transport, trace):
    global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

    ok = success = preamble_standby(transport, 0, trace);
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;            
    return ok;          

"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec):
    success = preamble(transport, trace);
    test_f = test_spec.test_private;
    if test_f.__code__.co_argcount > 3:
        success = success and test_f(transport, 0, 1, trace);
    else:
        success = success and test_f(transport, 0, trace);
    return not success
