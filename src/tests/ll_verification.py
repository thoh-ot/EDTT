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
    
def local_resolvable_address(transport, idx, identityAddress, trace):
    status, resolvableAddress = le_read_local_resolvable_address(transport, idx, identityAddress.type, identityAddress.address, 100);
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);
    return status, resolvableAddress;

"""
    LL/DDI/ADV/BV-01-C [Non-Connectable Advertising Events]
"""
def ll_ddi_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    advertising = advertiser.enable(); 
    success = advertising;
            
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );
        
    if advertising:
        advertising = not advertiser.disable();    
        success = success and not advertising;

    return success

"""
    LL/DDI/ADV/BV-02-C [Undirected Advertising Events]
"""
def ll_ddi_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    advertising = advertiser.enable(); 
    success = advertising;
            
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100, None, advertiser.advertiseData );
        
    if advertising:
        advertising = not advertiser.disable();    
        success = success and not advertising;

    return success

"""
    LL/DDI/ADV/BV-03-C [Advertising Data: Non-Connectable]
"""
def ll_ddi_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 50);
    success = True;
        
    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);
            
        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else [ 0x1E, 0x09 ] + [ ord(char) for char in "THIS IS JUST A RANDOM NAME..." ];
        advertising = advertiser.enable(); 
        success = success and advertising;
                
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );
            
        if advertising:
            advertising = not advertiser.disable();    
            success = success and not advertising;

    return success

"""
    LL/DDI/ADV/BV-04-C [Advertising Data: Undirected]
"""
def ll_ddi_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 50);
    success = True;
        
    for dataLength in [ 1, 0, 31, 0 ]:
        trace.trace(7, '-'*80);
            
        advertiser.advertiseData = [ ] if dataLength == 0 else [ 0x01 ] if dataLength == 1 else [ 0x1E, 0x09 ] + [ ord(char) for char in "THIS IS JUST A RANDOM NAME..." ];
        advertising = advertiser.enable(); 
        success = success and advertising;
                
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 50, None, advertiser.advertiseData );
            
        if advertising:
            advertising = not advertiser.disable();    
            success = success and not advertising;

    return success

"""
    LL/DDI/ADV/BV-05-C [Scan Request: Undirected Connectable]
"""
def ll_ddi_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);
    success = True;
        
    for address in [ 0x456789ABCDEFL, address_scramble_OUI( 0x456789ABCDEFL ), address_exchange_OUI_LAP( 0x456789ABCDEFL ) ]:
        for dataLength in [ 0, 31 ]:
            trace.trace(7, '-'*80);
                
            advertiser.responseData = [ ] if dataLength == 0 else [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
            advertising = advertiser.enable(); 
            success = success and advertising;
                    
            trace.trace(6, "\nUsing scanner address: %s SCAN_RSP data length: %d\n" % (formatAddress( toArray(address, 6), SimpleAddressType.PUBLIC), dataLength) ); 
            success = success and preamble_set_public_address( transport, lowerTester, address, trace );
                
            success = success and scanner.enable();
            scanner.monitor();
            success = success and scanner.disable();
            success = success and scanner.qualifyReports( 1 );
            success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
            if advertising:
                advertising = not advertiser.disable();    
                success = success and not advertising;

    return success

"""
    LL/DDI/ADV/BV-06-C [Connection Request]
"""
def ll_ddi_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1);
    success = True;

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
    LL/DDI/ADV/BV-07-C [Scan Request Connection Request]
"""
def ll_ddi_adv_bv_07_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);
        
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
    LL/DDI/ADV/BV-08-C [Scan Request Device Filtering]
"""
def ll_ddi_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List for the Advertiser
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30);
        
    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;
        success = success and advertiser.enable();

        for addressType in [ ExtendedAddressType.PUBLIC, ExtendedAddressType.RANDOM ]:
            for i in range(3):
                trace.trace(7, '-'*80);
                if   i == 0:
                    """
                        Correct Address Type - scrambled Address
                    """
                    if addressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using scrambled PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL ), trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using scrambled RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL | 0xC00000000000L ), trace );
                elif i == 1:
                    """
                        Incorrect Address Type - correct Address
                    """
                    if addressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEFL | 0xC00000000000L, trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace );
                else:
                    """
                        Correct Address Type - correct Address
                    """
                    if addressType == ExtendedAddressType.PUBLIC:
                        trace.trace(7, "-- (%s,%d) Using PUBLIC address..." % (addressType.name,i));
                        success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace );
                    else:
                        trace.trace(7, "-- (%s,%d) Using RANDOM static address..." % (addressType.name,i));
                        success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEFL | 0xC00000000000L, trace );

                scanner.ownAddress.type = addressType;
                scanner.expectedReports = 5 if ((addressType == ExtendedAddressType.PUBLIC) and (i == 2)) else 30;
                scanner.expectedResponses = 5 if ((addressType == ExtendedAddressType.PUBLIC) and (i == 2)) else None;
                success = success and scanner.enable();
                scanner.monitor();
                success = success and scanner.disable();
                success = success and scanner.qualifyReports( scanner.expectedReports );
                if not scanner.expectedResponses is None:
                    success = success and scanner.qualifyResponses( 5, advertiser.responseData ); 
                    
        advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-09-C [Connection Request Device Filtering]
"""
def ll_ddi_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List for the Advertiser
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30);
        
    for filterPolicy in [ AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS, AdvertisingFilterPolicy.FILTER_CONNECTION_REQUESTS, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS ]:
        trace.trace(7, "\nTesting Advertising Filter Policy: %s" % filterPolicy.name);
        advertiser.filterPolicy = filterPolicy;
        success = success and advertiser.enable();

        for j in range(2):
            for i in range(3):
                scanner.expectedReports = 1;
                success = success and scanner.enable();
                scanner.monitor();
                success = success and scanner.disable();
                success = success and scanner.qualifyReports( 1 );

                if   i == 0:
                    if j == 0:
                        trace.trace(7, "-- (%d,%d) Using scrambled PUBLIC address..." % (j,i));
                        success = success and preamble_set_public_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEFL ), trace );
                    else:
                        trace.trace(7, "-- (%d,%d) Using scrambled RANDOM static address..." % (j,i));
                        success = success and preamble_set_random_address( transport, lowerTester, address_scramble_OUI( 0x456789ABCDEFL | 0xC00000000000L ), trace );
                elif i == 1:
                    if j == 0:
                        trace.trace(7, "-- (%d,%d) Using correct PUBLIC address..." % (j,i));
                        success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace );
                    else:
                        trace.trace(7, "-- (%d,%d) Using RANDOM static address..." % (j,i));
                        success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEFL | 0xC00000000000L, trace );
                else:
                    if j == 0:
                        trace.trace(7, "-- (%d,%d) Using correct PUBLIC address..." % (j,i));
                        success = success and preamble_set_public_address( transport, lowerTester, 0x456789ABCDEFL, trace );
                    else:
                        trace.trace(7, "-- (%d,%d) Using RANDOM static address..." % (j,i));
                        success = success and preamble_set_random_address( transport, lowerTester, 0x456789ABCDEFL | 0xC00000000000L, trace );

                trace.trace(7, "-- Using correct address TYPE..." if i != 1 else "-- Using wrong address TYPE");
                initiatorAddress = Address( ExtendedAddressType.PUBLIC if i != 1 else ExtendedAddressType.RANDOM );
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
                connected = initiator.connect();
                """
                    Setting the Initiators address type to PUBLIC, cause the Initiator to use the PUBLIC address, regardless of the address set!
                """
                if filterPolicy != AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS:
                    success = success and (connected if (i == 2) or ((j == 1) and (i == 0)) else not connected);
                else:
                    success = success and connected;
                       
                if connected:
                    """
                        If a connection was established Advertising should have seized...
                    """
                    disconnected = initiator.disconnect(0x3E);
                    success = success and disconnected;
                    if not ((j == 1) and (i == 2)):
                        success = success and advertiser.enable();
                else:
                    """
                        If a connection wasn't established Advertising should continue...
                    """
                    scanner.expectedReports = 30;
                    success = success and scanner.enable();
                    if success:
                        scanner.monitor();
                    success = success and scanner.disable();
                    success = success and scanner.qualifyReports( 30 );
                    
        if not connected:
            success = success and advertiser.disable();

    return success

"""
    LL/DDI/ADV/BV-11-C [Directed Advertising Events]
"""
def ll_ddi_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30);
        
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor(True);
  # success = success and advertiser.disable();
    success = success and scanner.disable();
    success = success and advertiser.timeout();
        
    success = success and scanner.qualifyReportTime( 30, 1280 );

    scanner.expectedReports = 1;
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and scanner.disable();

    success = success and scanner.qualifyReports( 1 );

    initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    success = success and initiator.connect();
    if success:
        success = success and initiator.disconnect(0x3E);

    return success

"""
    LL/DDI/ADV/BV-15-C [Discoverable Advertising Events]
"""
def ll_ddi_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    success = success and scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and advertiser.disable();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );

    return success

"""
    LL/DDI/ADV/BV-16-C [Advertising Data: Discoverable]
"""    
def ll_ddi_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 50);

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
    LL/DDI/ADV/BV-17-C [Scan Request: Discoverable]
"""
def ll_ddi_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, ownAddress, peerAddress);

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30, 5);

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
    LL/DDI/ADV/BV-18-C [Device Filtering: Discoverable]
"""
def ll_ddi_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];            

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30);
        
    success = success and advertiser.enable();

    for i in range(3):
        if   i == 0:
            success = success and preamble_set_public_address( transport, lowerTester, address_scramble_LAP( 0x456789ABCDEFL ), trace);
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
    LL/DDI/ADV/BV-19-C [Low Duty Cycle Directed Advertising Events]
"""
def ll_ddi_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    """
        Place Public address of lowerTester in the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace);
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    success = advertiser.enable();
    success = success and scanner.enable();
    scanner.monitor();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );

    initiatorAddress = Address( ExtendedAddressType.PUBLIC );
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
    connected = initiator.connect();
    """
        Setting the Initiators address type to PUBLIC, cause the Initiator to use the PUBLIC address, regardless of the address set!
    """
    success = success and connected;
           
    if connected:
        """
            If a connection was established Advertising should have seized...
        """
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;

    return success

"""
    LL/DDI/ADV/BV-20-C [Advertising Always Using the LE 1M PHY]
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
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100);
        
    success = scanner.enable();
    success = success and advertiser.enable();
    scanner.monitor();
    success = success and advertiser.disable();
    success = success and scanner.disable();
    success = success and scanner.qualifyReports( 100 );

    return success

"""
    LL/DDI/ADV/BV-21-C [Extended Advertising, Legacy PDUs, Non-Connectable]
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
            
        flush_events(transport, lowerTester, 100);
            
        success = success and preamble_scan_enable(transport, lowerTester, Scan.DISABLE, ScanFilterDuplicate.DISABLE, trace);
        success = success and preamble_ext_advertise_enable(transport, upperTester, Advertise.DISABLE, SHandle, SDuration, SMaxExtAdvEvts, trace);
            
        AdvReportData = advertiseReport(reportData)[4];
        success = success and (AdvReportData == AdvData);
            
        trace.trace(7, "Mean distance between Advertise Events %d ms std. deviation %.1f ms" % (statistics.mean(deltas), statistics.pstdev(deltas)));

    return success

"""
    LL/DDI/SCN/BV-01-C [Passive Scanning: Non Connectable]
