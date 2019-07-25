# -*- coding: utf-8 -*-
# Copyright 2019 Oticon A/S
# SPDX-License-Identifier: Apache-2.0

import random;
import statistics;
import os;
import numpy;
import csv
from collections import defaultdict
from enum import IntEnum;
from components.utils import *;
from components.basic_commands import *;
from components.address import *;
from components.resolvable import *;
from components.advertiser import *;
from components.scanner import *;
from components.initiator import *;
from components.addata import *; 
from components.preambles import *;
from components.test_spec import TestSpec;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

class FragmentOperation(IntEnum):
    INTERMEDIATE_FRAGMENT = 0      # Intermediate fragment of fragmented extended advertising data
    FIRST_FRAGMENT        = 1      # First fragment of fragmented extended advertising data
    LAST_FRAGMENT         = 2      # Last fragment of fragmented extended advertising data
    COMPLETE_FRAGMENT     = 3      # Complete extended advertising data
    UNCHANGED_FRAGMENT    = 4      # Unchanged data (just update the Advertising DID)

class FragmentPreference(IntEnum):
    FRAGMENT_ALL_DATA = 0          # The Controller may fragment all Host advertising data
    FRAGMENT_MIN_DATA = 1          # The Controller should not fragment or should minimize fragmentation of Host advertising data

class PhysicalChannel(IntEnum):
    LE_1M    = 1
    LE_2M    = 2
    LE_CODED = 3

class PreferredPhysicalChannel(IntEnum):
    LE_1M    = 0                   # 0 ~ The Host prefers to use the LE 1M transmitter PHY (possibly among others)
    LE_2M    = 1                   # 1 ~ The Host prefers to use the LE 2M transmitter PHY (possibly among others)
    LE_CODED = 2                   # 2 ~ The Host prefers to use the LE Coded transmitter PHY (possibly among others)

"""
    ========================================================================================================================
    BEGIN                                      U T I L I T Y   P R O C E D U R E S
    ========================================================================================================================
"""
def verifyAndShowEvent(transport, idx, expectedEvent, trace):

    event, subEvent, eventData = get_event(transport, idx, 100)[1:];
    showEvent(event, eventData, trace);
    return (event == expectedEvent);

def verifyAndShowMetaEvent(transport, idx, expectedEvent, trace):

    event, subEvent, eventData = get_event(transport, idx, 100)[1:];
    showEvent(event, eventData, trace);
    return (subEvent == expectedEvent);

def verifyAndFetchEvent(transport, idx, expectedEvent, trace):

    event, subEvent, eventData = get_event(transport, idx, 100)[1:];
    showEvent(event, eventData, trace);
    return (event == expectedEvent), eventData;

def verifyAndFetchMetaEvent(transport, idx, expectedEvent, trace):

    event, subEvent, eventData = get_event(transport, idx, 100)[1:];
    showEvent(event, eventData, trace);
    return (subEvent == expectedEvent), eventData;

def getCommandCompleteEvent(transport, idx, trace):

    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_COMPLETE, trace);
    
def readLocalResolvableAddress(transport, idx, identityAddress, trace):

    status, resolvableAddress = le_read_local_resolvable_address(transport, idx, identityAddress.type, identityAddress.address, 100);
    trace.trace(6, "LE Read Local Resolvable Address returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), resolvableAddress;

"""
    Issue a channel Map Update
"""
def channelMapUpdate(transport, idx, channelMap, trace):

    status = le_set_host_channel_classification(transport, idx, toArray(channelMap, 5), 100);
    trace.trace(6, "LE Set Host Channel Classification returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setEventMask(transport, idx, events, trace):

    status = le_set_event_mask(transport, idx, events, 100);
    trace.trace(6, "LE Set Event Mask returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setPrivacyMode(transport, idx, address, mode, trace):

    status = le_set_privacy_mode(transport, idx, address.type, address.address, mode, 100);
    trace.trace(6, "LE Set Privacy Mode returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def setDataLength(transport, idx, handle, octets, time, trace):

    status, handle = le_set_data_length(transport, idx, handle, octets, time, 100);
    trace.trace(6, "LE Set Data Length returns status: 0x%02X handle: 0x%04X" % (status, handle));
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0);

def readBufferSize(transport, idx, trace):

    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, idx, 100);
    trace.trace(6, "LE Read Buffer Size returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers));
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), maxPacketLength, maxPacketNumbers;

def readLocalFeatures(transport, idx, trace):

    status, features = le_read_local_supported_features(transport, idx, 100)
    trace.trace(6, "LE Read Local Supported Features returns status: 0x%02X" % status);
    return getCommandCompleteEvent(transport, idx, trace) and (status == 0), features;

def readRemoteFeatures(transport, idx, handle, trace):

    status = le_read_remote_features(transport, idx, handle, 100);
    trace.trace(6, "LE Read Remote Features returns status: 0x%02X" % status);
    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0);

def readRemoteVersionInformation(transport, idx, handle, trace):

    status = read_remote_version_information(transport, idx, handle, 100);
    trace.trace(6, "Read Remote Version Information returns status: 0x%02X" % status);
    return verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_CMD_STATUS, trace) and (status == 0);

def addAddressesToWhiteList(transport, idx, addresses, trace):

    _addresses = [ [ _.type, toNumber(_.address) ] for _ in addresses ];
    return preamble_specific_white_listed(transport, idx, _addresses, trace);
 
"""
    Send a DATA package...
"""
def writeData(transport, idx, handle, pbFlags, txData, trace):

    status = le_data_write(transport, idx, handle, pbFlags, 0, txData, 100);
    trace.trace(6, "LE Data Write returns status: 0x%02X" % status);
    success = status == 0;

    dataSent = has_event(transport, idx, 200);
    success = success and dataSent;
    if dataSent:
        dataSent = verifyAndShowEvent(transport, idx, Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS, trace);
        success = success and dataSent;

    return success;

"""
    Read a single DATA Package...
"""
def readData(transport, idx, trace, timeout=200):
    rxData = [];

    dataReady = le_data_ready(transport, idx, timeout);
    if dataReady:
        rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, idx, 100)[2:];
        trace.trace(6, "LE Data Read returns PB=%d BC=%d - %2d data bytes: %s" % \
                       (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
        rxData = rxDataPart;

    return (len(rxData) > 0), rxData;

"""
    Read and concatenate multiple DATA Packages...
"""
def readDataFragments(transport, idx, trace, timeout=100):
    success, rxData = True, [];

    while success:
        dataReady = le_data_ready(transport, idx, timeout);
        success = success and dataReady;
        if dataReady:
            rxPBFlags, rxBCFlags, rxDataPart = le_data_read(transport, idx, 100)[2:];
            trace.trace(6, "LE Data Read returns PB=%d BC=%d - %2d data bytes: %s" % \
                           (rxPBFlags, rxBCFlags, len(rxDataPart), formatArray(rxDataPart)));
            rxData += rxDataPart;
            timeout = 99;

    return (len(rxData) > 0), rxData;

def hasConnectionUpdateCompleteEvent(transport, idx, trace):

    success, status = has_event(transport, idx, 100), -1;
    if success:
        success, eventData = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE, trace);
        if success:
            status, handle, interval, latency, timeout = connectionUpdated(eventData);
    return success, status;

def hasChannelSelectionAlgorithmEvent(transport, idx, trace):

    success, status, chSelAlgorithm = has_event(transport, idx, 100), -1, -1;
    if success:
        success, eventData = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO, trace);
        if success:
            status, handle, chSelAlgorithm = channelSelectionAlgorithm(eventData);
    return success, handle, chSelAlgorithm;

def hasDataLengthChangedEvent(transport, idx, trace):

    success, handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = has_event(transport, idx, 200), -1, -1, -1, -1, -1;
    if success:
        success, eventData = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE, trace);
        if success:
            handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime = dataLengthChanged(eventData);
    return success, handle, maxTxOctets, maxTxTime, maxRxOctets, maxRxTime;

def hasReadRemoteFeaturesCompleteEvent(transport, idx, trace):

    success, handle, features = has_event(transport, idx, 100), -1, [];
    if success:
        success, eventData = verifyAndFetchMetaEvent(transport, idx, MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE, trace);
        if success:
            handle, features = remoteFeatures(eventData)[1:];
    return success, handle, features;

def hasReadRemoteVersionInformationCompleteEvent(transport, idx, trace):

    success, handle, version, manufacturer, subVersion = has_event(transport, idx, 100), -1, -1, -1, -1;
    if success:
        success, eventData = verifyAndFetchEvent(transport, idx, Events.BT_HCI_EVT_REMOTE_VERSION_INFO, trace);
        if success:
            handle, version, manufacturer, subVersion = remoteVersion(eventData)[1:];
    return success, handle, version, manufacturer, subVersion;

"""
    ========================================================================================================================
                                               U T I L I T Y   P R O C E D U R E S                                       END
    ========================================================================================================================
"""

def matchingReportType(advertiseType):

    if   advertiseType == Advertising.CONNECTABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_IND;
    elif advertiseType == Advertising.CONNECTABLE_HDC_DIRECTED or advertiseType == Advertising.CONNECTABLE_LDC_DIRECTED:
        reportType = AdvertisingReport.ADV_DIRECT_IND;
    elif advertiseType == Advertising.SCANNABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_SCAN_IND;
    elif advertiseType == Advertising.NON_CONNECTABLE_UNDIRECTED:
        reportType = AdvertisingReport.ADV_NONCONN_IND;
    else:
        reportType = AdvertisingReport.ADV_IND;
    return reportType;

def setPassiveScanning(transport, advertiserId, scannerId, trace, advertiseType, advertiseReports=100, \
                       advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                       scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL if advertiserId == 0 else 0x123456789ABCL );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, scannerId, trace, ScanType.PASSIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports);

    return advertiser, scanner;

def setActiveScanning(transport, advertiserId, scannerId, trace, advertiseType, advertiseReports=1, advertiseResponses=1, \
                      advertiseFilter=AdvertisingFilterPolicy.FILTER_NONE, advertiseChannels=AdvertiseChannel.ALL_CHANNELS, \
                      scanFilter=ScanningFilterPolicy.FILTER_NONE):

    advertiserAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL if advertiserId == 0 else 0x123456789ABCL );

    advertiser = Advertiser(transport, advertiserId, trace, advertiseChannels, advertiseType, advertiserAddress, peerAddress, advertiseFilter);

    scannerAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, scannerId, trace, ScanType.ACTIVE, matchingReportType(advertiseType), scannerAddress, scanFilter, advertiseReports, advertiseResponses);

    return advertiser, scanner;

"""
    LL/DDI/ADV/BV-01-C [Non-Connectable Advertising Packets on one channel]
"""
def ll_ddi_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 100, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
        
    advertising = advertiser.enable(); 
    success = advertising;
            
    if advertising:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );
        
        success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-02-C [Undirected Advertising Packets on one channel]
"""
def ll_ddi_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 100, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
        
    advertising = advertiser.enable(); 
    success = advertising;
            
    if advertising:
        success = scanner.enable() and success;
        scanner.monitor();
        success = scanner.disable() and success;
        success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );
        
        success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-03-C [Non-Connectable Advertising Packets on all channels]
"""
def ll_ddi_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.NON_CONNECTABLE_UNDIRECTED, 50, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
        
    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);
            
        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else [ 0x1E, 0x09 ] + [ ord(char) for char in "THIS IS JUST A RANDOM NAME..." ];
        advertising = advertiser.enable(); 
        success = success and advertising;
                
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );
            
            success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-04-C [Undirected Advertising with Data on all channels ]
"""
def ll_ddi_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 50, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    success = True;
    
    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);
            
        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else [ 0x1E, 0x09 ] + [ ord(char) for char in "THIS IS JUST A RANDOM NAME..." ];
        advertising = advertiser.enable(); 
        success = success and advertising;
                
        if advertising:
            success = scanner.enable() and success;
            scanner.monitor();
            success = scanner.disable() and success;
            success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );
            
            success = advertiser.disable() and success;    

    return success

"""
    LL/DDI/ADV/BV-05-C [Undirected Connectable Advertising with Scan Request/Response ]
"""
def ll_ddi_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    success = True;
    
    for address in [ 0x456789ABCDEFL, address_scramble_OUI( 0x456789ABCDEFL ), address_exchange_OUI_LAP( 0x456789ABCDEFL ) ]:
        for dataLength in [ 0, 31 ]:
            trace.trace(7, '-'*80);
                
            advertiser.responseData = [ ] if dataLength == 0 else [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
            advertising = advertiser.enable(); 
            success = success and advertising;
                    
            trace.trace(6, "\nUsing scanner address: %s SCAN_RSP data length: %d\n" % (formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC), dataLength) ); 
            success = success and preamble_set_public_address( transport, lowerTester, address, trace );
                
            if advertising:
                success = scanner.enable() and success;
                scanner.monitor();
                success = scanner.disable() and success;
                success = success and scanner.qualifyReports( 1 );
                success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
                success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-06-C [Stop Advertising on Connection Request]
"""
def ll_ddi_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED, 1);
    success = True;

    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    for address in [ 0x456789ABCDEFL, address_scramble_OUI( 0x456789ABCDEFL ), address_scramble_LAP( 0x456789ABCDEFL ), address_exchange_OUI_LAP( 0x456789ABCDEFL ) ]:
        trace.trace(7, '-'*80);
            
        trace.trace(6, "\nUsing initiator address: %s\n" % formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC)); 
        success = success and preamble_set_public_address( transport, lowerTester, address, trace );
            
        success = success and advertiser.enable();
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
            
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
        connected = initiator.connect();
        success = success and connected;
            
        transport.wait(200);
            
        if connected:
            """
                If a connection was established Advertising should have seized...
            """
            scanner.expectedResponses = None;
            success = success and scanner.enable();
            scanner.monitor();
            success = success and scanner.disable();
            success = success and not scanner.qualifyReports( 1 );

            disconnected = initiator.disconnect(0x3E);
            success = success and disconnected;
        else:
            advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-07-C [Scan Request/Response followed by Connection Request]