"""
def ll_ddi_scn_bv_01_c(transport, upperTester, lowerTester, trace):

    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-02-C [Passive Scanning Device Filtering]
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
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-03-C [Active Scanning]
"""
def ll_ddi_scn_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-04-C [Active Scanning Device Filtering]
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
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-05-C [Scanning For Advertiser Types]
"""
def ll_ddi_scn_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20);
        
    success = scanner.enable();

    for advertiseType, reportType, channel, i in zip([ Advertising.NON_CONNECTABLE_UNDIRECTED, Advertising.SCANNABLE_UNDIRECTED, Advertising.CONNECTABLE_HDC_DIRECTED ],
                                                     [ AdvertisingReport.ADV_NONCONN_IND, AdvertisingReport.ADV_SCAN_IND, AdvertisingReport.ADV_DIRECT_IND],
                                                     [ AdvertiseChannel.CHANNEL_37, AdvertiseChannel.CHANNEL_38, AdvertiseChannel.CHANNEL_39 ], range(3)):
        if   i == 0:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_OUI(0x456789ABCDEFL), trace);
            scanner.expectedResponses = None;
        elif i == 1:
            success = success and preamble_set_public_address(transport, lowerTester, address_scramble_LAP(0x456789ABCDEFL), trace);
            scanner.expectedResponses = 1;
        else:
            success = success and preamble_set_random_address(transport, lowerTester, address_exchange_OUI_LAP(0x456789ABCDEFL), trace);
            scanner.expectedResponses = None;
            
        advertiser.channels = channel;
        advertiser.advertiseType = advertiseType;
        advertiser.advertiseData = [ i + 1 ];
        advertiser.responseData = [ 0x03, 0x09 ] + [ ord(char) for char in "IX" ];            

        success = success and advertiser.enable();
        scanner.reportType = reportType;
        scanner.monitor();
        success = success and advertiser.disable();
        success = success and scanner.qualifyReports( 1 if i == 1 else 20 );
        success = success and scanner.qualifyResponses( 1 if i == 1 else 0, advertiser.responseData if i == 1 else None );
            
    success = success and scanner.disable();

    return success

"""
    LL/DDI/SCN/BV-10-C [Passive Scanning: Undirected Events]