"""
def ll_ddi_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_UNDIRECTED);
    success = True;
    
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    success = advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 1 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData );
        
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            If a connection was established Advertising should have seized...
        """
        scanner.expectedResponses = None;
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyReports( 1 );

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-08-C [Advertiser Filtering Scan requests]
"""
def ll_ddi_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    """
        Place Public and static Random addresses of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEFL | 0xC00000000000L ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddresses[0], AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    scannerAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, scannerAddress, ScanningFilterPolicy.FILTER_NONE, 30);
        
    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], [ peerAddresses[0], peerAddresses[1] ]):

            advertiser.peerAddress = peerAddress;
            success = success and advertiser.enable();

            for i in range(3):
                useAddressType = addressType;
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL ) | 0xC00000000000L, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                scanner.ownAddress.type = useAddressType;
                scanner.expectedReports = 1 if (i == 2) else 30;
                scanner.expectedResponses = 1 if (i == 2) else None;

                success = success and scanner.enable();
                scanner.monitor();
                success = success and scanner.disable();
                success = success and scanner.qualifyReports( scanner.expectedReports );
                if not scanner.expectedResponses is None:
                    success = success and scanner.qualifyResponses( 1, advertiser.responseData ); 
                    
            advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-09-C [Advertiser Filtering Connection requests]
"""
def ll_ddi_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address and Random static address of lowerTester in the White List for the Advertiser
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddresses = [ Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), Address( IdentityAddressType.RANDOM, 0x456789ABCDEFL | 0xC00000000000L ) ];
    success = addAddressesToWhiteList(transport, upperTester, peerAddresses, trace);
    """
        Initialize Advertiser with Connectable Undirected advertising using a Public Address
    """ 
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddresses[0], AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    adData = ADData();
    advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'IUT' );

    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;

        for addressType, peerAddress in zip([ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ], peerAddresses):

            advertiser.peerAddress = peerAddress;

            for i in range(3):
                useAddressType = addressType;
                success = success and advertiser.enable();
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEFL ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEFL ) | 0xC00000000000L, trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    useAddressType = ExtendedAddressType.RANDOM if addressType == ExtendedAddressType.PUBLIC else ExtendedAddressType.PUBLIC;
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using incorrect PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using incorrect RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if useAddressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using correct PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, toNumber(peerAddresses[0].address), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using correct RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, toNumber(peerAddresses[1].address), trace );

                initiatorAddress = Address( useAddressType );
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
                
                for j in range(30):
                    connected = initiator.connect();
                    success = success and (connected if (i == 2 or filterPolicy == AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS) else not connected);
                       
                    if connected:
                        """
                            If a connection was established - disconnect...
                        """
                        success = initiator.disconnect(0x3E) and success;
                        break;

                if not connected:    
                    success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-11-C [High Duty Cycle Connectable Directed Advertising on all channels]
"""
def ll_ddi_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_HDC_DIRECTED, 30, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);
        
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor(True);
    success = success and advertiser.timeout();
    success = success and scanner.disable();
        
    success = success and scanner.qualifyReportTime( 30, 1280 );

    scanner.expectedReports = 1;
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and scanner.disable();

    success = success and scanner.qualifyReports( 1 );
    
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = success and initiator.connect();
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
    LL/DDI/ADV/BV-15-C [Discoverable Undirected Advertising on all channels]
"""
def ll_ddi_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 100, None, \
                                            AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);
        
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and advertiser.disable();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );

    return success

"""
    LL/DDI/ADV/BV-16-C [Discoverable Undirected Advertising with Data on all channels]
"""    
def ll_ddi_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 50);

    success = True;
    for i in range(3):
        if   i == 0:
            advertiser.advertiseData = [ 0x01 ];
        elif i == 1:
            advertiser.advertiseData = [ ];
        else:
            advertiser.advertiseData = [ 0x1E, 0x09 ] + [ ord(char) for char in "DATA:DATA:DATA:DATA:DATA:DATA" ]
                
        success = success and advertiser.enable();
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );
        success = success and advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-17-C [Discoverable Undirected Advertising with Scan Request/Response]
"""
def ll_ddi_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, 5);

    success = True;
    for i in range(3):
        for j in range(2):
            advertiser.responseData = [ 0x01, 0x09 ] if j == 0 else [ 0x1E, 0x09 ] + [ ord(char) for char in "IUT:IUT:IUT:IUT:IUT:IUT:IUT:I" ];            
                
            if   i == 0:
                success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace);
            elif i == 1:
                success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEFL ), trace );
            else:
                success = success and preamble_set_public_address( transport, lowerTester, address_exchange_OUI_LAP( 0x456789ABCDEFL ), trace );
                    
            success = success and advertiser.enable();
            success = success and scanner.enable();
            scanner.monitor();
            success = success and scanner.disable();
            success = success and scanner.qualifyReports( 5 );
            success = success and scanner.qualifyResponses( 5, advertiser.responseData );

            success = success and advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-18-C [Discoverable Undirected Advertiser Filtering Scan requests ]
"""
def ll_ddi_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setActiveScanning(transport, upperTester, lowerTester, trace, Advertising.SCANNABLE_UNDIRECTED, 30, None, \
                                            AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);
        
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];            

    success = success and advertiser.enable();

    for i in range(3):
        if   i == 0:
            success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL ), trace);
            scanner.ownAddress = Address( ExtendedAddressType.PUBLIC );
        elif i == 1:
            success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEFL | 0xC00000000000L, trace );
            scanner.ownAddress = Address( ExtendedAddressType.RANDOM );
        else:
            success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace );
            scanner.ownAddress = Address( ExtendedAddressType.PUBLIC );
            scanner.expectedResponses = 1;
                
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 if i > 1 else 30 );
        success = success and scanner.qualifyResponses( 1 if i > 1 else 0, advertiser.responseData if i > 1 else None );

    success = success and advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-19-C [Low Duty Cycle Directed Advertising on all channels]
"""
def ll_ddi_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    advertiser, scanner = setPassiveScanning(transport, upperTester, lowerTester, trace, Advertising.CONNECTABLE_LDC_DIRECTED, 100, \
                                             AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    """
        Place Public address of lowerTester in the White List
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);
        
    success = advertiser.enable() and success;

    success = scanner.enable() and success;
    scanner.monitor();
    success = scanner.disable() and success;
    success = success and scanner.qualifyReports( 100 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    success = success and connected;
           
    if connected:
        success = initiator.disconnect(0x3E) and success;
    else:
        success = advertiser.disable() and success;

    return success

"""
    LL/DDI/ADV/BV-20-C [Advertising on the LE 1M PHY on all channels]
"""
def ll_ddi_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

    AllPhys = 0;
    TxPhys = PreferredPhysicalChannel.LE_2M;
    RxPhys = PreferredPhysicalChannel.LE_2M;

    success = success and preamble_default_physical_channel(transport, upperTester, AllPhys, TxPhys, RxPhys, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );

    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    success = scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and advertiser.disable();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );

    return success

"""
    LL/DDI/ADV/BV-21-C [Non-Connectable Extended Legacy Advertising with Data on all channels]
"""
def ll_ddi_adv_bv_21_c(transport, upperTester, lowerTester, trace):

    Handle          = 0;
    Properties      = ExtAdvertiseType.LEGACY;
    PrimMinInterval = toArray(0x0020, 3); # Minimum Advertise Interval = 32 x 0.625 ms = 20.00 ms
    PrimMaxInterval = toArray(0x0022, 3); # Maximum Advertise Interval = 34 x 0.625 ms = 21.25 ms
    PrimChannelMap  = 0x07;  # Advertise on all three channels (#37, #38 and #39)
    OwnAddrType     = SimpleAddressType.PUBLIC;
    PeerAddrType, PeerAddress = random_address( 0x456789ABCDEFL );
    FilterPolicy    = AdvertisingFilterPolicy.FILTER_NONE;
    TxPower         = 0;
    PrimAdvPhy      = PhysicalChannel.LE_1M; # Primary advertisement PHY is LE 1M
    SecAdvMaxSkip   = 0;     # AUX_ADV_IND shall be sent prior to the next advertising event
    SecAdvPhy       = PhysicalChannel.LE_2M;
    Sid             = 0;
    ScanReqNotifyEnable = 0; # Scan request notifications disabled

    success = preamble_ext_advertising_parameters_set(transport, upperTester, Handle, Properties, PrimMinInterval, PrimMaxInterval, \
                                                      PrimChannelMap, OwnAddrType, PeerAddrType, PeerAddress, FilterPolicy, TxPower, \
                                                      PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, Sid, ScanReqNotifyEnable, trace);

    for i in range(3):
        if i == 0:
            AdvData = [ 0x01 ];
        elif i == 1:
            AdvData = [ ];
        else:
            AdvData = [ 0x1F ] + [ 0 for _ in range(30) ];

        Operation      = FragmentOperation.COMPLETE_FRAGMENT;
        FragPreference = FragmentPreference.FRAGMENT_ALL_DATA;
            
        success = success and preamble_ext_advertising_data_set(transport, upperTester, Handle, Operation, FragPreference, advData, trace);
                    
        scanInterval = 32; # Scan Interval = 32 x 0.625 ms = 20.0 ms
        scanWindow   = 32; # Scan Window   = 32 x 0.625 ms = 20.0 ms
        addrType     = SimpleAddressType.RANDOM;
        filterPolicy = ScanningFilterPolicy.FILTER_NONE;
            
        success = success and preamble_passive_scanning(transport, lowerTester, scanInterval, scanWindow, addrType, filterPolicy, trace);

        SHandle        = [ Handle ];
        SDuration      = [ 0 ];
        SMaxExtAdvEvts = [ 0 ];
            
        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.ENABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);

        deltas = [];
        reports = 0;
        while reports < 50:
            if has_event(transport, lowerTester, 100):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                # showEvent(event, eventData, trace);
                isReport = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_ADVERTISING_REPORT);
                if isReport:
                    eventType = advertiseReport(eventData)[1];
                    if eventType == AdvertisingReport.ADV_NONCONN_IND:
                        reports += 1;
                        reportData = eventData;
                        if reports > 1:
                            deltas += [eventTime - prevTime];
                        prevTime = eventTime;
            
        success = success and preamble_scan_enable(transport, lowerTester, Scan.DISABLE, ScanFilterDuplicate.DISABLE, trace);
        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.DISABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);
            
        AdvReportData = advertiseReport(reportData)[4];
        success = success and (AdvReportData == AdvData);
            
        trace.trace(7, "Mean distance between Advertise Events %d ms std. deviation %.1f ms" % (statistics.mean(deltas), statistics.pstdev(deltas)));

    return success

"""
    LL/DDI/SCN/BV-01-C [Passive Scanning of Non-Connectable Advertising Packets]
"""
def ll_ddi_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);
        
    success = scanner.enable();

    for i, channel in enumerate([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]):
        if   i == 0:
            success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL, trace);
        elif i == 1:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
        elif i == 2:
            success = success and preamble_set_random_address(transport, lowerTester, address_scramble_OUI(0x456789ABCDEFL), trace);
            
        advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC if (i < 2) else ExtendedAddressType.RANDOM );
        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];
            
        success = success and advertiser.enable();
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 20 );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-02-C [Filtered Passive Scanning of Non-Connectable Advertising Packets]
"""
def ll_ddi_scn_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_WHITE_LIST, 20);
        
    success = scanner.enable();

    for i in range(4):
        if   i == 1:
            success = success and preamble_set_random_address(transport, lowerTester, 0x456789ABCDEFL, trace);
        elif i == 2:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
        elif i == 3:
            success = success and preamble_set_random_address(transport, lowerTester, address_exchange_OUI_LAP(0x456789ABCDEFL), trace);
            
        advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC if (i & 1) == 0 else ExtendedAddressType.RANDOM );
            
        success = success and advertiser.enable();
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 20 if i == 0 else 0 );
          
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-03-C [Active Scanning of Connectable Undirected Advertising Packets]
"""
def ll_ddi_scn_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 1);
        
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(4):
            if   i == 0:
                success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL, trace);
            elif i == 1:
                success = success and preamble_set_public_address(transport, lowerTester, address_scramble_OUI(0x456789ABCDEFL), trace);
            elif i == 2:
                success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
            else:
                success = success and preamble_set_public_address(transport, lowerTester, address_exchange_OUI_LAP(0x456789ABCDEFL), trace);
                
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];
            advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];            
                
            success = success and advertiser.enable();
            scanner.monitor();
            success = success and advertiser.disable();
            success = success and scanner.qualifyReports( 1 );
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-04-C [Filtered Active Scanning of Connectable Undirected Advertising Packets]
"""
def ll_ddi_scn_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_WHITE_LIST, 20, 1);
        
    success = scanner.enable();

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(3):
            if   i == 0:
                success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL, trace);
            elif i == 1:
                success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
            else:
                success = success and preamble_set_public_address(transport, lowerTester, address_exchange_OUI_LAP(0x456789ABCDEFL), trace);
                
            advertiser.channels = channel;
            advertiser.advertiseData = [ i + 1 ];
            advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];            
                
            success = success and advertiser.enable();
            scanner.monitor();
            success = success and advertiser.disable();
            success = success and scanner.qualifyReports( 0 if i > 0 else 1 );
            success = success and scanner.qualifyResponses( 0 if i > 0 else 1, advertiser.responseData if i == 0 else None );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-05-C [Scanning for different Advertiser types with and without Data]
"""
def ll_ddi_scn_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
 
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE);
        
    success = scanner.enable();
    adData = ADData();

    for advertiseType, reportType, channel, reports, i in zip([ Advertising.NON_CONNECTABLE_UNDIRECTED, Advertising.SCANNABLE_UNDIRECTED, Advertising.CONNECTABLE_HDC_DIRECTED ],
                                                              [ AdvertisingReport.ADV_NONCONN_IND, AdvertisingReport.ADV_SCAN_IND, AdvertisingReport.ADV_DIRECT_IND],
                                                              [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], 
                                                              [ 20, 30, 15 ],
                                                                range(3)):
        if   i == 0:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_OUI(0x456789ABCDEFL), trace);
        elif i == 1:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
        else:
            success = success and preamble_set_public_address(transport, lowerTester, address_exchange_OUI_LAP(0x456789ABCDEFL), trace);

        advertiser.channels = channel;
        advertiser.advertiseType = advertiseType;
        advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED ); # [ i + 1 ];
        advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'IX' );          # [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];            

        scanner.expectedReports = reports; 
        scanner.expectedResponses = 1 if i == 1 else None;

        success = success and advertiser.enable();
        scanner.reportType = reportType;
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( reports );
        success = success and scanner.qualifyResponses( 1 if i == 1 else 0, advertiser.responseData if i == 1 else None );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-10-C [Passive Scanning for Undirected Advertising Packets with Data]
"""
def ll_ddi_scn_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);
        
    success = scanner.enable();

    for channel, i in zip([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], range(3)):
        if i < 2:
            success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL + i, trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, address_scramble_OUI(0x456789ABCDEFL), trace);
            
        advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC if i < 2 else ExtendedAddressType.RANDOM );
        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];
            
        success = success and advertiser.enable();
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 20 );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-11-C [Passive Scanning for Directed Advertising Packets]
"""
def ll_ddi_scn_bv_11_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_WHITE_LIST, 20);
        
    success = success and scanner.enable();
        
    for channel, i in zip([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], range(3)):
        if i < 2:
            success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL + i, trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, 0x456789ABCDEFL, trace);
            
        advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC if i < 2 else ExtendedAddressType.RANDOM );
        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];
            
        success = success and advertiser.enable();
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 20 if i == 0 else 0 );
           
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-12-C [Passive Scanning for Discoverable Undirected Advertising Packets]
"""
def ll_ddi_scn_bv_12_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.RANDOM, 0x123456789ABCL );

    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);

    ownAddress = Address( ExtendedAddressType.RANDOM );
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_WHITE_LIST, 20);

    success = success and scanner.enable();

    for channel, i in zip([ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], range(3)):
        if (i & 1) == 0:
            success = success and preamble_set_public_address(transport, lowerTester, 0x456789ABCDEFL + i, trace);
        else:
            success = success and preamble_set_random_address(transport, lowerTester, 0x456789ABCDEFL + i - 1, trace);
            
        advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC if (i & 1) == 0 else ExtendedAddressType.RANDOM );
        advertiser.channels = channel;
        advertiser.advertiseData = [ i + 1 ];
            
        success = success and advertiser.enable();
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 20 if i == 0 else 0 );

    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-13-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]
"""
def ll_ddi_scn_bv_13_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to upperTesters Resolving List
        Add Public address of upperTester to lowerTesters Resolving List (to allow the Controller to generate a Private Resolvable Address)
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set Resolvable Private Address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    """
        Verify that the Advertise address of the lowerTester has been correctly resolved
    """
    success = success and scanner.qualifyReports( 20, Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ) );
        
    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success

"""
    LL/DDI/SCN/BV-14-C [Passive Scanning for Connectable Directed Advertising Packets using Network Privacy]
"""
def ll_ddi_scn_bv_14_c(transport, upperTester, lowerTester, trace):

    """
        Clear the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
                 
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = Address( SimpleAddressType.RANDOM, (0x123456789ABCL & 0x3FFFFFFFFFFFL) | 0x400000000000L );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_ID_DIRECTED, 20);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    success = success and scanner.qualifyDirectedReports( 20 );

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success

"""
    LL/DDI/SCN/BV-15-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK]
"""
def ll_ddi_scn_bv_15_c(transport, upperTester, lowerTester, trace):

    """
        Set a Non-Resolvable Private Address in the upper Tester
    """
    upperAddress = toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL;
    preamble_set_random_address(transport, upperTester, upperAddress, trace);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.RANDOM, lowerRandomAddress ) );
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.RANDOM, upperAddress ) );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = Address( SimpleAddressType.RANDOM, upperAddress );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 5);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );

    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success

"""
    LL/DDI/SCN/BV-16-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK]
"""
def ll_ddi_scn_bv_16_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    success = RPAs.clear();
    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ) );
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout(2);
    success = success and RPAs.enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];
    """
        Scanner uses the Controller to generate a Resolvable Private Address ownAddress Type := ExtendedAddressType.RESOLVABLE_OR_PUBLIC
        It will perform a lookup of the Advertiser Address, which is the address of the lowerTester...
    """
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 5);

    success = success and advertiser.enable();

    resolvableAddresses = [ 0, 0 ];
        
    for i in range(2):
        if i == 1:
            """
                Wait for Resolvable Private Address timeout to expire...
            """
            transport.wait(2000);
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.qualifyReports( 5 );
        success = success and scanner.qualifyResponses( 5, advertiser.responseData );
        success = success and scanner.disable();

        addressRead, resolvableAddresses[i] = readLocalResolvableAddress(transport, upperTester, Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[i]));

    success = success and advertiser.disable();
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = success and RPAs.disable();

    return success

"""
    LL/DDI/SCN/BV-17-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK]
"""
def ll_ddi_scn_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Set a Non-Resolvable Private Address in the upper Tester
    """
    upperAddress = toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL;
    preamble_set_random_address(transport, upperTester, upperAddress, trace);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ) );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Set a Resolvable Private Address in the lower Tester
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);
    advertiser.advertiseData = [ 0x00 ];
    advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 5);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );
        
    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success

"""
    LL/DDI/SCN/BV-18-C [Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs]
"""
def ll_ddi_scn_bv_18_c(transport, upperTester, lowerTester, trace):

    """
        Set a Random Static Address in the upper Tester
    """
    upperAddress = (toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL) | 0xC00000000000L;
    preamble_set_random_address(transport, upperTester, upperAddress, trace);
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    success = success and RPAs[lowerTester].add( Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ), upperIRK );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[upperTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);
    advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 5);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses( 5, advertiser.responseData );
        
    success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    return success

"""
    LL/DDI/SCN/BV-26-C [Passive Scanning for Non-Connectable Advertising Packets using Network Privacy]
"""
def ll_ddi_scn_bv_26_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace );
    success = RPAs.clear();
    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), lowerIRK );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs.timeout( 60 );
    success = success and RPAs.enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, peerAddress, ScanningFilterPolicy.FILTER_NONE, 20);

    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    success = success and scanner.qualifyReports( 0 );
        
    success = success and RPAs.disable();

    return success

"""
    LL/DDI/SCN/BV-28-C [Passive Scanning for Non-Connectable Advertising Packets using Device Privacy]
"""
def ll_ddi_scn_bv_28_c(transport, upperTester, lowerTester, trace):

    lowerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace );
    success = RPAs.clear();
    success = success and RPAs.add( lowerAddress, lowerIRK );
    """
        Set Privacy Mode
    """
    success = success and setPrivacyMode(transport, upperTester, lowerAddress, PrivacyMode.DEVICE_PRIVACY, trace);
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs.timeout( 60 );
    success = success and RPAs.enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);
        
    success = success and advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and advertiser.disable();
    """
        Verify advertisers address!
    """
    success = success and scanner.qualifyReports( 1, lowerAddress );
        
    success = success and RPAs.disable();

    return success

"""
    LL/CON/ADV/BV-01-C [Accepting Connection Request]
"""
def ll_con_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);

    success = advertiser.enable();

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            If a connection was established Advertising should have seized...
        """
        scanner.expectedResponses = None;
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyReports( 1 );

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;

    return success

"""
   LL/CON/ADV/BV-04-C [Accepting Connection Request after Directed Advertising]
"""
def ll_con_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True;
    """
        Verify that the upper Tester continues to Advertise for 1280 ms.
    """        
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and not scanner.qualifyReportTime( 100, 1280 );
    success = success and advertiser.timeout();

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    transport.wait(200);

    if connected:
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;

    return success

"""
   LL/CON/ADV/BV-09-C [Accepting Connection Request using Channel Selection Algorithm #2]
"""
def ll_con_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    success = setEventMask(transport, upperTester, events, trace);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);

    success = advertiser.enable();

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(200);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
   LL/CON/ADV/BV-10-C [Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2]
"""
def ll_con_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    success = setEventMask(transport, upperTester, events, trace);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);

    success = advertiser.enable();

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Check for LE Channel Selection Algorithm Event in upper Tester...
        """
        success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
        success = success and (chSelAlgorithm == 1);

        transport.wait(200);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/INI/BV-01-C [Connection Initiation rejects Address change]
"""
def ll_con_ini_bv_01_c(transport, upperTester, lowerTester, trace):

    for channel in [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ]:
        for i in range(4):
            if   i == 0:
                address = 0x456789ABCDEFL;
            elif i == 1:
                address = address_scramble_OUI(0x456789ABCDEFL)
            elif i == 2:
                address = address_scramble_LAP(0x456789ABCDEFL);
            else:
                address = address_exchange_OUI_LAP(0x456789ABCDEFL);
            
            trace.trace(7, "\nUsing channel %s and Lower Tester address %s\n" % (str(channel), formatAddress(toArray(address, 6))));
                
            success = preamble_set_public_address(transport, lowerTester, address, trace);
            ownAddress = Address( ExtendedAddressType.PUBLIC );
            peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
            advertiser = Advertiser(transport, lowerTester, trace, channel, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, \
                                    peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
            advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
            initiatorAddress = Address( ExtendedAddressType.PUBLIC );
            initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, address ));
            success = success and initiator.preConnect();

            randAddress = [ random.randint(0,255) for _ in range(6) ];
            randAddress[5] |= 0xC0;
            status = le_set_random_address(transport, upperTester, randAddress, 100);
            trace.trace(6, "LE Set Random Address Command returns status: 0x%02X" % status);
            success = success and (status == 0x0C);
            getCommandCompleteEvent(transport, upperTester, trace);

            success = success and advertiser.enable();

            success = success and initiator.postConnect();
                
            transport.wait(1000);
                
            if success:
                disconnected = initiator.disconnect(0x3E);
                success = success and disconnected;

    return success

"""
    LL/CON/INI/BV-02-C [Connecting to Advertiser using Directed Advertising Packets]
"""
def ll_con_ini_bv_02_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = advertiser.enable();

    success = success and initiator.connect();
        
    transport.wait(1000);
        
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
    LL/CON/INI/BV-06-C [Filtered Connection to Advertiser using Undirected Advertising Packets]
"""
def ll_con_ini_bv_06_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
        
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_38, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, \
                          Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

    success = success and initiator.preConnect();

    for i in range(3):
        if (i == 0):
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEFL );
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        elif (i == 1):
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEFL) );
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
                
        success = success and advertiser.enable();
        transport.wait(150);
        connected = initiator.postConnect();

        if (i < 2):
            success = success and not connected;
            success = success and advertiser.disable();
        else:
            success = success and connected;
        
    transport.wait(1000);
        
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
    LL/CON/INI/BV-07-C [Filtered Connection to Advertiser using Directed Advertising Packets]