"""
def ll_ddi_scn_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.PUBLIC );
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.CHANNEL_37, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress);
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-11-C [Passive Scanning: Directed Events]
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
    ownAddress = Address( ExtendedAddressType.PUBLIC );
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
    LL/DDI/SCN/BV-12-C [Passive Scanning: Discoverable Events]
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
    LL/DDI/SCN/BV-13-C [Network Privacy – Passive Scanning, Peer IRK]
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
    LL/DDI/SCN/BV-14-C [Network Privacy - Passive Scanning: Directed Events to an address different from the scanner’s address]
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
    LL/DDI/SCN/BV-15-C [Network Privacy – Active Scanning, no Local IRK, no Peer IRK]
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
    LL/DDI/SCN/BV-16-C [Network Privacy – Active Scanning, Local IRK, no Peer IRK]
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

        status, resolvableAddresses[i] = local_resolvable_address(transport, upperTester, Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL ), trace);
        trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[i]));

    success = success and advertiser.disable();
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1]);
    success = success and RPAs.disable();

    return success

"""
    LL/DDI/SCN/BV-17-C [Network Privacy – Active Scanning, no Local IRK, Peer IRK]
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
    LL/DDI/SCN/BV-18-C [Network Privacy – Active Scanning, Local IRK, Peer IRK]
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
    LL/DDI/SCN/BV-26-C [Network Privacy – Passive Scanning, Peer IRK, Ignore Identity Address]
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
    LL/DDI/SCN/BV-28-C [Device Privacy – Passive Scanning, Peer IRK, Accept Identity Address]
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
    status = le_set_privacy_mode(transport, upperTester, lowerAddress.type, lowerAddress.address, PrivacyMode.DEVICE_PRIVACY, 100);
    success = success and (status == 0);
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);
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
    LL/CON/ADV/BV-01-C [Accepting Connections]
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
   LL/CON/ADV/BV-04-C [Directed Advertising Connection]
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
   LL/CON/ADV/BV-09-C [Accepting Connections, Channel Selection Algorithm #2]
"""
def ll_con_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    """
       Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    status = le_set_event_mask(transport, upperTester, events, 100);
    trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

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
        gotEvent = has_event(transport, upperTester, 100);
        success = success and gotEvent;
        if gotEvent:
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            showEvent(event, eventData, trace);
            rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO);
            success = success and rightEvent;
            if rightEvent:
                status, handle, chSelAlgorithm = channelSelectionAlgorithm(eventData);
                success = success and (chSelAlgorithm == 1);

        transport.wait(200);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
   LL/CON/ADV/BV-10-C [Directed Advertising Connection, Channel Selection Algorithm #2]
"""
def ll_con_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Enable the LE Channel Selection Algorithm Event
    """
    events = [0xFF, 0xFF, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    status = le_set_event_mask(transport, upperTester, events, 100);
    trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

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
        gotEvent = has_event(transport, upperTester, 100);
        success = success and gotEvent;
        if gotEvent:
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            showEvent(event, eventData, trace);
            rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO);
            if rightEvent:
                status, handle, chSelAlgorithm = channelSelectionAlgorithm(eventData);
                success = success and (chSelAlgorithm == 1);

        transport.wait(200);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/INI/BV-01-C [Connection Initiation]
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
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

            success = success and advertiser.enable();

            success = success and initiator.postConnect();
                
            transport.wait(1000);
                
            if success:
                disconnected = initiator.disconnect(0x3E);
                success = success and disconnected;

    return success

"""
    LL/CON/INI/BV-02-C [Connecting to Directed Advertising]
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
    LL/CON/INI/BV-06-C [Initiation Device Filtering: Undirected]
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
    LL/CON/INI/BV-07-C [Initiation Device Filtering: Directed]
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
    LL/CON/INI/BV-08-C [Network Privacy – Connection Establishment responding to connectable undirected advertising, Initiator]
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
   LL/CON/INI/BV-09-C [Network Privacy - Connection Establishment using resolving list, Initiator]
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
   LL/CON/INI/BV-10-C [Network Privacy - Connection Establishment using directed advertising and resolving list, Initiator]
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
   LL/CON/INI/BV-11-C [Network Privacy - Connection Establishment using directed advertising with wrong address and resolving list, Initiator]
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
   LL/CON/INI/BV-12-C [Network Privacy - Connection Establishment using directed advertising with identity address and resolving list, Initiator]
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
   LL/CON/INI/BV-16-C [Connection Initiation, Channel Selection Algorithm #2]
"""
def ll_con_ini_bv_16_c(transport, upperTester, lowerTester, trace):

    """
       Enable the LE Channel Selection Algorithm Event; Disable the LE_Enhanced_Connection_Complete_Event
    """
    events = [0xFF, 0xFD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
        
    success = True;
    for idx in [ upperTester, lowerTester ]:
        status = le_set_event_mask(transport, idx, events, 100);
        trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

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
            gotEvent = has_event(transport, upperTester, 100);
            success = success and gotEvent;
            if gotEvent:
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                showEvent(event, eventData, trace);
                rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO);
                success = success and rightEvent;
                if rightEvent:
                    status, handle, chSelAlgorithm = channelSelectionAlgorithm(eventData);
                    success = success and (chSelAlgorithm == 1);

            transport.wait(200);

            disconnected = initiator.disconnect(0x3E);
            success = success and disconnected;
        else:
            advertiser.disable();

    return success

"""
   LL/CON/INI/BV-17-C [Connecting to Directed Advertising, Channel Selection Algorithm #2]
"""
def ll_con_ini_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Enable the LE Channel Selection Algorithm Event; Disable the LE_Enhanced_Connection_Complete_Event
    """
    events = [0xFF, 0xFD, 0x0F, 0x00, 0x00, 0x00, 0x00, 0x00];
       
    success = True;
    for idx in [ upperTester, lowerTester ]:
        status = le_set_event_mask(transport, idx, events, 100);
        trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

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
            gotEvent = has_event(transport, upperTester, 100);
            success = success and gotEvent;
            if gotEvent:
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                showEvent(event, eventData, trace);
                rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CHAN_SEL_ALGO);
                success = success and rightEvent;
                if rightEvent:
                    status, handle, chSelAlgorithm = channelSelectionAlgorithm(eventData);
                    success = success and (chSelAlgorithm == 1);

            transport.wait(200);

            disconnected = initiator.disconnect(0x3E);
            success = success and disconnected;
        else:
            advertiser.disable();

    return success

"""
   LL/CON/INI/BV-18-C [Network Privacy - Connection Establishment using resolving list, Initiator, Ignore Identity Address]
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
   LL/CON/INI/BV-19-C [Network Privacy - Connection Establishment using directed advertising and resolving list, Initiator, Ignore Identity Address]
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
   LL/CON/INI/BV-20-C [Device Privacy - Connection Establishment using resolving list, Initiator, Accept Identity Address]
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
    status = le_set_privacy_mode(transport, upperTester, peerAddress.type, peerAddress.address, PrivacyMode.DEVICE_PRIVACY, 100);
    success = success and (status == 0);
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);
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
   LL/CON/INI/BV-21-C [Device Privacy - Connection Establishment using directed advertising and resolving list, Initiator, Accept Identity Address]
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
    status = le_set_privacy_mode(transport, upperTester, peerAddress.type, peerAddress.address, PrivacyMode.DEVICE_PRIVACY, 100);
    success = success and (status == 0);
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);
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
    LL/CON/SLA/BV-04-C [Slave Sending Data]
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
    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, upperTester, 100);
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers));
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

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
                status = le_data_write(transport, upperTester, initiator.handles[1], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, upperTester, 200);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    hasData = le_data_ready(transport, lowerTester, 200);
                    success = success and hasData;
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            
        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags = 0;
            count = 1 + int(1000/maxPacketLength);

            for j in range(count):
                txData = [0 for _ in range(random.randint(28,maxPacketLength))];

                status = le_data_write(transport, upperTester, initiator.handles[1], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, upperTester, 100);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    rxDataLength = 0;
                    while success and (rxDataLength < len(txData)):
                        hasData = le_data_ready(transport, lowerTester, 100);
                        success = success and hasData;
                        if hasData:
                            time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                            trace.trace(6, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxData), formatArray(rxData)));
                            rxDataLength += len(rxData);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-05-C [Slave Receiving Data]
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
                status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, lowerTester, 200);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    hasData = le_data_ready(transport, upperTester, 200);
                    success = success and hasData;
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100);
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-06-C [Slave Sending and Receiving Data]
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
            status = le_data_write(transport, upperTester, initiator.handles[1], pbFlags, 0, txData, 100);
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
            success = success and (status == 0);
            if success:
                dataSent = has_event(transport, upperTester, 200);
                success = success and dataSent;
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                hasData = le_data_ready(transport, lowerTester, 200);
                success = success and hasData;
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                    trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            """
                Lower Tester is sending Data...
            """
            status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100);
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
            success = success and (status == 0);
            if success:
                dataSent = has_event(transport, lowerTester, 200);
                success = success and dataSent;
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                hasData = le_data_ready(transport, upperTester, 200);
                success = success and hasData;
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100);
                    trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/SLA/BV-10-C [Accepting Parameter Update]
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
    LL/CON/SLA/BV-11-C [Slave sending termination]
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
    LL/CON/SLA/BV-12-C [Slave accepting termination]
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
    LL/CON/SLA/BV-13-C [Slave supervision timer]
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
    LL/CON/SLA/BV-14-C [Feature Setup Response]
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

    if connected:   # Wait for supervision timer to run out
        transport.wait(100)
        """
            Send LL_FEATURE_REQ to IUT
        """
        le_read_remote_features(transport, lowerTester, initiator.handles[0], 100)
        if has_event(transport, lowerTester, 100):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_CMD_STATUS)
        else:
            success = False

        """
            Verify if lower tester received LE Read Remote Features Complete Event
        """
        if has_event(transport, lowerTester, 100):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            numPackets, opCode, status = struct.unpack('<BHB', eventData[:4])
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE)
        else:
            success = False
    else:
        advertiser.disable()

    success = success and initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-19-C [Slave request version]
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
        read_remote_version_information(transport, upperTester, initiator.handles[1], 100)
        if(has_event(transport, upperTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            success = success and (event == Events.BT_HCI_EVT_CMD_STATUS)
        else:
            success = False
        if(has_event(transport, upperTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, handle, version, manufacturer, subVersion = struct.unpack('<BHBHH', eventData[0:8])
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_REMOTE_VERSION_INFO)
    else:
        advertiser.disable()

    transport.wait(200)
    success = success and initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-20-C [Slave respond version]
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
        read_remote_version_information(transport, lowerTester, initiator.handles[0], 100)
        if has_event(transport, lowerTester, 100):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            success = success and (event == Events.BT_HCI_EVT_CMD_STATUS)
        """
            Check that the IUT has responded to the remote version information request
        """
        if has_event(transport, lowerTester, 100):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            status, handle, version, manufacturer, subVersion = struct.unpack('<BHBHH', eventData[0:8])
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_REMOTE_VERSION_INFO)
        transport.wait(200)
            
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-22-C [Initiate feature exchange]
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
        status, features = le_read_local_supported_features(transport, upperTester, 100)
        success = success and (status == 0x00)
        """
            Verify that upper tester has received Command Complete Event with status 0x00
        """
        if(has_event(transport, upperTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            numPackets, opCode, status = struct.unpack('<BHB', eventData[:4])
            success = success and (opCode == 0x2003) and (status == 0x00) 
        else:
            success = False
 
        le_read_remote_features(transport, upperTester, initiator.handles[1], 100)
        """
            Upper tester expects command status event from IUT...
        """
        if (has_event(transport, upperTester, 200) and success):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
            success = success and (opCode == 0x2016) and (status == 0x00)
        else:
            success = False

        """
            Upper tester expects LE Read Remote Features Complete event...
        """
        if (has_event(transport, upperTester, 100) and success):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, handle = struct.unpack('<BH', eventData[1:4])
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE) and (status == 0x00)
        else:
            success = False

        transport.wait(500)
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-24-C [Initiate connection parameter request - Accept]
"""
def ll_con_sla_bv_24_c(transport, upperTester, lowerTester, trace):

    """
        The test consists of 3 cases for specific connection intervals and supervision timeouts
    """
    intervals = [6, 32, 6]
    supervisionTimeouts = [300, 3200, 300]

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(200)
    if connected:
        for i in range(0,len(intervals)):
            le_connection_update(transport, upperTester, initiator.handles[1], intervals[i], intervals[i], initiator.latency, \
                                 supervisionTimeouts[i], initiator.minCeLen, initiator.maxCeLen, 100)
            transport.wait(100)
            status, handle = le_remote_connection_parameter_request_reply(transport, lowerTester, initiator.handles[0], intervals[i], \
                                intervals[i], initiator.latency, supervisionTimeouts[i], initiator.minCeLen, initiator.maxCeLen, 100)
            """
                UpperTester expects a HCI_Command_Status event after sending the HCI_LE_Connection_Update command
            """
            if(has_event(transport, upperTester, 100)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
                success = success and (status == 0)
            else:
                success = False
            """
                LowerTester expects a BT_HCI_EVT_LE_CONN_PARAM_REQ control PDU from the IUT
            """
            if(has_event(transport, lowerTester, 100)):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                          (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
                showEvent(event, eventData, trace)
            else:
                success = False
            transport.wait(400) # send some empty data packets
            """
                Upper Tester expects an HCI_LE_Connection_Update_Complete from the IUT
            """
            if(has_event(transport, upperTester, 100)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                          (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE)
                status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
                success = success and (status == 0) and (timeout == supervisionTimeouts[i])
            else:
                success = False
            trace.trace(7, "Test case #" + str(i+1) + (" PASSED" if success else " FAILED"))
            flush_events(transport, lowerTester, 100) #flush events before the next test case
    else:
        advertiser.disable()

    success = success and initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-25-C [Initiate connection parameter request - Reject]
"""
def ll_con_sla_bv_25_c(transport, upperTester, lowerTester, trace):

    testInterval = 6
    testSupervision = 300
    errCode = 0x0C

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]
    initiatorAddress = Address( ExtendedAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ))
    success = True

    success = success and advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    transport.wait(200)
    if connected:
        le_connection_update(transport, upperTester, initiator.handles[1], testInterval, testInterval, initiator.latency, \
                             testSupervision, initiator.minCeLen, initiator.maxCeLen, 100)
        transport.wait(100)
        status, handle = le_remote_connection_parameter_request_negative_reply(transport, lowerTester, initiator.handles[0], errCode, 100)
        success = success and (status == 0)
        """
            UpperTester expects a HCI_Command_Status event after sending the HCI_LE_Connection_Update command
        """
        if (has_event(transport, upperTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
            success = success and (status == 0)
        else:
            success = False
        """
            LowerTester expects a BT_HCI_EVT_LE_CONN_PARAM_REQ control PDU from the IUT
        """
        if (has_event(transport, lowerTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                        (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
            showEvent(event, eventData, trace)
        else:
            success = False
        transport.wait(400) # send some empty data packets
        """
            Upper Tester expects an HCI_LE_Connection_Update_Complete from the IUT with the assigned error code
        """
        if (has_event(transport, upperTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                        (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == errCode)
        else:
            success = False
        flush_events(transport, lowerTester, 100) #flush events before the next test case
    else:
        advertiser.disable()

    success = success and initiator.disconnect(0x3E)

    return success

"""
    LL/CON/SLA/BV-26-C [Initiate connection parameter request - same procedure collision]
"""
def ll_con_sla_bv_26_c(transport, upperTester, lowerTester, trace):
    interval = 6
    testSupervision = 300
    errCode = 0x23

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
        """
            Send HCI_LE_Connection_Update command to the IUT from slave...
        """
        le_connection_update(transport, upperTester, initiator.handles[1], interval, interval, initiator.latency, \
                       testSupervision, initiator.minCeLen, initiator.maxCeLen, 100)
        """
            Verify that upper tester receives the command status 0x00
        """
        if(has_event(transport, upperTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
            showEvent(event, eventData, trace)
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_CMD_STATUS)
        else:
            success = False
        """
            Verify that lower tester receives a LE Remote Connection Parameter Request Event...
        """
        if(has_event(transport, lowerTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
            success = success and rightEvent
            """
                Send LL_REJECT_EXT_IND to IUT with error code 0x23 to IUT...
            """
            le_remote_connection_parameter_request_negative_reply(transport, lowerTester, initiator.handles[0], errCode, 100)
            if(has_event(transport, lowerTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                showEvent(event, eventData, trace)
            """
                Expect an LE_Connection_Update_Complete event with error code 0x23 from IUT
            """
            if(has_event(transport, upperTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                            (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == errCode)
            else:
                success = False
            """
                Send LL_CONNECTION_PARAM_REQ to IUT...
            """
            success = success and initiator.update(interval, interval, initiator.latency, testSupervision)
            """
                Upper tester expects HCI_LE_Remote_Connection_Parameter_Request_Event
            """
            if(has_event(transport, upperTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                """
                    Upper tester sends HCI_LE_Remote_Connection_Parameter_Request_Reply
                """
                status, handle = le_remote_connection_parameter_request_reply(transport, upperTester, initiator.handles[1], interval, interval, \
                                                                              0, 300, initiator.minCeLen, initiator.maxCeLen, 100)
                success = success and (status == 0x00)
            else:
                success = False
                
            get_event(transport, upperTester, 100) # command status event
            """
                Verify if upper tester received LE Connection Update Complete event
            """
            if(has_event(transport, upperTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                            (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == 0x00)
            else:
                success = False
            """
                Verify if lower tester received LE Connection Update Complete event
            """
            if(has_event(transport, lowerTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                showEvent(event, eventData, trace)
                status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                            (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == 0x00)
            else:
                success = False
            transport.wait(int(4 * interval * 1.25))
        else:
            advertiser.disable()

        success = success and initiator.disconnect(0x3E)
    else:
        success = False

    return success

"""
    LL/CON/SLA/BV-27-C [Initiate connection parameter request - different procedure collision - channel map update]
"""
def ll_con_sla_bv_27_c(transport, upperTester, lowerTester, trace):

    interval = 6
    testSupervision = 300
    errCode = 0x2A

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
        """
            Send HCI_LE_Connection_Update command to the IUT from slave...
        """
        le_connection_update(transport, upperTester, initiator.handles[1], interval, interval, initiator.latency, \
                       testSupervision, initiator.minCeLen, initiator.maxCeLen, 100)
        """
            Verify that upper tester receives the command status 0x00
        """
        if(has_event(transport, upperTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
            showEvent(event, eventData, trace)
            success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_CMD_STATUS)
        else:
            success = False
        """
            Verify that lower tester receives a LE Remote Connection Parameter Request Event...
        """
        if (has_event(transport, lowerTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
            success = success and rightEvent
        else:
            success = False
        """
            Use only even channels for sending a LL_CHANNEL_MAP_REQ...
        """
        channelMap = 0x1555555555
        status = le_set_host_channel_classification(transport, lowerTester, toArray(channelMap,5), 100)
        success = success and (status == 0x00)
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
        showEvent(event, eventData, trace)
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
        """
            Send LL_REJECT_EXT_IND to IUT with error code 0x23 to IUT...
        """
        le_remote_connection_parameter_request_negative_reply(transport, lowerTester, initiator.handles[0], errCode, 100)
        if (has_event(transport, lowerTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
        else:
            success = False
        """
            Expect an LE_Connection_Update_Complete event with error code 0x23 from IUT
        """
        if (has_event(transport, upperTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                        (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == errCode)
        else:
            advertiser.disable()

        transport.wait(int(8 * interval * 1.25))

        success = success and initiator.disconnect(0x3E)
    else:
        success = False

    return success

"""
    LL/CON/SLA/BV-29-C [Accepting connection parameter request - no Preffered_Periodicity]
"""
def ll_con_sla_bv_29_c(transport, upperTester, lowerTester, trace):

    intervals = [6, 32, 6]
    testSupervision = [300, 3200, 300]

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
        for i in range(0, len(intervals)):
            #transport.wait(100)
            """
                Send HCI_LE_Connection_Update command to the IUT from slave...
            """
            le_connection_update(transport, lowerTester, initiator.handles[0], intervals[i], intervals[i], initiator.latency, \
                        testSupervision[i], initiator.minCeLen, initiator.maxCeLen, 100)
            """
                Verify that lower tester receives the command status 0x00
            """
            if (has_event(transport, lowerTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                status, numPackets, opCode = struct.unpack('<BBH', eventData[:4])
                showEvent(event, eventData, trace)
                success = success and (status == 0x00) and (event == Events.BT_HCI_EVT_CMD_STATUS)
            else:
                success = False
            """
                Verify that upper tester receives a LE Remote Connection Parameter Request Event...
            """
            if (has_event(transport, upperTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
            else:
                success = False
            """
                Send LE Remote Connection Parameter Request Reply from upper tester to IUT...
            """
            le_remote_connection_parameter_request_reply(transport, upperTester, initiator.handles[1], intervals[i], intervals[i], \
                                                         initiator.latency, testSupervision[i], initiator.minCeLen, initiator.maxCeLen, 100)
            if (has_event(transport, upperTester, 200)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
            else:
                success = False
            """
                Expect an LE_Connection_Update_Complete event with error code 0x00 from IUT
            """
            if (has_event(transport, upperTester, 500)):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                showEvent(event, eventData, trace)
                status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                            (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == 0x00)
            else:
                success = False

            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            showEvent(event, eventData, trace)
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and \
                        (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == 0x00)
            transport.wait(int(15 * interval * 1.25))
        disconnected = initiator.disconnect(0x3E)
        success = success and disconnected
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-33-C [Accepting Connection Parameter Request – event masked]
"""
def ll_con_sla_bv_33_c(transport, upperTester, lowerTester, trace):

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

    success = advertiser.enable()
    """
        Lower Tester initiates a connection in the master role
    """
    connected = initiator.connect()
    success = success and connected
    if connected:
        transport.wait(100)
        """
            Mask LE Remote Connection Parameter Request Event
        """
        events = [0x1F, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
        status = le_set_event_mask(transport, upperTester, events, 100)
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
        showEvent(event, eventData, trace)
        success = success and (status == 0) and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
        """
            Send LL_CONNECTION_PARAM_REQ to IUT...
        """
        updated = initiator.update(interval, interval, initiator.latency, testSupervision)
        success = success and updated
        """
            Verify that lower tester receives a LL_REJECT_EXT_IND... unfortunately we cannot verify that (but it appears in the trace)!
        """
        success = success and initiator.updated()

        transport.wait(int(8 * initiator.intervalMin * 1.25))
        connected = not initiator.disconnect(0x3E)
        success = success and not connected
    else:
        success = False

    return success

"""
    LL/CON/SLA/BV-34-C [Accepting Connection Parameter Request – host rejects]
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
        status = initiator.update(interval, interval, initiator.latency, testSupervision)
        success = success and status
        """
            Upper tester expects HCI_LE_Remote_Connection_Parameter_Request_Event
        """
        if (has_event(transport, upperTester, 200)):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ)
            """
                Upper tester sends HCI_LE_Remote_Connection_Parameter_Request_Reply
            """
            status, handle = le_remote_connection_parameter_request_negative_reply(transport, upperTester, initiator.handles[1], errCode, 100)
            success = success and (status == 0x00)
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            showEvent(event, eventData, trace)
        else:
            success = False

        if (has_event(transport, lowerTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
            showEvent(event, eventData, trace)
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE) and (status == errCode)
        else:
            success = False

        transport.wait(int(8 * initiator.intervalMin * 1.25))
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-40-C [Initiate PHY Update Procedure]
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
    initiator.switchRoles()
    if connected:
        transport.wait(100)

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
    LL/CON/SLA/BV-42-C [Responding to PHY Update Procedure]
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
    LL/CON/SLA/BV-78-C [Slave Data Length Update - Initiating Data Length Update Procedure, LE 1M PHY]

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
            status, handle = le_set_data_length(transport, upperTester, initiator.handles[1], TxOctets, TxTime, 100)
            trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X" % (status, handle))
            success = success and (status == 0)
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
            showEvent(event, eventData, trace)
        
            if has_event(transport, lowerTester, 200):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                if success:
                    showEvent(event, eventData, trace)
                    if has_event(transport, upperTester, 200):
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                        success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                        if success:
                            showEvent(event, eventData, trace)
                    
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BV-81-C [Slave Data Length Update - Initiating Data Length Update Procedure, LE 2M PHY]

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
            status, handle = le_set_data_length(transport, upperTester, initiator.handles[1], TxOctets, TxTime, 100)
            trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X" % (status, handle))
            success = success and (status == 0)
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
            showEvent(event, eventData, trace)
        
            if has_event(transport, lowerTester, 200):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                if success:
                    showEvent(event, eventData, trace)
                    if has_event(transport, upperTester, 200):
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                        success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                        showEvent(event, eventData, trace)
        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)
    else:
        advertiser.disable()

    return success

"""
    LL/CON/SLA/BI-08-C [Accepting Connection Parameter Request – Illegal Parameters]
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
        status = initiator.update(interval, interval, initiator.latency, 300)
        success = success and status
        """
            Verify that lower tester receives a LL_REJECT_EXT_IND...
        """
        if(has_event(transport, lowerTester, 100)):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
            success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_UPDATE_COMPLETE)
            status, handle, interval, latency, timeout = struct.unpack('<BHHHH', eventData[1:10])
            success = success and (status == errCode)
            showEvent(event, eventData, trace)
        else:
            success = False

        transport.wait(int(8 * initiator.intervalMin * 1.25))
    else:
        advertiser.disable()
        
    disconnected = initiator.disconnect(0x3E)
    success = success and disconnected

    return success

"""
    LL/CON/MAS/BV-03-C [Master Sending Data]
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
    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, lowerTester, 100);
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers));
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

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
                status = le_data_write(transport, upperTester, initiator.handles[0], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, upperTester, 200);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    hasData = le_data_ready(transport, lowerTester, 200);
                    success = success and hasData;
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            
        if maxPacketLength > 27:
            """
                Sending Data Packets with a random length greater than 27...
            """
            pbFlags = 0;
            count = 1 + int(1000/maxPacketLength);

            for j in range(count):
                txData = [0 for _ in range(random.randint(28,maxPacketLength))];

                status = le_data_write(transport, upperTester, initiator.handles[0], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, upperTester, 100);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    rxDataLength = 0;
                    while success and (rxDataLength < len(txData)):
                        hasData = le_data_ready(transport, lowerTester, 100);
                        success = success and hasData;
                        if hasData:
                            time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                            trace.trace(6, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxData), formatArray(rxData)));
                            rxDataLength += len(rxData);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-04-C [Master Receiving Data]
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
                status = le_data_write(transport, lowerTester, initiator.handles[1], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, lowerTester, 200);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    hasData = le_data_ready(transport, upperTester, 200);
                    success = success and hasData;
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100);
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-05-C [Master Sending and Receiving Data]
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
            status = le_data_write(transport, upperTester, initiator.handles[0], pbFlags, 0, txData, 100);
            dataSent = status == 0;
            success = success and dataSent;
            if dataSent:
                dataSent = has_event(transport, upperTester, 100);
                success = success and dataSent;
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                hasData = le_data_ready(transport, lowerTester, 200);
                success = success and hasData;
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                else:
                    trace.trace(6, "Lower Tester didn't receive any data!");
            else:
                trace.trace(6, "LE Data Write Command failed in Upper Tester - returns status: 0x%02X" % status);

            """
                Lower Tester is sending Data...
            """
            status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100);
            dataSent = status == 0;
            success = success and dataSent;
            if dataSent:
                dataSent = has_event(transport, lowerTester, 100);
                success = success and dataSent;
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                hasData = le_data_ready(transport, upperTester, 200);
                success = success and hasData;
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100);
                else:
                    trace.trace(6, "Upper Tester didn't receive any data!");
            else:
                trace.trace(6, "LE Data Write Command failed in Lower Tester - returns status: 0x%02X" % status);
            
        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-07-C [Requesting Parameter Update]
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
    LL/CON/MAS/BV-08-C [Master Sending Termination]
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
    LL/CON/MAS/BV-09-C [Master Accepting Termination]
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
    LL/CON/MAS/BV-13-C [Feature Setup Request]
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
        status, features = le_read_local_supported_features(transport, upperTester, 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showLEFeatures(features, trace);
        """
            Issue the LE Read Remote Features Command, verify the reception of a Command Status Event
        """
        status = le_read_remote_features(transport, upperTester, initiator.handles[1], 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_STATUS);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        isLRRFCCEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE);
        success = success and isLRRFCCEvent;
        if isLRRFCCEvent:
            status, handle, features = remoteFeatures(eventData);
            success = success and (status == 0);
            showLEFeatures(features, trace);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-20-C [Master Request Version]
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
        status = read_remote_version_information(transport, upperTester, initiator.handles[1], 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_STATUS);
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        isRRVICEvent = (event == Events.BT_HCI_EVT_REMOTE_VERSION_INFO);
        success = success and isRRVICEvent;
        if isRRVICEvent:
            status, handle, version, manufacturerID, subVersion = remoteVersion(eventData);
            success = success and (status == 0);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-21-C [Master Respond Version]
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
        status = read_remote_version_information(transport, lowerTester, initiator.handles[1], 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_STATUS);
        """
            Await the reception of a Read Remote Version Information Complete Event
        """
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        showEvent(event, eventData, trace);
        isRRVICEvent = (event == Events.BT_HCI_EVT_REMOTE_VERSION_INFO);
        success = success and isRRVICEvent;
        if isRRVICEvent:
            status, handle, version, manufacturerID, subVersion = remoteVersion(eventData);
            success = success and (status == 0);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-23-C [Responding to Feature Exchange]
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
        status = le_read_remote_features(transport, lowerTester, initiator.handles[1], 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_STATUS);
        """
            Await the reception of a LE Read Remote Features Command Complete Event
        """
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        showEvent(event, eventData, trace);
        isLRRFCCEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_REMOTE_FEAT_COMPLETE);
        success = success and isLRRFCCEvent;
        if isLRRFCCEvent:
            status, handle, features = remoteFeatures(eventData);
            success = success and (status == 0);
            showLEFeatures(features, trace);

        disconnected = initiator.disconnect(0x3E);
        success = success and disconnected;
    else:
        advertiser.disable();

    return success

"""
    LL/CON/MAS/BV-24-C [Initiating Connection Parameter Request - Accept]
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
    LL/CON/MAS/BV-25-C [Initiating Connection Parameter Request - Reject]
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
    LL/CON/MAS/BV-26-C [Initiating Connection Parameter Request - same procedure collision]
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
        transport.wait(100);
    
        interval = 6; timeout = 300;
        """
            Request an update of the connection parameters - sends an LL_CONNECTION_PARAM_REQ...
        """
        success = success and initiator.update(interval, interval, initiator.latency, timeout);
        """
            Verify that the lower tester receives a LE Remote Connection Parameter Request Event...
        """
        gotEvent = has_event(transport, lowerTester, 3200);
        success = success and gotEvent;
        if gotEvent:
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
            showEvent(event, eventData, trace);
            rightEvent = (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_CONN_PARAM_REQ);
            success = success and rightEvent;
            if rightEvent:
                handle, minInterval, maxInterval, latency, timeout = remoteConnectionParameterRequest(eventData);
                success = success and (minInterval == interval) and (maxInterval == interval);
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
                initiator.pre_updated = True;
                """
                    Send a LL_CONNECTION_PARAM_RSP as a reaction to the original LE Remote Connection Parameter Request Event...
                """
                minCeLen = maxCeLen = 0;
                status, handle = le_remote_connection_parameter_request_reply(transport, lowerTester, handle, minInterval, maxInterval, \
                                                                              latency, timeout, minCeLen, maxCeLen, 100);

                success = success and (status == 0);
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                showEvent(event, eventData, trace);
                success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
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
    LL/CON/MAS/BV-27-C [Initiating Connection Parameter Request - different procedure collision - channel map update]
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
        channelMap = 0x1555555555;
        status = le_set_host_channel_classification(transport, upperTester, toArray(channelMap,5), 100);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        showEvent(event, eventData, trace);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);

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
    LL/CON/MAS/BV-29-C [Initiating Connection Parameter Request - remote legacy host]
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
    LL/CON/MAS/BV-30-C [Accepting Connection Parameter Request - no Preferred Periodicity]
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
    LL/CON/MAS/BV-34-C [Accepting Connection Parameter Request - event masked]
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
        
    status = le_set_event_mask(transport, upperTester, events, 100);
    trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
    success = success and (status == 0);
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);
            
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
    LL/CON/MAS/BV-35-C [Accepting Connection Parameter Request - Host rejects]
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
    LL/CON/MAS/BV-41-C [Initiating PHY Update Procedure]
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
    LL/CON/MAS/BV-43-C [Responding to PHY Update Procedure]
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
    LL/CON/MAS/BV-74-C [Master Data Length Update - Initiating Data Length Update Procedure, LE 1M PHY]

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
    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, lowerTester, 100);
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers));
    success = status == 0;
    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
    showEvent(event, eventData, trace);

    success = success and advertiser.enable();

    connected = initiator.connect();        
    success = success and connected;

    cmaxTxOctets = 27; cmaxTxTime = 328;

    if connected:
        for txOctets, txTime in zip([ 60, 27, 251, 60, 27, 251, 60, 27, 251, 60, 27, 251 ], [ 2120, 2120, 2120, 328, 328, 328, 2120, 2120, 2120, 2120, 2120, 2120 ]):
            status, handle = le_set_data_length(transport, upperTester, initiator.handles[0], txOctets, txTime, 100);
            trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X Tx: (%d, %d)" % (status, handle, txOctets, txTime));
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

            changed = not ((cmaxTxOctets == min(txOctets, 60)) and (cmaxTxTime == min(txTime, 592)));

            if changed:
                """
                    Both upper- and lower-Tester should receive a LE Data Length Change event with the new parameters
                """
                hasEvent = has_event(transport, upperTester, 100);
                success = success and hasEvent;
                if hasEvent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
                    if success:
                        showEvent(event, eventData, trace);
                        handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = dataLengthChanged(eventData);
                    
                hasEvent = has_event(transport, lowerTester, 100);
                success = success and hasEvent;
                if hasEvent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
                    if success:
                        showEvent(event, eventData, trace);
            
            pbFlags = 0;
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)];
            status = le_data_write(transport, upperTester, initiator.handles[0], pbFlags, 0, txData, 100);
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
            success = success and (status == 0);
            if success:
                dataSent = has_event(transport, upperTester, 200);
                success = success and dataSent;
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    rxDataLength = 0;
                    while success and (rxDataLength < len(txData)):
                        hasData = le_data_ready(transport, lowerTester, 100);
                        success = success and hasData;
                        if hasData:
                            time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100);
                            trace.trace(6, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxData), formatArray(rxData)));
                            rxDataLength += len(rxData);

            """
                Lower Tester is sending Data...
            """
            for i in range(20):
                txData = [_ for _ in range(27)];
                status = le_data_write(transport, lowerTester, initiator.handles[1], pbFlags, 0, txData, 100);
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status);
                success = success and (status == 0);
                if success:
                    dataSent = has_event(transport, lowerTester, 200);
                    success = success and dataSent;
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS);
                    
                    hasData = le_data_ready(transport, upperTester, 200);
                    success = success and hasData;
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100);
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)));

        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E);

    else:
        advertiser.disable();

    return success;

"""
    LL/CON/MAS/BV-77-C [Master Data Length Update - Initiating Data Length Update Procedure, LE 2M PHY]

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
    status, maxPacketLength, maxPacketNumbers = le_read_buffer_size(transport, lowerTester, 100)
    trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X - Data Packet length %d, Number of Data Packets %d" % (status, maxPacketLength, maxPacketNumbers))
    success = status == 0
    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
    showEvent(event, eventData, trace)

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
            status, handle = le_set_data_length(transport, upperTester, initiator.handles[0], txOctets, txTime, 100)
            trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X Tx: (%d, %d)" % (status, handle, txOctets, txTime))
            success = success and (status == 0)
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
            showEvent(event, eventData, trace)

            changed = not ((cmaxTxOctets == min(txOctets, 60)) and (cmaxTxTime == min(txTime, 592)))

            if changed:
                """
                    Both upper- and lower-Tester should receive a LE Data Length Change event with the new parameters
                """
                hasEvent = has_event(transport, upperTester, 100)
                success = success and hasEvent
                if hasEvent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                    success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                    if success:
                        showEvent(event, eventData, trace)
                        handle, cmaxTxOctets, cmaxTxTime, maxRxOctets, maxRxTime = dataLengthChanged(eventData)
                    
                hasEvent = has_event(transport, lowerTester, 100)
                success = success and hasEvent
                if hasEvent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                    success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE)
                    if success:
                        showEvent(event, eventData, trace)
            
            pbFlags = 0
            """
                Upper Tester is sending Data...
            """
            txData = [_ for _ in range(maxPacketLength)]
            status = le_data_write(transport, upperTester, initiator.handles[0], pbFlags, 0, txData, 100)
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
            success = success and (status == 0)
            if success:
                dataSent = has_event(transport, upperTester, 200)
                success = success and dataSent
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
                    
                    rxDataLength = 0
                    while success and (rxDataLength < len(txData)):
                        hasData = le_data_ready(transport, lowerTester, 100)
                        success = success and hasData
                        if hasData:
                            time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, lowerTester, 100)
                            trace.trace(6, "LE Data Read Command returns PB=%d BC=%d - %2d data bytes: %s" % (rxPBFlags, rxBCFlags, len(rxData), formatArray(rxData)))
                            rxDataLength += len(rxData)

            """
                Lower Tester is sending Data...
            """
            for i in range(20):
                txData = [_ for _ in range(27)]
                status = le_data_write(transport, lowerTester, initiator.handles[1], pbFlags, 0, txData, 100)
                trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
                success = success and (status == 0)
                if success:
                    dataSent = has_event(transport, lowerTester, 200)
                    success = success and dataSent
                    if dataSent:
                        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                        success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
                    
                    hasData = le_data_ready(transport, upperTester, 200)
                    success = success and hasData
                    if hasData:
                        time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                        trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))

        """
            Note: Disconnect can generate another LE Data Length Change event...
        """
        success = success and initiator.disconnect(0x3E)

    else:
        advertiser.disable()

    return success

"""
    LL/CON/MAS/BI-06-C [Accepting Parameter Connection Request - illegal parameters]
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

        success = success and initiator.update(interval, interval, initiator.latency, timeout);
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
    LL/SEC/ADV/BV-01-C [Advertising with static address]
"""
def ll_sec_adv_bv_01_c(transport, upperTester, lowerTester, trace):

    """
        Setting static address for upper tester and lower tester; adding lower tester's address to the whitelist
    """
    lowerAddress = [[ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) | 0xC00000000000L]]
    preamble_specific_white_listed(transport, upperTester, lowerAddress, trace)
    preamble_set_random_address(transport, lowerTester, toNumber(lowerRandomAddress) | 0xC00000000000L, trace)

    upperAddress = [[ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(upperRandomAddress) | 0xC00000000000L]]
    preamble_set_random_address(transport, upperTester, toNumber(upperRandomAddress) | 0xC00000000000L, trace)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM)
    peerAddress = Address(ExtendedAddressType.RESOLVABLE_OR_RANDOM, toNumber(lowerRandomAddress) | 0xC00000000000L)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ]

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 30)

    success = advertiser.enable()
    """
        Start scanning...
    """
    success = success and scanner.enable()
    scanner.monitor()
    transport.wait(200)
    """
        Attempt to change advertiser (upperTester) address...
    """
    success = success and not preamble_set_random_address(transport, upperTester, address_scramble_OUI(toNumber(upperRandomAddress)) | 0xC00000000000L, trace)

    disabled = scanner.disable()
    success = success and disabled
    success = success and scanner.qualifyReports( 5 )
    success = success and scanner.qualifyResponses(5, advertiser.responseData)

    disabled = advertiser.disable()
    success = success and disabled

    return success

"""
    LL/SEC/ADV/BV-02-C [Privacy - Non Connectable Undirected Advertising, non-resolvable private address]
"""
def ll_sec_adv_bv_02_c(transport, upperTester, lowerTester, trace):

    """
        Add Random address of upperTester to the Resolving List
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace );
    success = RPAs.add( Address( SimpleAddressType.RANDOM, upperRandomAddress ) );
    """
        Enable Private Address Resolution
    """
    success = success and RPAs.enable();

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 100)
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

    return success

"""
    LL/SEC/ADV/BV-03-C [Privacy - Non Connectable Undirected Advertising, Resolvable Private Address]
"""
def ll_sec_adv_bv_03_c(transport, upperTester, lowerTester, trace):

    """
        Add Public address of lowerTester to the Resolving List with the upperIRK
    """
    RPAs = ResolvableAddresses( transport, lowerTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC,  0x123456789ABCL ) )

    RPAs_upper = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs_upper.clear()
    success = success and RPAs_upper.add( Address( SimpleAddressType.PUBLIC,  0x123456789ABCL ) )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_upper.enable()
    """
        Scan interval should be three times the average Advertise interval. Scan window should be the maximum possible.
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress)

    scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_NONCONN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20)

    resolvableAddresses = [ 0, 0 ]

    success = success and advertiser.enable()
    success = success and scanner.enable()
    transport.wait(200)
    scanner.monitor()
    success = success and scanner.disable()
    """
        Read local address in resolving list.
    """
    status, resolvableAddresses[0] = local_resolvable_address(transport, lowerTester, Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ), trace)
    success = success and scanner.qualifyReports( 10 )
    trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[0]))
    transport.wait(2000) # Wait for RPA timeout to expire

    success = success and scanner.enable()
    scanner.monitor()
    success = success and scanner.disable()
    """
        Read local address in resolving list.
    """
    status, resolvableAddresses[1] = local_resolvable_address(transport, lowerTester, Address( SimpleAddressType.PUBLIC, 0x123456789ABCL ), trace)
    success = success and scanner.qualifyReports( 10 )
    trace.trace(6, "Local Resolvable Address: %s" % formatAddress(resolvableAddresses[1]))

    success = success and advertiser.disable()
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1])
    success = success and RPAs.disable()
    success = success and RPAs_upper.disable()

    return success

"""
    LL/SEC/ADV/BV-04-C [Network Privacy - Scannable Advertising, non-resolvable private address]
"""
def ll_sec_adv_bv_04_c(transport, upperTester, lowerTester, trace):

    """
        Set advertiser and scanner to use non-resolvable private addresses
    """
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    peerAddress = Address( SimpleAddressType.RANDOM, toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFFL)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)

    ownAddress = Address( ExtendedAddressType.RANDOM)
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20)
    scanner.expectedResponses = 1
    """
        Setting the private non-resolvable address to upper tester
    """
    success = preamble_set_random_address(transport, upperTester, toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL , trace)
    success = success and preamble_set_random_address(transport, lowerTester, toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFFL , trace)

    success = success and advertiser.enable()
    scanner.expectedReports = 100

    success = success and scanner.enable()
    scanner.monitor()
    success = success and scanner.qualifyReports( 100 )
    success = success and scanner.qualifyResponses( 1, advertiser.responseData)
    success = success and scanner.disable()

    disabled = advertiser.disable()
    success = success and disabled

    return success

"""
    LL/SEC/ADV/BV-05-C [Network Privacy - Scannable Advertising, resolvable private address]
"""
def ll_sec_adv_bv_05_c(transport, upperTester, lowerTester, trace):

    """
        Retrieving random addresses and forcing them to be private resolvable
    """
    lowerAddr = 0x123456789ABCL
    upperAddr = 0x456789ABCDEFL
    """
        Configure RPAs to use the upperIRK for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  lowerAddr ), lowerIRK)
        
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK )
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  upperAddr ), upperIRK )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    """
        Adding lowerTester address to the White List
    """
    addresses = [[ ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)
        
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20)
    scanner.expectedResponses = 1
        
    success = success and advertiser.enable()

    resolvableAddresses = [ 0, 0 ]
    for i in range(2):
        if i == 1:
            """
                Wait for RPA timeout
            """
            transport.wait(2000)
        success = success and scanner.enable()
        scanner.monitor()
        success = success and scanner.qualifyReports(10)
        success = success and scanner.qualifyResponses(1)
        success = success and scanner.disable()
        status, resolvableAddresses[i] = local_resolvable_address(transport, upperTester, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ), trace)
        trace.trace(6, "AdvA: %s" % formatAddress(resolvableAddresses[i]))

    success = success and advertiser.disable()
    success = success and toNumber(resolvableAddresses[0]) != toNumber(resolvableAddresses[1])
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-06-C [Network Privacy - Undirected Connectable Advertising no Local IRK, no peer IRK]
"""
def ll_sec_adv_bv_06_c(transport, upperTester, lowerTester, trace):

    upperAddr = toNumber(upperRandomAddress) & 0x3FFFFFFFFFFFL
    lowerAddrType = [SimpleAddressType.PUBLIC, ExtendedAddressType.RESOLVABLE_OR_RANDOM, ExtendedAddressType.RESOLVABLE_OR_RANDOM]
    lowerAddr = [0x456789ABCDEFL, toNumber(lowerRandomAddress) | 0xC00000000000L, (toNumber(lowerRandomAddress) & 0x3FFFFFFFFFFFL)]
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    success = True

    for i in range(len(lowerAddr)):
        peerAddress = Address(lowerAddrType[i], lowerAddr[i])
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                                ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
        initiatorAddress = Address( lowerAddrType[i] )
        initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, upperAddr ))
        """
            Setting upper tester's non-resolvable address
        """
        success = success and preamble_set_random_address(transport, upperTester, upperAddr, trace)
        if i == 0:
            """
                Set lower tester to use Public Address
            """
            success = success and preamble_set_public_address(transport, lowerTester, lowerAddr[i], trace)
        else:
            """
                Set lower tester to use Random Address
            """
            success = success and preamble_set_random_address(transport, lowerTester, lowerAddr[i], trace)
           
        success = success and advertiser.enable()
        """
            Attempt to connect...
        """
        success = success and initiator.connect()
        transport.wait(200)

        success = success and initiator.disconnect(0x13)
        transport.wait(500)

    return success

"""
    LL/SEC/ADV/BV-07-C [Network Privacy - Undirected Connectable Advertising with Local IRK, no peer IRK]
"""
def ll_sec_adv_bv_07_c(transport, upperTester, lowerTester, trace):

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
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)
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
    txData = [0 for _ in range(10)]
    pbFlags = 0

    if connected:
        transport.wait(200)
        """
            Lower Tester is sending Data...
        """
        status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
        trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
        success = success and (status == 0)
        if success:
            dataSent = has_event(transport, lowerTester, 200)
            success = success and dataSent
            if dataSent:
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
            hasData = le_data_ready(transport, upperTester, 200)
            success = success and hasData
            if hasData:
                time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        disconnected = initiator.disconnect(0x13)
        initiator.resetRoles()
        success = success and disconnected
    else:
        advertiser.disable()
        success = False

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-08-C [Network Privacy - Undirected Connectable Advertising with Local IRK, peer IRK]
"""
def ll_sec_adv_bv_08_c(transport, upperTester, lowerTester, trace):

    """
        Set advertiser and scanner to use resolvable private addresses
    """
    initiatorAddr = (toNumber(lowerRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    upperAddr = (toNumber( upperRandomAddress ) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    """
        Configure RPAs to use the upperIRK for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, initiatorAddr ), upperIRK)

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)

    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    addresses = [ [ ExtendedAddressType.RESOLVABLE_OR_PUBLIC, initiatorAddr ] ]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, initiatorAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))
    """
        Setting the private resolvable address to upper and lower tester
    """
    success = success and preamble_set_public_address(transport, lowerTester, initiatorAddr , trace)
    success = success and preamble_set_public_address(transport, upperTester, upperAddr, trace)

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    txData = [0 for _ in range(10)]
    pbFlags = 0

    if connected:
        transport.wait(200)
        """
            Lower Tester is sending Data...
        """
        status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
        trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
        success = success and (status == 0)
        if success:
            dataSent = has_event(transport, lowerTester, 200)
            success = success and dataSent
            if dataSent:
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
            hasData = le_data_ready(transport, upperTester, 200)
            success = success and hasData
            if hasData:
                time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        disconnected = initiator.disconnect(0x13)
        initiator.resetRoles()
        success = success and disconnected
    else:
        advertiser.disable()
        success = False

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-09-C [Network Privacy - Undirected Connectable Advertising without Local IRK, peer IRK]
"""
def ll_sec_adv_bv_09_c(transport, upperTester, lowerTester, trace):

    initiatorAddr = (toNumber(lowerRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    """
        Configure RPAs to use the upperIRK for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.PUBLIC, initiatorAddr ) )
    success = success and RPAs.enable()
    """
        Add initiator address to the White List
    """
    addresses = [[ ExtendedAddressType.RESOLVABLE_OR_RANDOM, initiatorAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)

    ownAddress = Address( ExtendedAddressType.PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, initiatorAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ))
    """
        Setting the addresses to upper and lower tester
    """
    success = success and preamble_set_public_address(transport, upperTester, 0x456789ABCDEFL, trace)
    success = success and preamble_set_random_address(transport, lowerTester, initiatorAddr , trace)

    success = success and advertiser.enable()

    connected = initiator.connect()
    success = success and connected

    txData = [0 for _ in range(10)]
    pbFlags = 0

    if connected:
        transport.wait(200)
        """
            Lower Tester is sending Data...
        """
        status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
        trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
        success = success and (status == 0)
        if success:
            dataSent = has_event(transport, lowerTester, 200)
            success = success and dataSent
            if dataSent:
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
            hasData = le_data_ready(transport, upperTester, 200)
            success = success and hasData
            if hasData:
                time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        disconnected = initiator.disconnect(0x13)
        initiator.resetRoles()
        success = success and disconnected
    else:
        advertiser.disable()
        success = False
            
    success = success and RPAs.disable()

    return success