"""
def ll_con_ini_bv_07_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
        
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_38, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, \
                          Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

    success = success and initiator.preConnect();

    for i in range(3):
        if (i == 0):
            advertiser.ownAddress = Address( ExtendedAddressType.RANDOM, 0x456789ABCDEFL );
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        elif (i == 1):
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, address_scramble_LAP(0x456789ABCDEFL) );
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
        else:
            advertiser.ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(advertiser.ownAddress.address), trace);
                
        success = success and advertiser.enable();
        transport.wait(150);
        connected = initiator.postConnect();

        if (i < 2):
            success = success and not connected;
            success = success and advertiser.disable();
        else:
            success = success and connected;
        
    transport.wait(1000);
        
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
    LL/CON/INI/BV-08-C [Connecting to Connectable Undirected Advertiser with Network Privacy]
"""
def ll_con_ini_bv_08_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs.clear();
    success = success and RPAs.add( peerAddress );
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout(2);
    success = success and RPAs.enable();

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_38, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = success and advertiser.enable();

    success = success and initiator.connect();
        
    transport.wait(1000);
        
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
   LL/CON/INI/BV-09-C [Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List]
"""
def ll_con_ini_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];        
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
                
    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    success = success and RPAs[lowerTester].clear();
    RPAs[lowerTester].localIRK = randIRK[ : ];
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
    success = success and advertiser.disable();

    success = success and RPAs[lowerTester].clear();
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = success and RPAs[lowerTester].add( peerAddress, upperIRK );

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;
    else:
        advertiser.disable();

    return success

"""
   LL/CON/INI/BV-10-C [Connecting to Directed Advertiser with Network Privacy thru Resolving List]
"""
def ll_con_ini_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];   
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout(60) and RPAs[lowerTester].timeout(60);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    success = success and RPAs[lowerTester].clear();
    RPAs[lowerTester].localIRK = randIRK[ : ];
    success = success and RPAs[lowerTester].add( ownAddress );

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
    success = success and advertiser.disable();

    success = success and RPAs[lowerTester].clear();
    RPAs[lowerTester].localIRK = lowerIRK[ : ];
    success = success and RPAs[lowerTester].add( peerAddress );

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;
    else:
        advertiser.disable();

    return success

"""
   LL/CON/INI/BV-11-C [Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List ]
"""
def ll_con_ini_bv_11_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    randIRK = [ random.randint(0,255) for _ in range(16) ];        
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs[upperTester].timeout(3) and RPAs[lowerTester].timeout(3);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    success = success and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( ownAddress, randIRK );

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
    success = success and advertiser.disable();

    success = success and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( peerAddress, upperIRK );

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        localRPAs = [ numpy.asarray(initiator.localRPA()[ : ]), numpy.asarray([ 0 for _ in range(6) ]) ];
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

        transport.wait(1500);

        success = success and advertiser.enable();
        connected = initiator.connect();        
        success = success and connected;

        if connected:
            localRPAs[1] = numpy.asarray(initiator.localRPA()[ : ]);
            transport.wait(200);
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;
            """
                Verify that the Initiator Address (RPA) used in the CONNECT_IND has changed due to RPA timeout... 
            """
            success = success and not (localRPAs[0] == localRPAs[1]).all();
        else:
            advertiser.disable();
    else:
        advertiser.disable();

    return success

"""
   LL/CON/INI/BV-12-C [Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List]
"""
def ll_con_ini_bv_12_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs[upperTester].timeout(3) and RPAs[lowerTester].timeout(3);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    success = success and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( ownAddress );

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
    success = success and advertiser.disable();

    success = success and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( peerAddress, upperIRK );

    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;

    if connected:
        localRPAs = [ numpy.asarray(initiator.localRPA()[ : ]), numpy.asarray([ 0 for _ in range(6) ]) ];
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

        transport.wait(1500);

        success = success and advertiser.enable();
        connected = initiator.connect();        
        success = success and connected;

        if connected:
            localRPAs[1] = numpy.asarray(initiator.localRPA()[ : ]);
            transport.wait(200);
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;
            """
                Verify that the Initiator Address (RPA) used in the CONNECT_IND has changed due to RPA timeout... 
            """
            success = success and not (localRPAs[0] == localRPAs[1]).all()
        else:
            advertiser.disable();
    else:
        advertiser.disable();

    return success

"""
   LL/CON/INI/BV-16-C [Connecting to Advertiser with Channel Selection Algorithm #2]
"""
def ll_con_ini_bv_16_c(transport, upperTester, lowerTester, trace):

    """
       Enable the LE Channel Selection Algorithm Event; Disable the LE_Enhanced_Connection_Complete_Event
    """
    events = [0xFF, 0xFD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    success = True;
    for idx in [ upperTester, lowerTester ]:
        success = success and setEventMask(transport, idx, events, trace);

        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                                ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);

        success = advertiser.enable();

        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                Check for LE Channel Selection Algorithm Event in upper Tester...
            """
            success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
            success = success and (chSelAlgorithm == 1);

            transport.wait(200);

            disconnected = initiator.disconnect(0x3E);
            success = success and disconnected;
        else:
            advertiser.disable();

    return success

"""
   LL/CON/INI/BV-17-C [Connecting to Directed Advertiser with Channel Selection Algorithm #2]
"""
def ll_con_ini_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Enable the LE Channel Selection Algorithm Event; Disable the LE_Enhanced_Connection_Complete_Event
    """
    events = [0xFF, 0xFD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
       
    success = True;
    for idx in [ upperTester, lowerTester ]:
        success = success and setEventMask(transport, idx, events, trace);

        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                                ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);

        success = advertiser.enable();

        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
        connected = initiator.connect();
        success = success and connected;

        if connected:
            """
                Check for LE Channel Selection Algorithm Event in upper Tester...
            """
            success, handle, chSelAlgorithm = hasChannelSelectionAlgorithmEvent(transport, upperTester, trace);
            success = success and (chSelAlgorithm == 1);

            transport.wait(200);

            disconnected = initiator.disconnect(0x3E);
            success = success and disconnected;
        else:
            advertiser.disable();

    return success

"""
   LL/CON/INI/BV-18-C [Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List]
"""
def ll_con_ini_bv_18_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs[upperTester].timeout(3) and RPAs[lowerTester].timeout(3);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    success = success and RPAs[lowerTester].clear();
    success = success and RPAs[lowerTester].add( ownAddress );

    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
        
    if not connected:       
        success = success and advertiser.disable();
    else:
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    return success

"""
   LL/CON/INI/BV-19-C [Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List]
"""
def ll_con_ini_bv_19_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress );
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs[upperTester].timeout(3) and RPAs[lowerTester].timeout(3);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and not connected;
        
    if not connected:       
        success = success and advertiser.disable();
    else:
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;

    return success

"""
   LL/CON/INI/BV-20-C [Connect to Advertiser using Identity address with Device Privacy thru Resolving List]
"""
def ll_con_ini_bv_20_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    success = success and RPAs[upperTester].add( peerAddress, lowerIRK );
    success = success and RPAs[lowerTester].add( ownAddress, upperIRK );
    """
        Set Privacy Mode
    """
    success = success and setPrivacyMode(transport, upperTester, peerAddress, PrivacyMode.DEVICE_PRIVACY, trace);
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs[upperTester].timeout(3) and RPAs[lowerTester].timeout(3);
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;
        
    if connected:   
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;
    else:
        success = success and advertiser.disable();

    return success

"""
   LL/CON/INI/BV-21-C [Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List]
"""
def ll_con_ini_bv_21_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace );
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    success = RPAs.clear();
    success = success and RPAs.add( peerAddress, lowerIRK );
    """
        Set Privacy Mode
    """
    success = success and setPrivacyMode(transport, upperTester, peerAddress, PrivacyMode.DEVICE_PRIVACY, trace);
    """
        Set resolvable private address timeout in seconds ( three seconds )
    """
    success = success and RPAs.timeout(3);
    success = success and RPAs.enable();

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = success and initiator.preConnect();

    ownAddress = Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    success = success and advertiser.enable();
    connected = initiator.postConnect();
    success = success and connected;
        
    if connected:   
        connected = not initiator.disconnect(0x3E);
        success = success and not connected;
    else:
        success = success and advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-04-C [Connection where Slave sends data to Master]
"""
def ll_con_sla_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, upperTester, trace);

    success = success and advertiser.enable();

    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):

                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
            
        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags = 0;
            count = 1 + int(1000/maxPacketLength);

            for j in range(count):
                txData = [0 for _ in range(random.randint(28, maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-05-C [Connection where Slave receives data from Master]
"""
def ll_con_sla_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-06-C [Connection where Slave sends and receives data to and from Master]
"""
def ll_con_sla_bv_06_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            dataSent = writeData(transport, upperTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            dataSent = writeData(transport, lowerTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-10-C [Slave accepting Connection Parameter Update from Master]
"""
def ll_con_sla_bv_10_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);

        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = success and initiator.acceptUpdate();
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-11-C [Slave sending Termination to Master]
"""
def ll_con_sla_bv_11_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:   # Terminate connection if devices are connected
        transport.wait(200)
        initiator.switchRoles()
        success = success and initiator.disconnect(0x13)
        initiator.resetRoles()
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-12-C [Slave accepting Termination from Master]
"""
def ll_con_sla_bv_12_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:   # Terminate connection if devices are connected
        transport.wait(100)
        success = success and initiator.disconnect(0x13)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-13-C [Slave Terminating Connection on Supervision Timer]
"""
def ll_con_sla_bv_13_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    initiator.supervisionTimer = 3200
    connected = initiator.connect()
    success = success and connected

    if connected:   # Terminate connection if devices are connected
        transport.wait(3200)
        if has_event(transport, upperTester, 3200):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
        else:
            success = False
    else:
        advertiser.disable()

    initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-14-C [Slave performs Feature Setup procedure]
"""
def ll_con_sla_bv_14_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    initiator.supervisionTimer = 3200
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        """
            Send LL_FEATURE_REQ to IUT
        """
        success = success and readRemoteFeatures(transport, lowerTester, initiator.handles[0], trace);
        """
            Verify if lower tester received LE Read Remote Features Complete Event
        """
        success = success and hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace)[0]; 

        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-19-C [Slave requests Version Exchange procedure]
"""
def ll_con_sla_bv_19_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(260)

    if connected:   # Request remote version information if connected
        success = success and readRemoteVersionInformation(transport, upperTester, initiator.handles[1], trace);

        success = success and hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace)[0];
    else:
        advertiser.disable()

    transport.wait(200)
    success = success and initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-20-C [Slave responds to Version Exchange procedure]
"""
def ll_con_sla_bv_20_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected

    if connected:   # Request remote version information if connected
        transport.wait(100)
        success = success and readRemoteVersionInformation(transport, lowerTester, initiator.handles[0], trace);
        """
            Check that the IUT has responded to the remote version information request
        """
        success = success and hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace)[0];

        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-22-C [Slave requests Feature Exchange procedure]
"""
def ll_con_sla_bv_22_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(100)
        """
            Upper Tester sends an HCI_LE_Read_Local_Supported_Features command...
        """
        success = success and readLocalFeatures(transport, upperTester, trace)[0];
        """
            Upper Tester sends an HCI_LE_Read_Remote_Features command...
        """
        success = success and readRemoteFeatures(transport, upperTester, initiator.handles[1], trace); 
        """
            Upper tester expects LE Read Remote Features Complete event...
        """
        success = success and hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace)[0];

        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-24-C [Slave requests Connection Parameters – Master Accepts]
"""
def ll_con_sla_bv_24_c(transport, upperTester, lowerTester, trace):

    """
        The test consists of 3 cases for specific connection intervals and supervision timeouts
    """
    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(200)
    if connected:
        initiator.switchRoles();

        for interval, timeout in zip([ 6, 32, 6 ], [ 300, 3200, 300 ]):        
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = success and initiator.acceptUpdate();
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-25-C [Slave requests Connection Parameters – Master Rejects]
"""
def ll_con_sla_bv_25_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(200)
    if connected:
        initiator.switchRoles();

        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = success and initiator.rejectUpdate(0x0C);
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = success and not initiator.updated() and initiator.status == 0x0C;

        transport.wait(int(4 * interval * 1.25));

        initiator.resetRoles();
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-26-C [Slave requests Connection Parameters – same procedure collision]
"""
def ll_con_sla_bv_26_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(100)
    if connected:
        initiator.switchRoles();

        interval, timeout, errCode = 6, 300, 0x23;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
            NOTE: Not according to test specification, LL_CONNECTION_PARAM_REQ should be issued prior to LL_REJECTEXT_IND,
                  but Zephyr is preventing us from sending the the LL_CONNECTION_PARAM_REQ first, returning COMMAND DISALLOWED
        """
        success = success and initiator.rejectUpdate(errCode);

        initiator.resetRoles();
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updInitiatorRequest = initiator.update(interval, interval, initiator.latency, timeout);
        updPeerRequest = initiator.updPeerRequest;
        success = success and updInitiatorRequest and updPeerRequest;

        initiator.switchRoles();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        updated = initiator.updated();
        success = success and not updated and (initiator.status == errCode);

        initiator.resetRoles();
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updInitiatorRequest, updPeerRequest;
        success = success and initiator.acceptUpdate();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated();

        transport.wait(int(4 * interval * 1.25));

        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-27-C [Slave requests Connection Parameters – channel map update procedure collision]
"""
def ll_con_sla_bv_27_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        initiator.switchRoles();

        interval, timeout, errCode, channelMap = 6, 300, 0x23, 0x1555555555;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Request an update of used channels - sends an LL_CHANNEL_MAP_IND...
        """
        success = success and channelMapUpdate(transport, lowerTester, channelMap, trace);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECTEXT_IND...
        """
        success = success and initiator.rejectUpdate(errCode);
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = success and not initiator.updated() and initiator.status == errCode;

        initiator.resetRoles();

        transport.wait(int(4 * interval * 1.25));

        success = success and initiator.disconnect(0x3E);
    else:
        success = False

    return success

"""
    LL/CON/SLA/BV-29-C [Slave responds to Connection Parameters – Master no Preferred Periodicity]
"""
def ll_con_sla_bv_29_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        for interval, timeout in zip([6, 32, 6], [300, 3200, 200]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = success and initiator.acceptUpdate();
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-33-C [Slave responds to Connection Parameters request – event masked]
"""
def ll_con_sla_bv_33_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)
        interval, timeout, errCode = 6, 300, 0x3B;
        """
            Mask LE Remote Connection Parameter Request Event
        """
        events = [0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        success = success and setEventMask(transport, upperTester, events, trace);        
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        requested = initiator.update(interval, interval, initiator.latency, timeout)
        success = success and requested and not initiator.updPeerRequest;
        """
            Verify that lower tester receives a LL_REJECT_EXT_IND... unfortunately we cannot verify that (but it appears in the trace)!
        """
        updated = initiator.updated();
        success = success and updated;

        transport.wait(int(4 * interval * 1.25))
        connected = not initiator.disconnect(0x3E)
        success = success and not connected
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-34-C [Slave responds to Connection Parameters request – Host rejects]
"""
def ll_con_sla_bv_34_c(transport, upperTester, lowerTester, trace):

    interval = 6
    testSupervision = 300
    errCode = 0x3B

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        updated = initiator.update(interval, interval, initiator.latency, testSupervision)
        success = success and updated
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = success and initiator.rejectUpdate(errCode);
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
        """
        success = success and not initiator.updated() and (initiator.status == errCode);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-40-C [Slave requests PHY Update procedure]
"""
def ll_con_sla_bv_40_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True
       
    columns = defaultdict(list) # each value in each column is appended to a list

    with open('src/tests/params_con_sla_bv_40.csv') as f:
        reader = csv.reader(f)
        reader.next()
        for row in reader:
            for (i,v) in enumerate(row):
                columns[i].append(int(v, 16))

    all_phys = columns[1]
    tx_phys = columns[2]
    rx_phys = columns[3]

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)
        initiator.switchRoles()

        for i in range(0, len(columns[0])):
            if (tx_phys[i] == 0 or tx_phys[i] > 3 or rx_phys[i] == 0 or rx_phys[i] > 3):
                continue

            trace.trace(7, "Execute PHY Update with the following parameters:\tALL_PHYS: %s\tTX: %s\tRX: %s" % (str(all_phys[i]), str(tx_phys[i]), str(rx_phys[i])))
            success = success and initiator.updatePhys(all_phys[i], tx_phys[i], rx_phys[i], 0)
            trace.trace(4, "Updated PHYs:\tTX: %s\tRX: %s\n" % (str(initiator.txPhys), str(initiator.rxPhys)))
            transport.wait(100)

        transport.wait(int(4 * initiator.intervalMin * 1.25))
        initiator.resetRoles()
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-42-C [Slave responds to PHY Update procedure]
"""
def ll_con_sla_bv_42_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
        
    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)

        initiator.switchRoles();
        success = success and initiator.updatePhys( 3, 0, 0, 0 );
        initiator.resetRoles();

        for txPhys, rxPhys, expTxPhys, expRxPhys in zip([2, 1, 2, 1, 3, 3, 1, 2, 3], [2, 2, 1, 1, 2, 1, 3, 3, 3], [2, 1, 2, 1, 2, 2, 1, 2, 2], [2, 2, 1, 1, 2, 1, 2, 2, 2]):
            success = success and initiator.updatePhys(0, txPhys, rxPhys, 0)
            success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys)

            transport.wait(100)
    else:
        advertiser.disable()
        
    disconnected = initiator.disconnect(0x3E)
    success = success and disconnected

    return success

"""
    LL/CON/SLA/BV-78-C [Slave requests Packet Data Length Update procedure; LE 1M PHY]

    NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def ll_con_sla_bv_78_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))
    success = advertiser.enable()

    connected = initiator.connect()
    success = success and connected
    if connected:
        for TxOctets, TxTime in zip([ 60, 27, 251 ], [ 728, 728, 728 ]):

            success = success and setDataLength(transport, upperTester, initiator.handles[1], TxOctets, TxTime, trace);

            success = success and hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
            success = success and hasDataLengthChangedEvent(transport, upperTester, trace)[0];
                    
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-81-C [Slave requests Packet Data Length Update procedure; LE 2M PHY]

    NOTE: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def ll_con_sla_bv_81_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))
    success = advertiser.enable()

    connected = initiator.connect()
    success = success and connected

    txPhys = 0x02
    rxPhys = 0x02
    allPhys = 0
    optionPhys = 0

    if connected:
        transport.wait(100)
        initiator.switchRoles()
        success = success and initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys)
        success = success and (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys)
        initiator.resetRoles()

        for TxOctets, TxTime in zip([ 60, 27, 251 ], [ 728, 728, 728 ]):

            success = success and setDataLength(transport, upperTester, initiator.handles[1], TxOctets, TxTime, trace);

            success = success and hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
            success = success and hasDataLengthChangedEvent(transport, upperTester, trace)[0];
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BI-08-C [Slave responds to Connection Parameters request – Illegal Parameters]
"""
def ll_con_sla_bi_08_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = True
    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)

        errCode = 0x1E
        interval = 4
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        updated = initiator.update(interval, interval, initiator.latency, 300)
        success = success and updated;
        """
            Verify that lower tester receives a CONNECTION UPDATE COMPLETE Event...
        """
        rejected, status = hasConnectionUpdateCompleteEvent(transport, lowerTester, trace);        
        success = success and rejected and (status == errCode);
        
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    LL/CON/MAS/BV-03-C [Master sending Data packets to Slave]
"""
def ll_con_mas_bv_03_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    """
       Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):
                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
            
        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags = 0;
            count = 1 + int(1000/maxPacketLength);

            for j in range(count):
                txData = [0 for _ in range(random.randint(28,maxPacketLength))];

                dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-04-C [Master receiving Data packets from Slave]
"""
def ll_con_mas_bv_04_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 1;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for count in [ 100, 100, 1, 99 ]:
            pbFlags ^= 1;
            for j in range(count):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-05-C [Master sending and receiving Data packets to and form Slave]
"""
def ll_con_mas_bv_05_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        txData = [0 for _ in range(10)];
        pbFlags = 0;
        """
            Sending Data Packets with a fixed length less than 27...
        """
        for j in range(100):
            """
                Upper Tester is sending Data...
            """
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readData(transport, upperTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-07-C [Master requests Connection Parameter Update]
"""
def ll_con_mas_bv_07_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
            
        interval = timeout = 3200;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
        """
        success = success and initiator.acceptUpdate();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated();

        transport.wait(int(4 * interval * 1.25));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();
    
    return success

"""
    LL/CON/MAS/BV-08-C [Master Terminating Connection]
"""
def ll_con_mas_bv_08_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
            
        disconnected = initiator.disconnect(0x13);
        success = success and disconnected and (initiator.reasons[0] == 0x16);
    else:
        advertiser.disable();
    
    return success

"""
    LL/CON/MAS/BV-09-C [Master accepting Connection Termination]
"""
def ll_con_mas_bv_09_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
        """
            Slave is terminating the connection
        """
        initiator.switchRoles();
        disconnected = initiator.disconnect(0x13);
        success = success and disconnected and (initiator.reasons[1] == 0x13);
    else:
        advertiser.disable();
    
    return success

"""
    LL/CON/MAS/BV-13-C [Master requests Feature Setup procedure]
"""
def ll_con_mas_bv_13_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Issue the LE Read Local Supported Features Command, verify the reception of a Command Complete Event
        """
        hasFeatures, features = readLocalFeatures(transport, upperTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace);
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteFeatures(transport, upperTester, initiator.handles[1], trace);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, upperTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-20-C [Master requests Version Exchange procedure]
"""
def ll_con_mas_bv_20_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteVersionInformation(transport, upperTester, initiator.handles[1], trace);
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        success = success and hasReadRemoteVersionInformationCompleteEvent(transport, upperTester, trace)[0];

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-21-C [Master responds to Version Exchange procedure]
"""
def ll_con_mas_bv_21_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Issue the Read Remote Version Information Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteVersionInformation(transport, lowerTester, initiator.handles[1], trace);
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        success = success and hasReadRemoteVersionInformationCompleteEvent(transport, lowerTester, trace)[0];

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-23-C [Master responds to Feature Exchange procedure]
"""
def ll_con_mas_bv_23_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        success = success and readRemoteFeatures(transport, lowerTester, initiator.handles[1], trace);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        hasFeatures, handle, features = hasReadRemoteFeaturesCompleteEvent(transport, lowerTester, trace);
        success = success and hasFeatures;
        if hasFeatures:
            showLEFeatures(features, trace);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-24-C [Master requests Connection Parameters – Slave Accepts]
"""
def ll_con_mas_bv_24_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        
    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
            
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = success and initiator.acceptUpdate();
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();
    
    return success

"""
    LL/CON/MAS/BV-25-C [Master requests Connection Parameters – Slave Rejects]
"""
def ll_con_mas_bv_25_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
        
        for reject in [ True, False ]:
            interval = 6; timeout = 300;
            """
                Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            """
            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept or Reject the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP or a LL_REJECT_EXT_IND...
            """
            success = success and (initiator.rejectUpdate(0x3B) if reject else initiator.acceptUpdate());
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event... if request was accepted
            """
            if reject:
                success = success and not initiator.updated() and initiator.status == 0x3B;
            else:
                success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-26-C [Master requests Connection Parameters – same procedure collision]
"""
def ll_con_mas_bv_26_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        interval, timeout = 6, 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        updRequested = initiator.update(interval, interval, initiator.latency, timeout);
        success = success and updRequested;
        """
            Verify that the lower tester receives a LE Remote Connection Parameter Request Event...
        """
        updPeerInvolved = initiator.updPeerRequest;
        success = success and updPeerInvolved;
        """
            Send a LL_CONNECTION_PARAM_REQ as a reaction to the LE Remote Connection Parameter Request Event...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        """
            Update request will be rejected with an error code 0x0C - command disallowed...
        """
        success = success and not initiator.update(interval, interval, initiator.latency, timeout) and initiator.status == 0x0C;
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        """
            Send a LL_CONNECTION_PARAM_RSP as a reaction to the original LE Remote Connection Parameter Request Event...
        """
        initiator.updInitiatorRequest, initiator.updPeerRequest = updRequested, updPeerInvolved;
        success = success and initiator.acceptUpdate();
        """
            Both lower and upper Tester should receive a LE Connection Update Complete Event...
        """
        success = success and initiator.updated();
                                
        transport.wait(int(4 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-27-C [Master requests Connection Parameters - Channel Map Update procedure collision]
"""
def ll_con_mas_bv_27_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
        """
            Use only even channels...
        """
        success = success and channelMapUpdate(transport, upperTester, 0x1555555555, trace);

        interval = 6; timeout = 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = success and initiator.rejectUpdate(0x2A);
        """
            Verify that the update was rejected with error code 0x2A
        """
        success = success and (not initiator.updated()) and (initiator.status == 0x2A); 
        """
            Get back to original roles of initiator and peer...
        """
        initiator.resetRoles();
        initiator.pre_updated = True;
        interval = 24;

        transport.wait(int(8 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-29-C [Master requests Connection Parameters – Slave unsupported]
"""
def ll_con_mas_bv_29_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);

        interval = 6; timeout = 300;
        """
            Upper tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND... (update will take place)
        """
        success = success and initiator.rejectUpdate(0x1A);
        """
            Verify that the update was accepted
        """
        success = success and initiator.updated(); 

        transport.wait(int(8 * interval * 1.25));

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-30-C [Master responds to Connection Parameters request – no Preferred_Periodicity]
"""
def ll_con_mas_bv_30_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
    
        for interval, timeout in zip([ 6, 3200, 6 ], [ 300, 3200, 300 ]):
            """
                Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
                NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
            """
            initiator.switchRoles();

            success = success and initiator.update(interval, interval, initiator.latency, timeout);
            """
                Accept the LE Remote Connection Parameter Request Event by issuing a LL_CONNECTION_PARAM_RSP...
            """
            success = success and initiator.acceptUpdate();
            """
                Both lower and upper Tester should receive a LE Connection Update Complete Event...
            """
            success = success and initiator.updated();

            transport.wait(int(4 * interval * 1.25));

            initiator.resetRoles();

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-34-C [Master responds to Connection Parameters request – event masked]
"""
def ll_con_mas_bv_34_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    """
        Disable the LE Remote Connection Parameter Request event (Bit 5)
    """
    events = [0xDF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
    
    success = success and setEventMask(transport, upperTester, events, trace);
            
    if connected:
        transport.wait(100);

        interval = 6; timeout = 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Update request should be rejected with a LL_REJECT_EXT_IND...
        """
        success = success and not initiator.updated() and (initiator.status == 0x1A); 

        initiator.resetRoles();

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-35-C [Master responds to Connection Parameters request – Host rejects]
"""
def ll_con_mas_bv_35_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);

        interval = 6; timeout = 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Reject the LE Remote Connection Parameter Request Event by issuing a LL_REJECT_EXT_IND...
        """
        success = success and initiator.rejectUpdate(0x3B);
        """
            Verify that the update was rejected...
        """
        success = success and not initiator.updated(); 

        transport.wait(int(8 * interval * 1.25));

        initiator.resetRoles();

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-41-C [Master requests PHY Update procedure]
"""
def ll_con_mas_bv_41_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
            
        optionPhys = 0;

        for allPhys, txPhys, rxPhys, expTxPhys, expRxPhys in zip( [0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 2, 3], \
                                                                  [2, 1, 2, 1, 3, 3, 1, 2, 3, 0, 2, 0], \
                                                                  [2, 2, 1, 1, 2, 1, 3, 3, 3, 2, 0, 0], \
                                                                  [2, 1, 2, 1, 2, 2, 1, 2, 2, 2, 2, 2], \
                                                                  [2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 2, 2] ):

            success = success and initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys);
            success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);

            transport.wait(100);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-43-C [Master responds to PHY Update procedure]
"""
def ll_con_mas_bv_43_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

    success = advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
            
    if connected:
        transport.wait(100);
            
        allPhys = 3; optionPhys = 0;
        expTxPhys = expRxPhys = 2;

        success = success and initiator.updatePhys(allPhys, 1, 1, optionPhys);
        success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);

        allPhys = 0;
        initiator.switchRoles();

        for txPhys, rxPhys, expTxPhys, expRxPhys in zip( [2, 1, 2, 1, 3, 3, 1, 2, 3], \
                                                         [2, 2, 1, 1, 2, 1, 3, 3, 3], \
                                                         [2, 1, 2, 1, 2, 2, 1, 2, 2], \
                                                         [2, 2, 1, 1, 2, 1, 2, 2, 2] ):

            success = success and initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys);
            success = success and (initiator.txPhys == expTxPhys) and (initiator.rxPhys == expRxPhys);

            transport.wait(100);

        initiator.resetRoles();
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-74-C [Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 1M PHY]

    Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def ll_con_mas_bv_74_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace);

    success = success and advertiser.enable();

    connected = initiator.connect();        
    success = success and connected;

    cmaxTxOctets = 27; cmaxTxTime = 328;

    if connected:
        for txOctets, txTime in zip([ 60, 27, 251, 60, 27, 251, 60, 27, 251, 60, 27, 251 ], [ 2120, 2120, 2120, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = success and setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace);

            changed = not ((cmaxTxOctets == min(txOctets, 60)) and (cmaxTxTime == min(txTime, 592)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;
            
            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)];
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));

        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E);

    else:
        advertiser.disable();

    return success;