"""
    LL/SEC/ADV/BV-10-C [Network Privacy - Undirected Connectable Advertising using Resolving List and Peer Device Identity not in the List]
"""
def ll_sec_adv_bv_10_c(transport, upperTester, lowerTester, trace):

    """
        Retreive resolvable private address for lower tester
    """
    lowerAddr = (toNumber(lowerRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    """
        Configure RPAs to use for address resolutions (incorrect (0) IRK for lower tester identity address)
    """
    addresses = [[ ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ]]
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace)

    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = success and RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ))

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)

    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    lowerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))
    success = success and advertiser.enable()

    connected = initiator.connect()
    success = success and (not connected)
    if not success:
        initiator.disconnect(0x13)

    success = success and advertiser.disable()
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-11-C [Network Privacy - Directed Connectable Advertising using local and remote IRK]
"""
def ll_sec_adv_bv_11_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs for use in address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ), lowerIRK)

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)
    """
        Enable RPAs...
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    lowerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))

    success = success and advertiser.enable()

    connected = initiator.connect()
    success = success and connected
    if success:
        txData = [0 for _ in range(10)]
        pbFlags = 0
        transport.wait(200)
        """
            Attempt to send data from lower tester...
        """
        status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
        trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
        success = success and (status == 0)
        if success:
            dataSent = has_event(transport, lowerTester, 200)
            success = success and dataSent
            if dataSent:
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
            hasData = le_data_ready(transport, upperTester, 200)
            success = success and hasData
            if hasData:
                time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
        """
            Upper tester (SLAVE) terminates the connection
        """
        initiator.switchRoles()
        disconnected = initiator.disconnect(0x13)
        initiator.resetRoles()
        success = success and disconnected
    else:
        advertiser.disable()

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-12-C [Network Privacy - Directed Connectable Advertising using local IRK, but not remote IRK]
"""
def ll_sec_adv_bv_12_c(transport, upperTester, lowerTester, trace):

    lowerAddr = 0x123456789ABCL
    """
        Configure RPAs for use in address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace)
    success = RPAs_lower.clear() and RPAs.clear() 

    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC, lowerAddr ))
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)
    """
        Enable RPAs...
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( SimpleAddressType.PUBLIC, lowerAddr )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    lowerAddress = Address( SimpleAddressType.PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))
    success = success and preamble_set_public_address(transport, lowerTester, lowerAddr, trace)
    for i in range(2):
        if i == 1:
            transport.wait( 2000 ) # wait for RPA to timeout
        success = success and advertiser.enable()
        connected = initiator.connect()
        success = success and connected
        if success:
            txData = [0 for _ in range(10)]
            pbFlags = 0
            resolvableAddresses = [ 0, 0 ]
            transport.wait(200)
            """
                Attempt to send data from lower tester...
            """
            status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
            success = success and (status == 0)
            if success:
                dataSent = has_event(transport, lowerTester, 200)
                success = success and dataSent
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
                hasData = le_data_ready(transport, upperTester, 200)
                success = success and hasData
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                    trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
            """
                Read the resolvable address used in the AdvA field
            """
            status, resolvableAddresses[i] = local_resolvable_address(transport, upperTester, Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, lowerAddr ), trace)
            trace.trace(6, "AdvA Address: %s" % formatAddress(resolvableAddresses[i]))
            """
                Upper tester (SLAVE) terminates the connection
            """
            initiator.switchRoles()
            disconnected = initiator.disconnect(0x13)
            initiator.resetRoles()
            success = success and disconnected
        else:
            advertiser.disable()
            success = False
            break
        
    success = success and (resolvableAddresses[0] != resolvableAddresses[1])
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-13-C [Network Privacy - Directed Connectable Advertising without local IRK, but with remote IRK]
"""
def ll_sec_adv_bv_13_c(transport, upperTester, lowerTester, trace):

    upperAddr = toNumber( upperRandomAddress ) | 0xC00000000000L
    """
        Configure RPAs for use in address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK)
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)
    success = RPAs.clear() 
    success = success and RPAs_lower.clear()

    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ))
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, upperAddr ))
    """
        Enable RPAs...
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE)
    lowerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, Address( ExtendedAddressType.RESOLVABLE_OR_RANDOM, upperAddr ))

    for i in range(2):
        if i == 1:
            transport.wait( 2000 ) # wait for RPA to timeout
        success = success and advertiser.enable()
        connected = initiator.connect()
        success = success and connected
        if success:
            txData = [0 for _ in range(10)]
            pbFlags = 0
            resolvableAddresses = [ 0, 0 ]
            transport.wait(200)
            """
                Attempt to send data from lower tester...
            """
            status = le_data_write(transport, lowerTester, initiator.handles[0], pbFlags, 0, txData, 100)
            trace.trace(6, "LE Data Write Command returns status: 0x%02X" % status)
            success = success and (status == 0)
            if success:
                dataSent = has_event(transport, lowerTester, 200)
                success = success and dataSent
                if dataSent:
                    eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100)
                    success = success and (event == Events.BT_HCI_EVT_NUM_COMPLETED_PACKETS)
                hasData = le_data_ready(transport, upperTester, 200)
                success = success and hasData
                if hasData:
                    time, handle, rxPBFlags, rxBCFlags, rxData = le_data_read(transport, upperTester, 100)
                    trace.trace(6, "LE Data Read Command returns %d data bytes: %s" % (len(rxData), formatArray(rxData)))
            """
                Read the resolvable address used in the InitA field
            """
            status, resolvableAddresses[i] = local_resolvable_address(transport, upperTester, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ), trace)
            trace.trace(6, "AdvA Address: %s" % formatAddress(resolvableAddresses[i]))
            success = success and (status == 0)
            """
                Upper tester (SLAVE) terminates the connection
            """
            initiator.switchRoles()
            disconnected = initiator.disconnect(0x13)
            initiator.resetRoles()
            success = success and disconnected
        else:
            advertiser.disable()
            success = False
            break

    success = success and (resolvableAddresses[0] != resolvableAddresses[1])
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-14-C [Network Privacy - Directed Connectable Advertising without local IRK, but with remote IRK]
"""
def ll_sec_adv_bv_14_c(transport, upperTester, lowerTester, trace):

    """
        Retreive resolvable private address for lower tester
    """
    lowerAddr = (toNumber(lowerRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    fakeIRK = [1 for _ in range(16)]
    """
        Configure RPAs to use for address resolutions (incorrect IRK for lower tester identity address)
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace)
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ), fakeIRK)

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace, lowerIRK)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)

    addresses = [[ ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)

    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    lowerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))
    success = success and preamble_set_random_address(transport, lowerTester, lowerAddr, trace)

    success = success and advertiser.enable()
    """
        Initiate connection
    """
    connected = initiator.connect()
    success = success and not connected
    transport.wait(200)
    if success:
        success = success and advertiser.disable()
    else:
        initiator.disconnect(0x13)
        advertiser.disable()
        success = False

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-15-C [Network Privacy - Scannable Advertising, resolvable private address, Ignore Identity Address]
"""
def ll_sec_adv_bv_15_c(transport, upperTester, lowerTester, trace):

    lowerAddr = 0x123456789ABCL
    upperAddr = 0x456789ABCDEFL
    """
        Configure RPAs to use the upperIRK for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  lowerAddr ))
        
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace )
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  upperAddr ), upperIRK )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    """
        Adding lowerTester address to the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, lowerAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)
        
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()
    """
        Enable device privacy mode...
    """
    status = le_set_privacy_mode(transport, upperTester, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, toArray(lowerAddr, 6), 0, 200)
    success = success and (status == 0)
    if has_event(transport, upperTester, 100):
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
        showEvent(event, eventData, trace)
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20)
    success = success and preamble_set_public_address(transport, lowerTester, lowerAddr, trace)
    success = success and preamble_set_public_address(transport, upperTester, upperAddr, trace)

    success = success and advertiser.enable()

    success = success and scanner.enable()
    scanner.monitor()
    success = success and scanner.qualifyReports(10)
    success = success and not scanner.qualifyResponses(1)
    success = success and scanner.disable()

    success = success and advertiser.disable()
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-16-C [Network Privacy - Undirected Connectable Advertising with Local IRK and Peer IRK, Ignore Identity Address]
"""
def ll_sec_adv_bv_16_c(transport, upperTester, lowerTester, trace):

    upperAddr = (toNumber(upperRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    lowerAddrType = SimpleAddressType.PUBLIC
    lowerAddr = 0x456789ABCDEFL

    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC,  lowerAddr ))

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace )
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  upperAddr ), upperIRK )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    """
        Adding lowerTester address to the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, lowerAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)
    success = success and RPAs.enable() and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address(lowerAddrType, lowerAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)

    initiatorAddress = Address( lowerAddrType )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, upperAddr ))
    """
        Setting upper tester's resolvable address
    """
    success = success and preamble_set_random_address(transport, upperTester, upperAddr, trace)
    success = success and preamble_set_public_address(transport, lowerTester, lowerAddr, trace)
    """
        Start advertising and attempt to connect...
    """
    success = success and advertiser.enable()
    success = success and not initiator.connect()
    if not success:
        initiator.disconnect(0x13)
    else:
        success = success and advertiser.disable()

    return success

"""
    LL/SEC/ADV/BV-17-C [Network Privacy - Directed Connectable Advertising using local and remote IRK, Ignore Identity Address]