"""
    LL/CON/MAS/BV-77-C [Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 2M PHY]

    Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app. 
"""
def ll_con_mas_bv_77_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ))
    """
        Obtain maximum Data Packet size and maximum number of Data Packets
    """
    success, maxPacketLength, maxPacketNumbers = readBufferSize(transport, lowerTester, trace); 

    success = success and advertiser.enable()

    connected = initiator.connect()
    success = success and connected

    cmaxTxOctets = 27; cmaxTxTime = 328
    allPhys = 0
    txPhys = 0x02
    rxPhys = 0x02
    optionPhys = 0

    if connected:
        success = success and initiator.updatePhys(allPhys, txPhys, rxPhys, optionPhys)
        success = success and (initiator.txPhys == txPhys) and (initiator.rxPhys == rxPhys)
        for txOctets, txTime in zip([ 60, 27, 251, 60, 27, 251, 60, 27, 251, 60, 27, 251 ], [ 2120, 2120, 2120, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):

            success = success and setDataLength(transport, upperTester, initiator.handles[0], txOctets, txTime, trace);

            changed = not ((cmaxTxOctets == min(txOctets, 60)) and (cmaxTxTime == min(txTime, 592)));

            if changed:
                gotEvent, handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = hasDataLengthChangedEvent(transport, upperTester, trace);
                success = success and gotEvent;
                gotEvent = hasDataLengthChangedEvent(transport, lowerTester, trace)[0];
                success = success and gotEvent;

            pbFlags = 0
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)]
            dataSent = writeData(transport, upperTester, initiator.handles[0], pbFlags, txData, trace);
            success = success and dataSent;
            if dataSent:
                dataReceived, rxData = readDataFragments(transport, lowerTester, trace);
                success = success and dataReceived and (len(rxData) == len(txData));
            """
                Lower Tester is sending Data...
            """
            txData = [_ for _ in range(27)]
            for i in range(20):
                dataSent = writeData(transport, lowerTester, initiator.handles[1], pbFlags, txData, trace);
                success = success and dataSent;
                if dataSent:
                    dataReceived, rxData = readData(transport, upperTester, trace);
                    success = success and dataReceived and (len(rxData) == len(txData));

        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)

    else:
        advertiser.disable()

    return success

"""
    LL/CON/MAS/BI-06-C [Master responds to Connection Parameter Request – illegal parameters]
"""
def ll_con_mas_bi_06_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
    success = advertiser.enable();

    connected = initiator.connect();        
    success = success and connected;

    if connected:
        interval = 4; timeout = 300;
        """
            Lower tester requests an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
            NOTE: We use a little nasty trick here. Swap the roles of initiator and peer and swap assigned handles...
        """
        initiator.switchRoles();

        updated = initiator.update(interval, interval, initiator.latency, timeout);
        success = success and updated;
        """
            Verify that the update was rejected...
        """
        success = success and not initiator.updated() and (initiator.status == 0x1E); 

        interval = 24;
        transport.wait(int(8 * interval * 1.25));

        initiator.resetRoles();

        success = success and initiator.disconnect(0x3E);

    else:
        advertiser.disable();

    return success;

"""
    LL/SEC/ADV/BV-01-C [Changing Static Address while Advertising]
"""
def ll_sec_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Setting static address for upper tester and lower tester; adding lower tester's address to the whitelist
    """
    ownAddress = Address( ExtendedAddressType.RANDOM, toNumber(upperRandomAddress) | 0xC00000000000L );
    peerAddress = Address( SimpleAddressType.RANDOM, toNumber(lowerRandomAddress) | 0xC00000000000L );
    preamble_set_random_address(transport, upperTester, toNumber(ownAddress.address), trace);
    preamble_set_random_address(transport, lowerTester, toNumber(peerAddress.address), trace);
    """
        Adding lowerTester address to the White List
    """
    success = addAddressesToWhiteList(transport, upperTester, [ peerAddress ], trace);

    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30, 5);

    success = advertiser.enable();
    """
        Start scanning...
    """
    success = success and scanner.enable();
    scanner.monitor();
    """
        Attempt to change advertiser (upperTester) address...
    """
    success = success and not preamble_set_random_address(transport, upperTester, address_scramble_OUI( toNumber(ownAddress.address) ), trace);

    disabled = scanner.disable();
    success = success and disabled;
    success = success and scanner.qualifyReports( 5 );
    success = success and scanner.qualifyResponses(5, advertiser.responseData);

    disabled = advertiser.disable();
    success = success and disabled;

    return success;

"""
    LL/SEC/ADV/BV-02-C [Non Connectable Undirected Advertising with non-resolvable private address]
"""
def ll_sec_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Add Random address of upperTester to the Resolving List
    """
    RPA = ResolvableAddresses( transport, upperTester, trace );
    success = RPA.add( Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ) );
    """
        Enable Private Address Resolution
     """
    success = success and RPA.enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100)
    """
        Start NON_CONNECTABLE_ADVERTISING using non-resolvable private adddress
    """
    enabledadv = advertiser.enable()
    success = success and enabledadv

    success = success and scanner.enable()
    scanner.monitor()
    success = success and scanner.disable()
    success = success and scanner.qualifyReports( 100, Address( ExtendedAddressType.RANDOM, upperRandomAddress ) )

    success = success and advertiser.disable()
    success = success and RPA.disable();

    return success

"""
    LL/SEC/ADV/BV-03-C [Non Connectable Undirected Advertising with resolvable private address]
"""
def ll_sec_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List with the upperIRK
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, upperIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();

    success = success and RPAs[upperTester].add( identityAddresses[upperTester] );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester] );
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs[lowerTester].timeout( 2 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);

    resolvableAddresses = [ 0, 0 ];
    success = success and advertiser.enable();

    for n in [0, 1]:
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 20 );
        """
            Read local address in resolving list.
        """
        addressRead, resolvableAddresses[n] = readLocalResolvableAddress(transport, lowerTester, identityAddresses[upperTester], trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[n]));
        
        if n == 0:
            transport.wait(2000); # Wait for RPA timeout to expire

    success = advertiser.disable() and success; 
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/ADV/BV-04-C [Scannable Undirected Advertising with non-resolvable private address]
"""
def ll_sec_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    success = True;
    """
        Setting the non-resolvable Private addresses...
    """
    nrpAddresses = [ Address( SimpleAddressType.RANDOM, toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL ), \
                     Address( SimpleAddressType.RANDOM, toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFFL ) ];
    if toNumber(nrpAddresses[upperTester].address) != toNumber(upperRandomAddress):
       success = success and preamble_set_random_address(transport, upperTester, toNumber(nrpAddresses[upperTester].address), trace);
    if toNumber(nrpAddresses[lowerTester].address) != toNumber(lowerRandomAddress):
       success = success and preamble_set_random_address(transport, lowerTester, toNumber(nrpAddresses[lowerTester].address), trace);
    """
        Set advertiser and scanner to use non-resolvable Private addresses
    """
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = nrpAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

    ownAddress = Address( ExtendedAddressType.RANDOM );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100, 1);

    success = success and advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );
    success = success and scanner.qualifyResponses( 1, advertiser.responseData);

    success = advertiser.disable() and success;

    return success

"""
    LL/SEC/ADV/BV-05-C [Scannable Undirected Advertising with resolvable private address]
"""
def ll_sec_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();

    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs[upperTester].timeout( 2 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Adding lowerTester address to the White List
    """
    addresses = [ [ identityAddresses[lowerTester].type, toNumber(identityAddresses[lowerTester].address) ] ];
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);

    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 1);
        
    success = success and advertiser.enable();

    resolvableAddresses = [ 0, 0 ];
    for n in [0, 1]:
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports(20);
        success = success and scanner.qualifyResponses(1);
        addressRead, resolvableAddresses[n] = readLocalResolvableAddress(transport, upperTester, identityAddresses[lowerTester], trace);
        trace.trace(6, "AdvA: %s" % formatAddress(resolvableAddresses[n]));
        if n == 1:
            transport.wait(2000); # Wait for RPA timeout

    success = advertiser.disable() and success;
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-06-C [Connecting with Undirected Connectable Advertiser using non-resolvable private address]
"""
def ll_sec_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    """
       Setting upper tester's non-resolvable private address
    """
    upperAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL );
    success = preamble_set_random_address(transport, upperTester, toNumber(upperAddress.address), trace);

    lowerAddresses = [ Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ), \
                       Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) | 0xC00000000000L ), \
                       Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFFL ) ];

    for i, lowerAddress in enumerate(lowerAddresses):
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                                upperAddress, lowerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, upperAddress);
        if i == 0:
            """
                Set lower tester to use Public Address
            """
            success = success and preamble_set_public_address(transport, lowerTester, toNumber(lowerAddress.address), trace);
        else:
            """
                Set lower tester to use Random Address
            """
            success = success and preamble_set_random_address(transport, lowerTester, toNumber(lowerAddress.address), trace);
           
        success = success and advertiser.enable();
        """
            Attempt to connect...
        """
        success = success and initiator.connect();
        transport.wait(200);
        success = success and initiator.disconnect(0x13);

    return success;

"""
    LL/SEC/ADV/BV-07-C [Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK]
"""
def ll_sec_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    """
        Set advertiser and scanner to use non-resolvable private addresses
    """
    initiatorAddr = toNumber(lowerRandomAddress) | 0xC00000000000L
    upperAddr = (toNumber( upperRandomAddress ) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    """
        Configure RPAs to use their own IRKs for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( SimpleAddressType.RANDOM, initiatorAddr ), lowerIRK)
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)

    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( identityAddresses[lowerTester], upperIRK ) # Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    addresses = [[ SimpleAddressType.RANDOM, initiatorAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, initiatorAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS)

    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))
    """
        Setting the private non-resolvable address to upper tester
    """
    success = success and preamble_set_random_address(transport, lowerTester, initiatorAddr , trace)
    success = success and preamble_set_random_address(transport, upperTester, upperAddr, trace)

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(200)
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles()
    else:
        advertiser.disable()

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