"""
def ll_sec_adv_bv_17_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs for use in address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ))

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL), upperIRK)
    """
        Adding device identity of lower tester to the whitelist
    """
    addresses = [[ ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)
    """
        Enable RPAs...
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    lowerAddrType = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddrType, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL ))

    success = success and preamble_set_random_address(transport, upperTester, 0x456789ABCDEFL, trace)
    success = success and preamble_set_public_address(transport, lowerTester, 0x123456789ABCL, trace)

    status = le_set_privacy_mode(transport, upperTester, SimpleAddressType.PUBLIC, toArray(0x023456789ABCL, 6), 0, 2000)
    if has_event(transport, upperTester, 100):
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
        showEvent(event, eventData, trace)

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and not connected
    if not success:
        initiator.disconnect(0x13)
    else:
        success = success and advertiser.disable()
        initiator.disconnect(0x13)

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-18-C [Device Privacy - Scannable Advertising, resolvable private address, Accept Identity Address]
"""
def ll_sec_adv_bv_18_c(transport, upperTester, lowerTester, trace):

    lowerAddr = 0x123456789ABCL
    upperAddr = 0x456789ABCDEFL
    """
        Configure RPAs to use the upperIRK for address resolutions
    """
    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr ))
        
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace )
    success = RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  upperAddr ), upperIRK )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    """
        Adding lowerTester address to the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, lowerAddr ]]
    success = preamble_specific_white_listed(transport, upperTester, addresses, trace)
        
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()
    """
        Enable device privacy mode...
    """
    status = le_set_privacy_mode(transport, upperTester, ExtendedAddressType.RESOLVABLE_OR_PUBLIC, toArray(lowerAddr, 6), 1, 200)
    if has_event(transport, upperTester, 100):
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
        showEvent(event, eventData, trace)
    """
        Setting up scanner and advertiser (filter-policy: scan requests)
    """ 
    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, lowerAddr )
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.SCANNABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_SCAN_REQUESTS)

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_SCAN_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 20)
    preamble_set_public_address(transport, lowerTester, lowerAddr, trace)
    preamble_set_public_address(transport, upperTester, upperAddr, trace)

    success = success and advertiser.enable()

    success = success and scanner.enable()
    scanner.monitor()
    success = success and scanner.qualifyReports(10)
    success = success and scanner.qualifyResponses(1)
    success = success and scanner.disable()

    success = success and advertiser.disable()
    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