def ll_sec_adv_bv_07_x(transport, upperTester, lowerTester, trace):

    """
        Add Identity addresses of upperTester and lowerTester to respective Resolving Lists with the distributed IRKs
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();

    success = success and RPAs[upperTester].add( identityAddresses[lowerTester] );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );
    """
        Set resolvable private address timeout in seconds ( sixty seconds )
    """
    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Adding lowerTester address to the White List
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(200);
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        advertiser.disable();

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/ADV/BV-08-C [Connecting with Undirected Connectable Advertiser with both Local and Peer IRK]
"""
def ll_sec_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and preamble_specific_white_listed(transport, upperTester, [ [ IdentityAddressType.PUBLIC, 0x456789ABCDEFL ] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, identityAddresses[upperTester]);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(200);
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-09-C [Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK]
"""
def ll_sec_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester] );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);

    success = success and advertiser.enable();
    connected = initiator.connect()
    success = success and connected

    if connected:
        transport.wait(200)
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        success = initiator.disconnect(0x13) and success
        initiator.resetRoles()
    else:
        advertiser.disable()
            
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success

    return success

"""
    LL/SEC/ADV/BV-10-C [Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity]
"""
def ll_sec_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], bogusIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);
    success = success and advertiser.enable();

    for n in range(7):
        connected = initiator.connect();
        success = success and not connected;
        if connected:
            success = initiator.disconnect(0x13) and success;
            break;

    success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-11-C [Connecting with Directed Connectable Advertiser using local and remote IRK]
"""
def ll_sec_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );
    """
        Enable use of the Resolving Lists...
    """
    success = success and RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, identityAddresses[lowerTester], AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, identityAddresses[upperTester]);

    success = success and advertiser.enable();

    connected = initiator.connect();
    success = success and connected;
    if success:
        transport.wait(200);
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        success = initiator.disconnect(0x13) and success;
        initiator.resetRoles();
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-12-C [Connecting with Directed Connectable Advertising with local IRK but without remote IRK]
"""
def ll_sec_adv_bv_12_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester] );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );
    """
        Enable use of the Resolving Lists...
    """
    success = success and RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, identityAddresses[lowerTester], AdvertisingFilterPolicy.FILTER_NONE);
    ownAddress = Address( SimpleAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, identityAddresses[upperTester] );

    privateAddresses = [ 0, 0 ];

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readLocalResolvableAddress(transport, upperTester, identityAddresses[lowerTester], trace);
        trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        disconnected = initiator.disconnect(0x13);
        initiator.resetRoles();
        success = success and disconnected;

        if disconnected:
            transport.wait( 2000 ); # wait for RPA to timeout
            success = success and advertiser.enable();
            """
                Read the resolvable address used in the AdvA field
            """
            addressRead, privateAddresses[1] = readLocalResolvableAddress(transport, upperTester, identityAddresses[lowerTester], trace);
            trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[1]));
            success = success and advertiser.disable();
    else:
        advertiser.disable();

    success = success and (privateAddresses[0] != privateAddresses[1])
    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success

    return success

"""
    LL/SEC/ADV/BV-13-C [Directed Connectable Advertising without local IRK but with remote IRK]
"""
def ll_sec_adv_bv_13_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester] );

    success = success and RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 60 );

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);

    privateAddresses = [ 0, 0 ];

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        """
            Read the resolvable address used in the AdvA field
        """
        addressRead, privateAddresses[0] = readLocalResolvableAddress(transport, upperTester, identityAddresses[lowerTester], trace);
        trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[0]));
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles();
        disconnected = initiator.disconnect(0x13);
        initiator.resetRoles();
        success = success and disconnected;

        if disconnected:
            transport.wait( 2000 ); # wait for RPA to timeout
            success = success and advertiser.enable();
            """
                Read the resolvable address used in the AdvA field
            """
            addressRead, privateAddresses[1] = readLocalResolvableAddress(transport, upperTester, identityAddresses[lowerTester], trace);
            trace.trace(6, "AdvA Address: %s" % formatAddress(privateAddresses[1]));
            success = success and advertiser.disable();
    else:
        advertiser.disable();

    success = success and (privateAddresses[0] != privateAddresses[1]);
    RPAsDisabled = RPAs[upperTester].disable() and RPAs[lowerTester].disable();
    success = success and RPAsDisabled;

    return success

"""
    LL/SEC/ADV/BV-14-C [Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List]
"""
def ll_sec_adv_bv_14_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    bogusIRK = [ random.randint(0,255) for _ in range(16) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], bogusIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = identityAddresses[lowerTester]
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = identityAddresses[upperTester]
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress)

    success = success and advertiser.enable()
    """
        Initiate connection
    """
    connected = initiator.connect()
    success = success and not connected

    if connected:
        transport.wait(200)
        success = initiator.disconnect(0x13) and success
    else:
        """
            Need to stop connection attempt - otherwies Resolvable List disable will fail with command not allowed...
        """
        success = initiator.cancelConnect() and success;
        success = advertiser.disable() and success

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success

    return success

"""
    LL/SEC/ADV/BV-15-C [Scannable Advertising with resolvable private address, no Scan Response to Identity Address]
"""
def ll_sec_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 1);

    success = success and advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.qualifyReports(20);
    success = success and not scanner.qualifyResponses(1);
    success = success and scanner.disable();

    success = success and advertiser.disable();

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-16-C [Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address]
"""
def ll_sec_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);
    """
        Start advertising and attempt to connect...
    """
    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    if not success:
        initiator.disconnect(0x13);
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-17-C [Directed Connectable Advertising using local and remote IRK, Ignore Identity Address]
"""
def ll_sec_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and not connected;
    if not success:
        initiator.disconnect(0x13);
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

"""
    LL/SEC/ADV/BV-18-C [Scannable Advertising with resolvable private address, accept Identity Address]
"""
def ll_sec_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and setPrivacyMode(transport, upperTester, identityAddresses[lowerTester], PrivacyMode.DEVICE_PRIVACY, trace);
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20, 1);

    success = success and advertiser.enable();

    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.qualifyReports(20);
    success = success and scanner.qualifyResponses(1);
    success = success and scanner.disable();

    success = advertiser.disable() and success; 

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-19-C [Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address]
"""
def ll_sec_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and setPrivacyMode(transport, upperTester, identityAddresses[lowerTester], PrivacyMode.DEVICE_PRIVACY, trace);
    """
        Add Identity Address of lower Tester to White List to enable responding to Scan Requests
    """
    success = success and addAddressesToWhiteList(transport, upperTester, [ identityAddresses[lowerTester] ], trace);

    success = success and RPAs[upperTester].timeout( 2 ) and RPAs[lowerTester].timeout( 2 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);
    """
        Start advertising and attempt to connect...
    """
    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;
    if connected:
        transport.wait(2000);
        initiator.disconnect(0x13)
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success;