"""
    LL/SEC/ADV/BV-19-C [Device Privacy - Undirected Connectable Advertising with Local IRK and Peer IRK, Accept Identity Address]
"""
def ll_sec_adv_bv_19_c(transport, upperTester, lowerTester, trace):

    """
        Retrieving random addresses and forcing it to be private resolvable
    """
    upperAddr = (toNumber(upperRandomAddress) | 0x400000000000L) & 0x7FFFFFFFFFFFL
    lowerAddrType = SimpleAddressType.PUBLIC
    lowerAddr = 0x456789ABCDEFL

    RPAs = ResolvableAddresses( transport, upperTester, trace, upperIRK )
    success = RPAs.clear()
    success = success and RPAs.add( Address( SimpleAddressType.PUBLIC,  lowerAddr ))
        
    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace )
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC,  upperAddr ), upperIRK )
    """
        Set resolvable private address timeout in seconds ( two seconds )
    """
    success = success and RPAs.timeout( 2 )
    """
        Adding lowerTester address to the White List
    """
    addresses = [[ SimpleAddressType.PUBLIC, lowerAddr ]]
    success = success and preamble_specific_white_listed(transport, upperTester, addresses, trace)
        
    success = success and RPAs.enable() and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    peerAddress = Address(lowerAddrType, lowerAddr)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, \
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)

    initiatorAddress = Address( lowerAddrType )
    initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, upperAddr ))
    """
        Setting upper tester's resolvable address
    """
    success = success and preamble_set_random_address(transport, upperTester, upperAddr, trace)
    success = success and preamble_set_public_address(transport, lowerTester, lowerAddr, trace)

    status = le_set_privacy_mode(transport, upperTester, SimpleAddressType.PUBLIC, toArray(lowerAddr, 6), 1, 200)
    if has_event(transport, upperTester, 100):
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
        showEvent(event, eventData, trace)
    success = success and (status == 0)
    """
        Start advertising and attempt to connect...
    """
    success = success and advertiser.enable()
    success = success and initiator.connect()
    if success:
        initiator.disconnect(0x13)
    else:
        advertiser.disable()
        success = False

    return success