"""
    LL/SEC/ADV/BV-20-C [Directed Connectable Advertising with resolvable private address; Connect to Identity Address]
"""
def ll_sec_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs to use the IRKs for address resolutions
    """
    RPAs = [ ResolvableAddresses( transport, upperTester, trace, upperIRK ), ResolvableAddresses( transport, lowerTester, trace, lowerIRK ) ];
    success = RPAs[upperTester].clear() and RPAs[lowerTester].clear();
    """
        Add Identity Addresses to Resolving Lists
    """
    identityAddresses = [ Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ) ];
    success = success and RPAs[upperTester].add( identityAddresses[lowerTester], lowerIRK );
    success = success and RPAs[lowerTester].add( identityAddresses[upperTester], upperIRK );

    success = success and setPrivacyMode(transport, upperTester, identityAddresses[lowerTester], PrivacyMode.DEVICE_PRIVACY, trace);

    success = success and RPAs[upperTester].timeout( 60 ) and RPAs[lowerTester].timeout( 60 );
    success = success and RPAs[upperTester].enable() and RPAs[lowerTester].enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
    peerAddress = identityAddresses[lowerTester];
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                             ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = identityAddresses[upperTester];
    initiator = Initiator(transport, lowerTester, upperTester, trace, ownAddress, peerAddress);

    success = success and advertiser.enable();
    connected = initiator.connect();
    success = success and connected;

    if connected:
        transport.wait(200);
        success = initiator.disconnect(0x13) and success;
    else:
        success = advertiser.disable() and success;

    success = RPAs[upperTester].disable() and RPAs[lowerTester].disable() and success;

    return success

__tests__ = {
    "LL/CON/ADV/BV-01-C": [ ll_con_adv_bv_01_c, "Accepting Connection Request" ],
    "LL/CON/ADV/BV-04-C": [ ll_con_adv_bv_04_c, "Accepting Connection Request after Directed Advertising" ],
    "LL/CON/ADV/BV-09-C": [ ll_con_adv_bv_09_c, "Accepting Connection Request using Channel Selection Algorithm #2" ],
    "LL/CON/ADV/BV-10-C": [ ll_con_adv_bv_10_c, "Accepting Connection Request after Directed Advertising using Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-01-C": [ ll_con_ini_bv_01_c, "Connection Initiation rejects Address change" ],
    "LL/CON/INI/BV-02-C": [ ll_con_ini_bv_02_c, "Connecting to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-06-C": [ ll_con_ini_bv_06_c, "Filtered Connection to Advertiser using Undirected Advertising Packets" ],
    "LL/CON/INI/BV-07-C": [ ll_con_ini_bv_07_c, "Filtered Connection to Advertiser using Directed Advertising Packets" ],
    "LL/CON/INI/BV-08-C": [ ll_con_ini_bv_08_c, "Connecting to Connectable Undirected Advertiser with Network Privacy" ],
    "LL/CON/INI/BV-09-C": [ ll_con_ini_bv_09_c, "Connecting to Connectable Undirected Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-10-C": [ ll_con_ini_bv_10_c, "Connecting to Directed Advertiser with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-11-C": [ ll_con_ini_bv_11_c, "Connecting to Directed Advertiser using  wrong address with Network Privacy thru Resolving List " ],
    "LL/CON/INI/BV-12-C": [ ll_con_ini_bv_12_c, "Connecting to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-16-C": [ ll_con_ini_bv_16_c, "Connecting to Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-17-C": [ ll_con_ini_bv_17_c, "Connecting to Directed Advertiser with Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-18-C": [ ll_con_ini_bv_18_c, "Don't connect to Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-19-C": [ ll_con_ini_bv_19_c, "Don't connect to Directed Advertiser using Identity address with Network Privacy thru Resolving List" ],
    "LL/CON/INI/BV-20-C": [ ll_con_ini_bv_20_c, "Connect to Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/INI/BV-21-C": [ ll_con_ini_bv_21_c, "Connect to Directed Advertiser using Identity address with Device Privacy thru Resolving List" ],
    "LL/CON/MAS/BI-06-C": [ ll_con_mas_bi_06_c, "Master responds to Connection Parameter Request – illegal parameters" ],
    "LL/CON/MAS/BV-03-C": [ ll_con_mas_bv_03_c, "Master sending Data packets to Slave" ],
    "LL/CON/MAS/BV-04-C": [ ll_con_mas_bv_04_c, "Master receiving Data packets from Slave" ],
    "LL/CON/MAS/BV-05-C": [ ll_con_mas_bv_05_c, "Master sending and receiving Data packets to and form Slave" ],
    "LL/CON/MAS/BV-07-C": [ ll_con_mas_bv_07_c, "Master requests Connection Parameter Update" ],
    "LL/CON/MAS/BV-08-C": [ ll_con_mas_bv_08_c, "Master Terminating Connection" ],
    "LL/CON/MAS/BV-09-C": [ ll_con_mas_bv_09_c, "Master accepting Connection Termination" ],
    "LL/CON/MAS/BV-13-C": [ ll_con_mas_bv_13_c, "Master requests Feature Setup procedure" ],
    "LL/CON/MAS/BV-20-C": [ ll_con_mas_bv_20_c, "Master requests Version Exchange procedure" ],
    "LL/CON/MAS/BV-21-C": [ ll_con_mas_bv_21_c, "Master responds to Version Exchange procedure" ],
    "LL/CON/MAS/BV-23-C": [ ll_con_mas_bv_23_c, "Master responds to Feature Exchange procedure" ],
    "LL/CON/MAS/BV-24-C": [ ll_con_mas_bv_24_c, "Master requests Connection Parameters – Slave Accepts" ],
    "LL/CON/MAS/BV-25-C": [ ll_con_mas_bv_25_c, "Master requests Connection Parameters – Slave Rejects" ],
    "LL/CON/MAS/BV-26-C": [ ll_con_mas_bv_26_c, "Master requests Connection Parameters – same procedure collision" ],
    "LL/CON/MAS/BV-27-C": [ ll_con_mas_bv_27_c, "Master requests Connection Parameters - Channel Map Update procedure collision" ],
    "LL/CON/MAS/BV-29-C": [ ll_con_mas_bv_29_c, "Master requests Connection Parameters – Slave unsupported" ],
    "LL/CON/MAS/BV-30-C": [ ll_con_mas_bv_30_c, "Master responds to Connection Parameters request – no Preferred_Periodicity" ],
    "LL/CON/MAS/BV-34-C": [ ll_con_mas_bv_34_c, "Master responds to Connection Parameters request – event masked" ],
    "LL/CON/MAS/BV-35-C": [ ll_con_mas_bv_35_c, "Master responds to Connection Parameters request – Host rejects" ],
    "LL/CON/MAS/BV-41-C": [ ll_con_mas_bv_41_c, "Master requests PHY Update procedure" ],
    "LL/CON/MAS/BV-43-C": [ ll_con_mas_bv_43_c, "Master responds to PHY Update procedure" ],
    "LL/CON/MAS/BV-74-C": [ ll_con_mas_bv_74_c, "Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 1M PHY" ],
    "LL/CON/MAS/BV-77-C": [ ll_con_mas_bv_77_c, "Master Packet Data Length Update – Initiating Packet Data Length Update Procedure; LE 2M PHY" ],
    "LL/CON/SLA/BI-08-C": [ ll_con_sla_bi_08_c, "Slave responds to Connection Parameters request – Illegal Parameters" ],
    "LL/CON/SLA/BV-04-C": [ ll_con_sla_bv_04_c, "Connection where Slave sends data to Master" ],
    "LL/CON/SLA/BV-05-C": [ ll_con_sla_bv_05_c, "Connection where Slave receives data from Master" ],
    "LL/CON/SLA/BV-06-C": [ ll_con_sla_bv_06_c, "Connection where Slave sends and receives data to and from Master" ],
    "LL/CON/SLA/BV-10-C": [ ll_con_sla_bv_10_c, "Slave accepting Connection Parameter Update from Master" ],
    "LL/CON/SLA/BV-11-C": [ ll_con_sla_bv_11_c, "Slave sending Termination to Master" ],
    "LL/CON/SLA/BV-12-C": [ ll_con_sla_bv_12_c, "Slave accepting Termination from Master" ],
#   "LL/CON/SLA/BV-13-C": [ ll_con_sla_bv_13_c, "Slave Terminating Connection on Supervision Timer" ],
    "LL/CON/SLA/BV-14-C": [ ll_con_sla_bv_14_c, "Slave performs Feature Setup procedure" ],
    "LL/CON/SLA/BV-19-C": [ ll_con_sla_bv_19_c, "Slave requests Version Exchange procedure" ],
    "LL/CON/SLA/BV-20-C": [ ll_con_sla_bv_20_c, "Slave responds to Version Exchange procedure" ],
    "LL/CON/SLA/BV-22-C": [ ll_con_sla_bv_22_c, "Slave requests Feature Exchange procedure" ],
    "LL/CON/SLA/BV-24-C": [ ll_con_sla_bv_24_c, "Slave requests Connection Parameters – Master Accepts" ],
    "LL/CON/SLA/BV-25-C": [ ll_con_sla_bv_25_c, "Slave requests Connection Parameters – Master Rejects" ],
    "LL/CON/SLA/BV-26-C": [ ll_con_sla_bv_26_c, "Slave requests Connection Parameters – same procedure collision" ],
    "LL/CON/SLA/BV-27-C": [ ll_con_sla_bv_27_c, "Slave requests Connection Parameters – channel map update procedure collision" ],
    "LL/CON/SLA/BV-29-C": [ ll_con_sla_bv_29_c, "Slave responds to Connection Parameters – Master no Preferred Periodicity" ],
    "LL/CON/SLA/BV-33-C": [ ll_con_sla_bv_33_c, "Slave responds to Connection Parameters request – event masked" ],
    "LL/CON/SLA/BV-34-C": [ ll_con_sla_bv_34_c, "Slave responds to Connection Parameters request – Host rejects" ],
    "LL/CON/SLA/BV-40-C": [ ll_con_sla_bv_40_c, "Slave requests PHY Update procedure" ],
    "LL/CON/SLA/BV-42-C": [ ll_con_sla_bv_42_c, "Slave responds to PHY Update procedure" ],
    "LL/CON/SLA/BV-78-C": [ ll_con_sla_bv_78_c, "Slave requests Packet Data Length Update procedure; LE 1M PHY" ],
    "LL/CON/SLA/BV-81-C": [ ll_con_sla_bv_81_c, "Slave requests Packet Data Length Update procedure; LE 2M PHY" ],
    "LL/DDI/ADV/BV-01-C": [ ll_ddi_adv_bv_01_c, "Non-Connectable Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-02-C": [ ll_ddi_adv_bv_02_c, "Undirected Advertising Packets on one channel" ],
    "LL/DDI/ADV/BV-03-C": [ ll_ddi_adv_bv_03_c, "Non-Connectable Advertising Packets on all channels" ],
    "LL/DDI/ADV/BV-04-C": [ ll_ddi_adv_bv_04_c, "Undirected Advertising with Data on all channels " ],
    "LL/DDI/ADV/BV-05-C": [ ll_ddi_adv_bv_05_c, "Undirected Connectable Advertising with Scan Request/Response " ],
    "LL/DDI/ADV/BV-06-C": [ ll_ddi_adv_bv_06_c, "Stop Advertising on Connection Request" ],
    "LL/DDI/ADV/BV-07-C": [ ll_ddi_adv_bv_07_c, "Scan Request/Response followed by Connection Request" ],
    "LL/DDI/ADV/BV-08-C": [ ll_ddi_adv_bv_08_c, "Advertiser Filtering Scan requests" ],
    "LL/DDI/ADV/BV-09-C": [ ll_ddi_adv_bv_09_c, "Advertiser Filtering Connection requests" ],
    "LL/DDI/ADV/BV-11-C": [ ll_ddi_adv_bv_11_c, "High Duty Cycle Connectable Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-15-C": [ ll_ddi_adv_bv_15_c, "Discoverable Undirected Advertising on all channels" ],
    "LL/DDI/ADV/BV-16-C": [ ll_ddi_adv_bv_16_c, "Discoverable Undirected Advertising with Data on all channels" ],
    "LL/DDI/ADV/BV-17-C": [ ll_ddi_adv_bv_17_c, "Discoverable Undirected Advertising with Scan Request/Response" ],
    "LL/DDI/ADV/BV-18-C": [ ll_ddi_adv_bv_18_c, "Discoverable Undirected Advertiser Filtering Scan requests " ],
    "LL/DDI/ADV/BV-19-C": [ ll_ddi_adv_bv_19_c, "Low Duty Cycle Directed Advertising on all channels" ],
    "LL/DDI/ADV/BV-20-C": [ ll_ddi_adv_bv_20_c, "Advertising on the LE 1M PHY on all channels" ],
#   "LL/DDI/ADV/BV-21-C": [ ll_ddi_adv_bv_21_c, "Non-Connectable Extended Legacy Advertising with Data on all channels" ],
    "LL/DDI/SCN/BV-01-C": [ ll_ddi_scn_bv_01_c, "Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-02-C": [ ll_ddi_scn_bv_02_c, "Filtered Passive Scanning of Non-Connectable Advertising Packets" ],
    "LL/DDI/SCN/BV-03-C": [ ll_ddi_scn_bv_03_c, "Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-04-C": [ ll_ddi_scn_bv_04_c, "Filtered Active Scanning of Connectable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-05-C": [ ll_ddi_scn_bv_05_c, "Scanning for different Advertiser types with and without Data" ],
    "LL/DDI/SCN/BV-10-C": [ ll_ddi_scn_bv_10_c, "Passive Scanning for Undirected Advertising Packets with Data" ],
    "LL/DDI/SCN/BV-11-C": [ ll_ddi_scn_bv_11_c, "Passive Scanning for Directed Advertising Packets" ],
    "LL/DDI/SCN/BV-12-C": [ ll_ddi_scn_bv_12_c, "Passive Scanning for Discoverable Undirected Advertising Packets" ],
    "LL/DDI/SCN/BV-13-C": [ ll_ddi_scn_bv_13_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-14-C": [ ll_ddi_scn_bv_14_c, "Passive Scanning for Connectable Directed Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-15-C": [ ll_ddi_scn_bv_15_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local or Peer IRK" ],
    "LL/DDI/SCN/BV-16-C": [ ll_ddi_scn_bv_16_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with Local and no Peer IRK" ],
    "LL/DDI/SCN/BV-17-C": [ ll_ddi_scn_bv_17_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with no Local and a Peer IRK" ],
    "LL/DDI/SCN/BV-18-C": [ ll_ddi_scn_bv_18_c, "Active Scanning for Scannable Undirected Advertising Packets using Network Privacy with both Local and Peer IRKs" ],
    "LL/DDI/SCN/BV-26-C": [ ll_ddi_scn_bv_26_c, "Passive Scanning for Non-Connectable Advertising Packets using Network Privacy" ],
    "LL/DDI/SCN/BV-28-C": [ ll_ddi_scn_bv_28_c, "Passive Scanning for Non-Connectable Advertising Packets using Device Privacy" ],
#   "LL/SEC/ADV/BV-01-C": [ ll_sec_adv_bv_01_c, "Changing Static Address while Advertising" ],
    "LL/SEC/ADV/BV-02-C": [ ll_sec_adv_bv_02_c, "Non Connectable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-03-C": [ ll_sec_adv_bv_03_c, "Non Connectable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-04-C": [ ll_sec_adv_bv_04_c, "Scannable Undirected Advertising with non-resolvable private address" ],
    "LL/SEC/ADV/BV-05-C": [ ll_sec_adv_bv_05_c, "Scannable Undirected Advertising with resolvable private address" ],
    "LL/SEC/ADV/BV-06-C": [ ll_sec_adv_bv_06_c, "Connecting with Undirected Connectable Advertiser using non-resolvable private address" ],
    "LL/SEC/ADV/BV-07-C": [ ll_sec_adv_bv_07_c, "Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK" ],
#   "LL/SEC/ADV/BV-07-X": [ ll_sec_adv_bv_07_x, "Connecting with Undirected Connectable Advertiser with Local IRK but no Peer IRK" ],
    "LL/SEC/ADV/BV-08-C": [ ll_sec_adv_bv_08_c, "Connecting with Undirected Connectable Advertiser with both Local and Peer IRK" ],
    "LL/SEC/ADV/BV-09-C": [ ll_sec_adv_bv_09_c, "Connecting with Undirected Connectable Advertiser with no Local IRK but peer IRK" ],
    "LL/SEC/ADV/BV-10-C": [ ll_sec_adv_bv_10_c, "Connecting with Undirected Connectable Advertiser where no match for Peer Device Identity" ],
    "LL/SEC/ADV/BV-11-C": [ ll_sec_adv_bv_11_c, "Connecting with Directed Connectable Advertiser using local and remote IRK" ],
    "LL/SEC/ADV/BV-12-C": [ ll_sec_adv_bv_12_c, "Connecting with Directed Connectable Advertising with local IRK but without remote IRK" ],
#   "LL/SEC/ADV/BV-13-C": [ ll_sec_adv_bv_13_c, "Directed Connectable Advertising without local IRK but with remote IRK" ],
    "LL/SEC/ADV/BV-14-C": [ ll_sec_adv_bv_14_c, "Directed Connectable Advertising using Resolving List and Peer Device Identity not in the List" ],
    "LL/SEC/ADV/BV-15-C": [ ll_sec_adv_bv_15_c, "Scannable Advertising with resolvable private address, no Scan Response to Identity Address" ],
    "LL/SEC/ADV/BV-16-C": [ ll_sec_adv_bv_16_c, "Undirected Connectable Advertising with resolvable private address; no Connection to Identity Address" ],
    "LL/SEC/ADV/BV-17-C": [ ll_sec_adv_bv_17_c, "Directed Connectable Advertising using local and remote IRK, Ignore Identity Address" ],
    "LL/SEC/ADV/BV-18-C": [ ll_sec_adv_bv_18_c, "Scannable Advertising with resolvable private address, accept Identity Address" ],
#   "LL/SEC/ADV/BV-19-C": [ ll_sec_adv_bv_19_c, "Undirected Connectable Advertising with Local IRK and Peer IRK, accept Identity Address" ],
    "LL/SEC/ADV/BV-20-C": [ ll_sec_adv_bv_20_c, "Directed Connectable Advertising with resolvable private address; Connect to Identity Address" ]
};

_maxNameLength = max([ len(key) for key in __tests__ ]);

_spec = { key: TestSpec(name = key, number_devices = 1, description = "#[" + __tests__[key][1] + "]", test_private = __tests__[key][0]) for key in __tests__ };

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
    success = preamble_standby(transport, 1, trace);
    ok = ok and success;
    trace.trace(4, "preamble Standby " + ("PASS" if success else "FAIL"));
    success, upperIRK, upperRandomAddress = preamble_device_address_set(transport, 0, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    ok = ok and success;            
    success, lowerIRK, lowerRandomAddress = preamble_device_address_set(transport, 1, trace);
    trace.trace(4, "preamble Device Address Set " + ("PASS" if success else "FAIL"));
    return ok and success;          
    
"""
    Run a test given its test_spec
"""
def run_a_test(args, transport, trace, test_spec):
    try:
        success = preamble(transport, trace);
    except Exception as e: 
        trace.trace(3, "Preamble generated exception: %s" % str(e));
        success = False;

    trace.trace(2, "%-*s %s test started..." % (_maxNameLength, test_spec.name, test_spec.description[1:]));
    test_f = test_spec.test_private;
    try:
        if test_f.__code__.co_argcount > 3:
            success = success and test_f(transport, 0, 1, trace);
        else:
            success = success and test_f(transport, 0, trace);
    except Exception as e: 
        trace.trace(3, "Test generated exception: %s" % str(e));
        success = False;

    return not success