"""
    LL/SEC/ADV/BV-20-C [Device Privacy - Directed Connectable Advertising using local and remote IRK, Accept Identity Address]
"""
def ll_sec_adv_bv_20_c(transport, upperTester, lowerTester, trace):

    """
        Configure RPAs for use in address resolutions
    """
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
    ownAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
       
    RPAs = ResolvableAddresses( transport, upperTester, trace )
    success = RPAs.clear()
    success = success and RPAs.add( peerAddress, lowerIRK)

    RPAs_lower = ResolvableAddresses( transport, lowerTester, trace)
    success = success and RPAs_lower.clear()
    success = success and RPAs_lower.add( ownAddress)
    """
        Enabling device privacy mode...
    """
    status = le_set_privacy_mode(transport, upperTester, peerAddress.type, peerAddress.address, PrivacyMode.DEVICE_PRIVACY, 200)
    success = success and status == 0
    eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100)
    success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE)
    showEvent(event, eventData, trace)
    """
        Enable RPAs...
    """
    success = success and RPAs.timeout( 2 )
    success = success and RPAs.enable()
    success = success and RPAs_lower.enable()

    ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL )
    peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL)
    advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_HDC_DIRECTED, 
                            ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_BOTH_REQUESTS)
    lowerAddrType = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC )
    initiator = Initiator(transport, lowerTester, upperTester, trace, lowerAddrType, Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x123456789ABCL ))

    success = success and advertiser.enable()
    connected = initiator.connect()
    success = success and connected

    if success:
        initiator.disconnect(0x13)
    else:
        success = False
        advertiser.disable()
        RPAs.disable()
        RPAs_lower.disable()

    success = success and RPAs.disable()
    success = success and RPAs_lower.disable()

    return success

__tests__ = {
    "LL/CON/ADV/BV-01-C": [ ll_con_adv_bv_01_c, "Accepting Connections" ],
    "LL/CON/ADV/BV-04-C": [ ll_con_adv_bv_04_c, "Directed Advertising Connection" ],
    "LL/CON/ADV/BV-09-C": [ ll_con_adv_bv_09_c, "Accepting Connections, Channel Selection Algorithm #2" ],
    "LL/CON/ADV/BV-10-C": [ ll_con_adv_bv_10_c, "Directed Advertising Connection, Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-01-C": [ ll_con_ini_bv_01_c, "Connection Initiation" ],
    "LL/CON/INI/BV-02-C": [ ll_con_ini_bv_02_c, "Connecting to Directed Advertising" ],
    "LL/CON/INI/BV-06-C": [ ll_con_ini_bv_06_c, "Initiation Device Filtering: Undirected" ],
    "LL/CON/INI/BV-07-C": [ ll_con_ini_bv_07_c, "Initiation Device Filtering: Directed" ],
    "LL/CON/INI/BV-08-C": [ ll_con_ini_bv_08_c, "Network Privacy Connection Establishment responding to connectable undirected advertising, Initiator" ],
    "LL/CON/INI/BV-09-C": [ ll_con_ini_bv_09_c, "Network Privacy - Connection Establishment using resolving list, Initiator" ],
    "LL/CON/INI/BV-10-C": [ ll_con_ini_bv_10_c, "Network Privacy - Connection Establishment using directed advertising and resolving list, Initiator" ],
    "LL/CON/INI/BV-11-C": [ ll_con_ini_bv_11_c, "Network Privacy - Connection Establishment using directed advertising with wrong address and resolving list, Initiator" ],
    "LL/CON/INI/BV-12-C": [ ll_con_ini_bv_12_c, "Network Privacy - Connection Establishment using directed advertising with identity address and resolving list, Initiator" ],
    "LL/CON/INI/BV-16-C": [ ll_con_ini_bv_16_c, "Connection Initiation, Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-17-C": [ ll_con_ini_bv_17_c, "Connecting to Directed Advertising, Channel Selection Algorithm #2" ],
    "LL/CON/INI/BV-18-C": [ ll_con_ini_bv_18_c, "Network Privacy - Connection Establishment using resolving list, Initiator, Ignore Identity Address" ],
    "LL/CON/INI/BV-19-C": [ ll_con_ini_bv_19_c, "Network Privacy - Connection Establishment using directed advertising and resolving list, Initiator, Ignore Identity Address" ],
    "LL/CON/INI/BV-20-C": [ ll_con_ini_bv_20_c, "Device Privacy - Connection Establishment using resolving list, Initiator, Accept Identity Address" ],
    "LL/CON/INI/BV-21-C": [ ll_con_ini_bv_21_c, "Device Privacy - Connection Establishment using directed advertising and resolving list, Initiator, Accept Identity Address" ],
    "LL/CON/MAS/BI-06-C": [ ll_con_mas_bi_06_c, "Accepting Parameter Connection Request - illegal parameters" ],
    "LL/CON/MAS/BV-03-C": [ ll_con_mas_bv_03_c, "Master Sending Data" ],
    "LL/CON/MAS/BV-04-C": [ ll_con_mas_bv_04_c, "Master Receiving Data" ],
    "LL/CON/MAS/BV-05-C": [ ll_con_mas_bv_05_c, "Master Sending and Receiving Data" ],
    "LL/CON/MAS/BV-07-C": [ ll_con_mas_bv_07_c, "Requesting Parameter Update" ],
    "LL/CON/MAS/BV-08-C": [ ll_con_mas_bv_08_c, "Master Sending Termination" ],
    "LL/CON/MAS/BV-09-C": [ ll_con_mas_bv_09_c, "Master Accepting Termination" ],
    "LL/CON/MAS/BV-13-C": [ ll_con_mas_bv_13_c, "Feature Setup Request" ],
    "LL/CON/MAS/BV-20-C": [ ll_con_mas_bv_20_c, "Master Request Version" ],
    "LL/CON/MAS/BV-21-C": [ ll_con_mas_bv_21_c, "Master Respond Version" ],
    "LL/CON/MAS/BV-23-C": [ ll_con_mas_bv_23_c, "Responding to Feature Exchange" ],
    "LL/CON/MAS/BV-24-C": [ ll_con_mas_bv_24_c, "Initiating Connection Parameter Request - Accept" ],
    "LL/CON/MAS/BV-25-C": [ ll_con_mas_bv_25_c, "Initiating Connection Parameter Request - Reject" ],
    "LL/CON/MAS/BV-26-C": [ ll_con_mas_bv_26_c, "Initiating Connection Parameter Request - same procedure collision" ],
    "LL/CON/MAS/BV-27-C": [ ll_con_mas_bv_27_c, "Initiating Connection Parameter Request - different procedure collision - channel map update" ],
    "LL/CON/MAS/BV-29-C": [ ll_con_mas_bv_29_c, "Initiating Connection Parameter Request - remote legacy host" ],
    "LL/CON/MAS/BV-30-C": [ ll_con_mas_bv_30_c, "Accepting Connection Parameter Request - no Preferred Periodicity" ],
    "LL/CON/MAS/BV-34-C": [ ll_con_mas_bv_34_c, "Accepting Connection Parameter Request - event masked" ],
    "LL/CON/MAS/BV-35-C": [ ll_con_mas_bv_35_c, "Accepting Connection Parameter Request - Host rejects" ],
    "LL/CON/MAS/BV-41-C": [ ll_con_mas_bv_41_c, "Initiating PHY Update Procedure" ],
    "LL/CON/MAS/BV-43-C": [ ll_con_mas_bv_43_c, "Responding to PHY Update Procedure" ],
    "LL/CON/MAS/BV-74-C": [ ll_con_mas_bv_74_c, "Master Data Length Update - Initiating Data Length Update Procedure, LE 1M PHY" ],
    "LL/CON/MAS/BV-77-C": [ ll_con_mas_bv_77_c, "Master Data Length Update - Initiating Data Length Update Procedure, LE 2M PHY" ],
    "LL/CON/SLA/BI-08-C": [ ll_con_sla_bi_08_c, "Accepting Connection Parameter Request Illegal Parameters" ],
    "LL/CON/SLA/BV-04-C": [ ll_con_sla_bv_04_c, "Slave Sending Data" ],
    "LL/CON/SLA/BV-05-C": [ ll_con_sla_bv_05_c, "Slave Receiving Data" ],
    "LL/CON/SLA/BV-06-C": [ ll_con_sla_bv_06_c, "Slave Sending and Receiving Data" ],
    "LL/CON/SLA/BV-10-C": [ ll_con_sla_bv_10_c, "Accepting Parameter Update" ],
    "LL/CON/SLA/BV-11-C": [ ll_con_sla_bv_11_c, "Slave sending termination" ],
    "LL/CON/SLA/BV-12-C": [ ll_con_sla_bv_12_c, "Slave accepting termination" ],
#   "LL/CON/SLA/BV-13-C": [ ll_con_sla_bv_13_c, "Slave supervision timer - FAILS" ],
    "LL/CON/SLA/BV-14-C": [ ll_con_sla_bv_14_c, "Feature Setup Response" ],
    "LL/CON/SLA/BV-19-C": [ ll_con_sla_bv_19_c, "Slave request version" ],
    "LL/CON/SLA/BV-20-C": [ ll_con_sla_bv_20_c, "Slave respond version" ],
    "LL/CON/SLA/BV-22-C": [ ll_con_sla_bv_22_c, "Initiate feature exchange" ],
    "LL/CON/SLA/BV-24-C": [ ll_con_sla_bv_24_c, "Initiating Connection Parameter Request - Accept" ],
    "LL/CON/SLA/BV-25-C": [ ll_con_sla_bv_25_c, "Initiating Connection Parameter Request - Reject" ],
    "LL/CON/SLA/BV-26-C": [ ll_con_sla_bv_26_c, "Initiating Connection Parameter Request - same procedure collision" ],
    "LL/CON/SLA/BV-27-C": [ ll_con_sla_bv_27_c, "Initiating Connection Parameter Request - different procedure collision - channel map update" ],
    "LL/CON/SLA/BV-29-C": [ ll_con_sla_bv_29_c, "Responding to Connection Parameter Request - no Preffered_Periodicity" ],
    "LL/CON/SLA/BV-33-C": [ ll_con_sla_bv_33_c, "Accepting Connection Parameter Request - event masked" ],
    "LL/CON/SLA/BV-34-C": [ ll_con_sla_bv_34_c, "Accepting Connection Parameter Request - host rejectssur" ],
    "LL/CON/SLA/BV-40-C": [ ll_con_sla_bv_40_c, "Initiating PHY Update Procedure" ],
    "LL/CON/SLA/BV-42-C": [ ll_con_sla_bv_42_c, "Responding to PHY Update Procedure" ],
    "LL/CON/SLA/BV-78-C": [ ll_con_sla_bv_78_c, "Slave Data Length Update - Initiating Data Length Update Procedure, LE 1M PHY" ],
    "LL/CON/SLA/BV-81-C": [ ll_con_sla_bv_81_c, "Slave Data Length Update - Initiating Data Length Update Procedure, LE 2M PHY" ],
    "LL/DDI/ADV/BV-01-C": [ ll_ddi_adv_bv_01_c, "Non-Connectable Advertising Events" ],
    "LL/DDI/ADV/BV-02-C": [ ll_ddi_adv_bv_02_c, "Undirected Advertising Events" ],
    "LL/DDI/ADV/BV-03-C": [ ll_ddi_adv_bv_03_c, "Advertising Data: Non-Connectable" ],
    "LL/DDI/ADV/BV-04-C": [ ll_ddi_adv_bv_04_c, "Advertising Data: Undirected" ],
    "LL/DDI/ADV/BV-05-C": [ ll_ddi_adv_bv_05_c, "Scan Request: Undirected Connectable" ],
    "LL/DDI/ADV/BV-06-C": [ ll_ddi_adv_bv_06_c, "Connection Request" ],
    "LL/DDI/ADV/BV-07-C": [ ll_ddi_adv_bv_07_c, "Scan Request Connection Request" ],
    "LL/DDI/ADV/BV-08-C": [ ll_ddi_adv_bv_08_c, "Scan Request Device Filtering" ],
    "LL/DDI/ADV/BV-09-C": [ ll_ddi_adv_bv_09_c, "Connection Request Device Filtering" ],
    "LL/DDI/ADV/BV-11-C": [ ll_ddi_adv_bv_11_c, "Directed Advertising Events" ],
    "LL/DDI/ADV/BV-15-C": [ ll_ddi_adv_bv_15_c, "Discoverable Advertising Events" ],
    "LL/DDI/ADV/BV-16-C": [ ll_ddi_adv_bv_16_c, "Advertising Data: Discoverable" ],
    "LL/DDI/ADV/BV-17-C": [ ll_ddi_adv_bv_17_c, "Scan Request: Discoverable" ],
    "LL/DDI/ADV/BV-18-C": [ ll_ddi_adv_bv_18_c, "Device Filtering: Discoverable" ],
    "LL/DDI/ADV/BV-19-C": [ ll_ddi_adv_bv_19_c, "Low Duty Cycle Directed Advertising Events" ],
    "LL/DDI/ADV/BV-20-C": [ ll_ddi_adv_bv_20_c, "Advertising Always Using the LE 1M PHY" ],
#   "LL/DDI/ADV/BV-21-C": [ ll_ddi_adv_bv_21_c, "Extended Advertising, Legacy PDUs, Non-Connectable - FAILS" ],
    "LL/DDI/SCN/BV-01-C": [ ll_ddi_scn_bv_01_c, "Passive Scanning: Non Connectable" ],
    "LL/DDI/SCN/BV-02-C": [ ll_ddi_scn_bv_02_c, "Passive Scanning Device Filtering" ],
    "LL/DDI/SCN/BV-03-C": [ ll_ddi_scn_bv_03_c, "Active Scanning" ],
    "LL/DDI/SCN/BV-04-C": [ ll_ddi_scn_bv_04_c, "Active Scanning Device Filtering" ],
    "LL/DDI/SCN/BV-05-C": [ ll_ddi_scn_bv_05_c, "Scanning For Advertiser Types" ],
    "LL/DDI/SCN/BV-10-C": [ ll_ddi_scn_bv_10_c, "Passive Scanning: Undirected Events" ],
    "LL/DDI/SCN/BV-11-C": [ ll_ddi_scn_bv_11_c, "Passive Scanning: Directed Events" ],
    "LL/DDI/SCN/BV-12-C": [ ll_ddi_scn_bv_12_c, "Passive Scanning: Discoverable Events" ],
    "LL/DDI/SCN/BV-13-C": [ ll_ddi_scn_bv_13_c, "Network Privacy Passive Scanning, Peer IRK" ],
    "LL/DDI/SCN/BV-14-C": [ ll_ddi_scn_bv_14_c, "Network Privacy - Passive Scanning: Directed Events to an address different from the scanner s address" ],
    "LL/DDI/SCN/BV-15-C": [ ll_ddi_scn_bv_15_c, "Network Privacy Active Scanning, no Local IRK, no Peer IRK" ],
    "LL/DDI/SCN/BV-16-C": [ ll_ddi_scn_bv_16_c, "Network Privacy Active Scanning, Local IRK, no Peer IRK" ],
    "LL/DDI/SCN/BV-17-C": [ ll_ddi_scn_bv_17_c, "Network Privacy Active Scanning, no Local IRK, Peer IRK" ],
    "LL/DDI/SCN/BV-18-C": [ ll_ddi_scn_bv_18_c, "Network Privacy Active Scanning, Local IRK, Peer IRK" ],
    "LL/DDI/SCN/BV-26-C": [ ll_ddi_scn_bv_26_c, "Network Privacy Passive Scanning, Peer IRK, Ignore Identity Address" ],
    "LL/DDI/SCN/BV-28-C": [ ll_ddi_scn_bv_28_c, "Device Privacy Passive Scanning, Peer IRK, Accept Identity Address" ],
#   "LL/SEC/ADV/BV-01-C": [ ll_sec_adv_bv_01_c, "Advertising with static address - FAILS" ],
    "LL/SEC/ADV/BV-02-C": [ ll_sec_adv_bv_02_c, "Privacy - Non Connectable Undirected Advertising, non-resolvable private address" ],
    "LL/SEC/ADV/BV-03-C": [ ll_sec_adv_bv_03_c, "Privacy - Non Connectable Undirected Advertising, Resolvable Private Address" ],
    "LL/SEC/ADV/BV-04-C": [ ll_sec_adv_bv_04_c, "Network Privacy - Scannable Advertising, non-resolvable private address" ],
    "LL/SEC/ADV/BV-05-C": [ ll_sec_adv_bv_05_c, "Network Privacy - Scannable Advertising, resolvable private address" ],
    "LL/SEC/ADV/BV-06-C": [ ll_sec_adv_bv_06_c, "Network Privacy - Undirected Connectable Advertising no Local IRK, no peer IRK" ],
    "LL/SEC/ADV/BV-07-C": [ ll_sec_adv_bv_07_c, "Network Privacy - Undirected Connectable Advertising with Local IRK, no peer IRK" ],
#   "LL/SEC/ADV/BV-08-C": [ ll_sec_adv_bv_08_c, "Network Privacy - Undirected Connectable Advertising with Local IRK, peer IRK - FAILS" ],
    "LL/SEC/ADV/BV-09-C": [ ll_sec_adv_bv_09_c, "Network Privacy - Undirected Connectable Advertising without Local IRK, peer IRK" ],
    "LL/SEC/ADV/BV-10-C": [ ll_sec_adv_bv_10_c, "Network Privace - Undirected Connectable Advertising using Resolving List and Peer Device Identity not in the List" ],
    "LL/SEC/ADV/BV-11-C": [ ll_sec_adv_bv_11_c, "Network Privacy - Directed Connectable Advertising using local and remote IRK" ],
    "LL/SEC/ADV/BV-12-C": [ ll_sec_adv_bv_12_c, "Network Privacy - Directed Connectable Advertising using local IRK, but not remote IRK" ],
#   "LL/SEC/ADV/BV-13-C": [ ll_sec_adv_bv_13_c, "Network Privacy - Directed Connectable Advertising without local IRK, but with remote IRK - FAILS" ],
#   "LL/SEC/ADV/BV-14-C": [ ll_sec_adv_bv_14_c, "Network Privacy - Directed Connectable Advertising without local IRK, but with remote IRK - FAILS" ],
    "LL/SEC/ADV/BV-15-C": [ ll_sec_adv_bv_15_c, "Network Privacy - Scannable Advertising, resolvable private address, Ignore Identity Address" ],
    "LL/SEC/ADV/BV-16-C": [ ll_sec_adv_bv_16_c, "Network Privacy - Undirected Connectable Advertising with Local IRK and Peer IRK, Ignore Identity Address" ],
#   "LL/SEC/ADV/BV-17-C": [ ll_sec_adv_bv_17_c, "Network Privacy - Directed Connectable Advertising using local and remote IRK, Ignore Identity Address - FAILS" ],
#   "LL/SEC/ADV/BV-18-C": [ ll_sec_adv_bv_18_c, "Device Privacy - Scannable Advertising, resolvable private address, Accept Identity Address -FAILS" ],
#   "LL/SEC/ADV/BV-19-C": [ ll_sec_adv_bv_19_c, "Device Privacy - Undirected Connectable Advertising with Local IRK and Peer IRK, Accept Identity Address- FAILS" ],
    "LL/SEC/ADV/BV-20-C": [ ll_sec_adv_bv_20_c, "Device Privacy - Directed Connectable Advertising using local and remote IRK, Accept Identity Address" ]
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
