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
from components.pairing import *;

global lowerIRK, upperIRK, lowerRandomAddress, upperRandomAddress;

"""
    GAP/DISC/NONM/BV-01-C [Non-discoverable Mode Non-connectable Mode]
"""
def gap_disc_nonm_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/NONM/BV-01-C [Non-discoverable Mode Non-connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Non-discoverable Mode Non-connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Non-discoverable Mode Non-connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/NONM/BV-02-C [Non-discoverable Mode Undirected Connectable Mode]
"""
def gap_disc_nonm_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/NONM/BV-02-C [Non-discoverable Mode Undirected Connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Non-discoverable Mode Undirected Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Non-discoverable Mode Undirected Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMM/BV-01-C [Limited Discoverable Mode Non-connectable Mode BR/EDR/LE]
"""
def gap_disc_limm_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMM/BV-01-C [Limited Discoverable Mode Non-connectable Mode BR/EDR/LE]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discoverable Mode Non-connectable Mode BR/EDR/LE test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discoverable Mode Non-connectable Mode BR/EDR/LE test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMM/BV-02-C [Limited Discoverable Mode Undirected Connectable Mode BR/EDR/LE]
"""
def gap_disc_limm_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMM/BV-02-C [Limited Discoverable Mode Undirected Connectable Mode BR/EDR/LE]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discoverable Mode Undirected Connectable Mode BR/EDR/LE test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discoverable Mode Undirected Connectable Mode BR/EDR/LE test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMM/BV-03-C [Limited Discoverable Mode Non-connectable Mode LE Only]
"""
def gap_disc_limm_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMM/BV-03-C [Limited Discoverable Mode Non-connectable Mode LE Only]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discoverable Mode Non-connectable Mode LE Only test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discoverable Mode Non-connectable Mode LE Only test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMM/BV-04-C [Limited Discoverable Mode Undirected Connectable Mode LE Only]
"""
def gap_disc_limm_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMM/BV-04-C [Limited Discoverable Mode Undirected Connectable Mode LE Only]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discoverable Mode Undirected Connectable Mode LE Only test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discoverable Mode Undirected Connectable Mode LE Only test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENM/BV-01-C [General Discoverable Mode Non-connectable Mode BR/EDR/LE]
"""
def gap_disc_genm_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENM/BV-01-C [General Discoverable Mode Non-connectable Mode BR/EDR/LE]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE);
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discoverable Mode Non-connectable Mode BR/EDR/LE test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discoverable Mode Non-connectable Mode BR/EDR/LE test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENM/BV-02-C [General Discoverable Mode Undirected Connectable Mode BR/EDR/LE]
"""
def gap_disc_genm_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENM/BV-02-C [General Discoverable Mode Undirected Connectable Mode BR/EDR/LE]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discoverable Mode Undirected Connectable Mode BR/EDR/LE test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discoverable Mode Undirected Connectable Mode BR/EDR/LE test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENM/BV-03-C [General Discoverable Mode Non-connectable Mode LE Only]
"""
def gap_disc_genm_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENM/BV-03-C [General Discoverable Mode Non-connectable Mode LE Only]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discoverable Mode Non-connectable Mode LE Only test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discoverable Mode Non-connectable Mode LE Only test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENM/BV-04-C [General Discoverable Mode Undirected Connectable Mode LE Only]
"""
def gap_disc_genm_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENM/BV-04-C [General Discoverable Mode Undirected Connectable Mode LE Only]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));

                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discoverable Mode Undirected Connectable Mode LE Only test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discoverable Mode Undirected Connectable Mode LE Only test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMP/BV-01-C [Limited Discovery Procedure Find Limited Discoverable Device]
"""
def gap_disc_limp_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMP/BV-01-C [Limited Discovery Procedure Find Limited Discoverable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);

        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discovery Procedure Find Limited Discoverable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discovery Procedure Find Limited Discoverable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMP/BV-02-C [Limited Discovery Procedure Does not find General Discoverable Device]
"""
def gap_disc_limp_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMP/BV-02-C [Limited Discovery Procedure Does not find General Discoverable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
    
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discovery Procedure Does not find General Discoverable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discovery Procedure Does not find General Discoverable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMP/BV-04-C [Limited Discovery Procedure Does not find Undirected Connectable Device]
"""
def gap_disc_limp_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMP/BV-04-C [Limited Discovery Procedure Does not find Undirected Connectable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
    
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discovery Procedure Does not find Undirected Connectable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discovery Procedure Does not find Undirected Connectable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/LIMP/BV-05-C [Limited Discovery Procedure Does not find Directed Connectable Device]
"""
def gap_disc_limp_bv_05_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/LIMP/BV-05-C [Limited Discovery Procedure Does not find Directed Connectable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
    
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "Limited Discovery Procedure Does not find Directed Connectable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Limited Discovery Procedure Does not find Directed Connectable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENP/BV-01-C [General Discovery Procedure Finding General Discoverable Device]
"""
def gap_disc_genp_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENP/BV-01-C [General Discovery Procedure Finding General Discoverable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discovery Procedure Finding General Discoverable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discovery Procedure Finding General Discoverable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENP/BV-02-C [General Discovery Procedure Finding Limited Discoverable Device]
"""
def gap_disc_genp_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENP/BV-01-C [General Discovery Procedure Finding Limited Discoverable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discovery Procedure Finding Limited Discoverable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discovery Procedure Finding Limited Discoverable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENP/BV-04-C [General Discovery Procedure Does not find Undirected Connectable Device]
"""
def gap_disc_genp_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENP/BV-04-C [General Discovery Procedure Does not find Undirected Connectable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData  = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discovery Procedure Does not find Undirected Connectable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discovery Procedure Does not find Undirected Connectable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/GENP/BV-05-C [General Discovery Procedure Does not find Directed Connectable Device]
"""
def gap_disc_genp_bv_05_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/GENP/BV-05-C [General Discovery Procedure Does not find Directed Connectable Device]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
            success = not success;
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "General Discovery Procedure Does not find Directed Connectable Device test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Discovery Procedure Does not find Directed Connectable Device test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/DISC/RPA/BV-01-C [Discovery Procedure Find Discoverable Device using Resolvable Private Address]
"""
def gap_disc_rpa_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/DISC/RPA/BV-01-C [Discovery Procedure Find Discoverable Device using Resolvable Private Address]");

    try:
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
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        
        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );
            trace.trace(6, "Received %d advertising reports; %d scan responses" % (scanner.reports, scanner.responses));
                
        success = success and advertiser.disable();
        success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    except Exception as e: 
        trace.trace(3, "Discovery Procedure Find Discoverable Device using Resolvable Private Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Discovery Procedure Find Discoverable Device using Resolvable Private Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/NCON/BV-01-C [Non-Connectable Mode]
"""
def gap_conn_ncon_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/NCON/BV-01-C [Non-Connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x123456789ABCL ));

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );
        """
            Attempt to initiate connection with Advertiser
        """
        success = advertiser.enable();
        connected = initiator.connect();
        success = success and not connected;
        success = success and advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Non-Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Non-Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/NCON/BV-02-C [Non-Connectable Mode General Discoverable Mode]
"""
def gap_conn_ncon_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/NCON/BV-02-C [Non-Connectable Mode General Discoverable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and not connected;
        
        success = success and advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Non-Connectable Mode General Discoverable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Non-Connectable Mode General Discoverable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/NCON/BV-03-C [Non-Connectable Mode Limited Discoverable Mode]
"""
def gap_conn_ncon_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/NCON/BV-03-C [Non-Connectable Mode Limited Discoverable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

        success = advertiser.enable();
        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and not connected;
        
        success = success and advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Non-Connectable Mode Limited Discoverable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Non-Connectable Mode Limited Discoverable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/DCON/BV-01-C [Directed Connectable Mode]
"""
def gap_conn_dcon_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/DCON/BV-01-C [Directed Connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_DIRECT_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        success = advertising = advertiser.enable();

        if success: 
            success, devices = scanner.discover( 2000 );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and connected;
                advertising = not connected;

                if connected:
                    connected = not initiator.disconnect(0x3E);
                    success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Directed Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Directed Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/UCON/BV-01-C [Undirected Connectable Mode Non-Discoverable Mode]
"""
def gap_conn_ucon_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/UCON/BV-01-C [Undirected Connectable Mode Non-Discoverable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

        success = advertising = advertiser.enable();

        if success: 
            success, devices = scanner.discover( 2000 );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and connected;
                advertising = not connected;

                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Undirected Connectable Mode Non-Discoverable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Undirected Connectable Mode Non-Discoverable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/UCON/BV-02-C [Undirected Connectable Mode General Discoverable Mode]
"""
def gap_conn_ucon_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/UCON/BV-02-C [Undirected Connectable Mode General Discoverable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

        success = advertising = advertiser.enable();

        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and connected;
                advertising = not connected;

                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Undirected Connectable Mode General Discoverable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Undirected Connectable Mode General Discoverable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/UCON/BV-03-C [Undirected Connectable Mode Limited Discoverable Mode]
"""
def gap_conn_ucon_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/UCON/BV-03-C [Undirected Connectable Mode Limited Discoverable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1 );

        adData = ADData();
        advertiser.advertiseData  = adData.encode( ADType.FLAGS, ADFlag.LE_LIMITED_DISCOVERABLE | ADFlag.BR_EDR_NOT_SUPPORTED );
        advertiser.advertiseData += adData.encode( ADType.TX_POWER_LEVEL, -4 );
        advertiser.advertiseData += adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData   = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Flødebolle' );

        success = advertising = advertiser.enable();

        if success: 
            success, devices = scanner.discover( 2000, ADFlag.LE_GENERAL_DISCOVERABLE | ADFlag.LE_LIMITED_DISCOVERABLE );
            for address in devices:
                trace.trace(6, "Found device with address: %s complete local name: %s" % (formatAddress( toArray( address, 6 ), devices[address]["type"] ), devices[address]["name"]) );

            if success:
                address = next(iter(devices));
                """
                    Attempt to initiate connection with Advertiser
                """
                initiator = Initiator(transport, lowerTester, upperTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( devices[address]["type"], address ));
                connected = initiator.connect();
                success = success and connected;
                advertising = not connected;

                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Undirected Connectable Mode Limited Discoverable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Undirected Connectable Mode Limited Discoverable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/ACEP/BV-01-C [Auto Connection Establishment Procedure Directed Connectable Mode]
"""
def gap_conn_acep_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/ACEP/BV-01-C [Auto Connection Establishment Procedure Directed Connectable Mode]");

    try:
        """
            Place Public address of lowerTester in the White List for the Scanner
        """
        addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
        success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

        advertising = advertiser.enable();
	success = success and advertising;

        if success:
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Auto Connection Establishment Procedure Directed Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Auto Connection Establishment Procedure Directed Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/ACEP/BV-03-C [Auto Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_conn_acep_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/ACEP/BV-03-C [Auto Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]");

    try:
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
            Place Public address of lowerTester in the White List for the Scanner
        """
        addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
        success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

        advertising = advertiser.enable();
	success = success and advertising;

        if success:
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

        success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    except Exception as e: 
        trace.trace(3, "Auto Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Auto Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/ACEP/BV-04-C [Auto Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_conn_acep_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/ACEP/BV-04-C [Auto Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]");

    try:
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
            Place Public address of lowerTester in the White List for the Scanner
        """
        addresses = [[ SimpleAddressType.PUBLIC, 0x456789ABCDEFL ]];
        success = preamble_specific_white_listed(transport, upperTester, addresses, trace);

        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ), InitiatorFilterPolicy.FILTER_WHITE_LIST_ONLY);

        advertising = advertiser.enable();
	success = success and advertising;

        if success:
            connected = initiator.connect();
            success = success and connected;
            advertising = not connected;

            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

        success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    except Exception as e: 
        trace.trace(3, "Auto Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Auto Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/GCEP/BV-01-C [General Connection Establishment Procedure Directed Connectable Mode]
"""
def gap_conn_gcep_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/GCEP/BV-01-C [General Connection Establishment Procedure Directed Connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
        success = advertising = advertiser.enable();
	connected = initiator.connect()
        success = success and connected;
        advertising = not connected;

        if connected: 
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "General Connection Establishment Procedure Directed Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Connection Establishment Procedure Directed Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/GCEP/BV-02-C [General Connection Establishment Procedure Undirected Connectable Mode]
"""
def gap_conn_gcep_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/GCEP/BV-02-C [General Connection Establishment Procedure Undirected Connectable Mode]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
        success = advertising = advertiser.enable();
	connected = initiator.connect()
        success = success and connected;
        advertising = not connected;

        if connected: 
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "General Connection Establishment Procedure Undirected Connectable Mode test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Connection Establishment Procedure Undirected Connectable Mode test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/GCEP/BV-05-C [General Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
"""
def gap_conn_gcep_bv_05_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/GCEP/BV-05-C [General Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]");

    try:
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

        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
        success = advertising = advertiser.enable();
	connected = initiator.connect()
        success = success and connected;
        advertising = not connected;

        if connected: 
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

        success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    except Exception as e: 
        trace.trace(3, "General Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/GCEP/BV-06-C [General Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]
"""
def gap_conn_gcep_bv_06_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/GCEP/BV-06-C [General Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]");

    try:
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

        ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        initiator = Initiator(transport, upperTester, lowerTester, trace, Address( ExtendedAddressType.PUBLIC ), Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL ));
 
        success = advertising = advertiser.enable();
	connected = initiator.connect()
        success = success and connected;
        advertising = not connected;

        if connected: 
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

        success = success and RPAs[upperTester].disable() and RPAs[lowerTester].disable();

    except Exception as e: 
        trace.trace(3, "General Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "General Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-01-C [AD Type - Service UUID]
"""
def gap_adv_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-01-C [AD Type - Service UUID]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.ILIST_UUIDS_16, 0x1234, 0x5678, 0x9ABC );
        advertiser.responseData = adData.encode( ADType.ILIST_UUIDS_16, 0x9ABC, 0x5678, 0x1234 );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();

        advertiser.advertiseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
        advertiser.responseData = adData.encode( ADType.ILIST_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Service UUID test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Service UUID test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-02-C [AD Type - Local Name]
"""
def gap_adv_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-02-C [AD Type - Local Name]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.SHORTENED_LOCAL_NAME, u'Blåbær' );
        advertiser.responseData = adData.encode( ADType.COMPLETE_LOCAL_NAME, u'Rødgrød med fløde' );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Local Name test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Local Name test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-03-C [AD Type - Flags]
"""
def gap_adv_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-03-C [AD Type - Flags]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.FLAGS, 0x06 );
        advertiser.responseData = adData.encode( ADType.FLAGS, 0x1F );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Flags test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Flags test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-04-C [AD Type - Manufacturer Specific Data]
"""
def gap_adv_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-04-C [AD Type - Manufacturer Specific Data]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.MANUFACTURER_DATA, 0x0107, 0x00, 0x01, 0x02, 0x03, 0x04, 0x05 ); # Manufacturer Oticon
        advertiser.responseData = adData.encode( ADType.MANUFACTURER_DATA, 0x0107, 0x05, 0x04, 0x03, 0x02, 0x01, 0x00 ); # Manufacturer Oticon
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Manufacturer Specific Data test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Manufacturer Specific Data test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-05-C [AD Type - TX Power Level]
"""
def gap_adv_bv_05_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-05-C [AD Type - TX Power Level]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.TX_POWER_LEVEL, -20 );
        advertiser.responseData = adData.encode( ADType.TX_POWER_LEVEL, -40 );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - TX Power Level test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - TX Power Level test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-08-C [AD Type - Slave Connection Interval Range]
"""
def gap_adv_bv_08_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-08-C [AD Type - Slave Connection Interval Range]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.SLAVE_CONNECT_INT, 20, 40 );
        advertiser.responseData = adData.encode( ADType.SLAVE_CONNECT_INT, 10, 50 );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Slave Connection Interval Range test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Slave Connection Interval Range test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-09-C [AD Type - Service  Solicitation]
"""
def gap_adv_bv_09_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-09-C [AD Type - Service  Solicitation]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.SS_UUIDS_16, 0x1234, 0x5678, 0x9ABC );
        advertiser.responseData = adData.encode( ADType.SS_UUIDS_128, 0x1429304977D74244AE6AD3873E4A3184L );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Service  Solicitation test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Service  Solicitation test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-10-C [AD Type - Service Data]
"""
def gap_adv_bv_10_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-10-C [AD Type - Service Data]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.SERVICE_DATA_16, 0x1234, 0x01, 0x02, 0x03 );
        advertiser.responseData = adData.encode( ADType.SERVICE_DATA_128, 0x1429304977D74244AE6AD3873E4A3184L, 0x04, 0x05, 0x06 );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Service Data test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Service Data test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-11-C [AD Type - Apperance]
"""
def gap_adv_bv_11_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-11-C [AD Type - Apperance]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.APPEARANCE, 640 );  # Media Player
        advertiser.responseData = adData.encode( ADType.APPEARANCE, 832 );   # Heart rate Sensor
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Apperance test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Apperance test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-12-C [AD Type - Public Target Address]
"""
def gap_adv_bv_12_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-12-C [AD Type - Public Target Address]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x456789ABCDEFL, 0x123456789ABCL );
        advertiser.responseData = adData.encode( ADType.PUBLIC_ADDRESS, 0x123456789ABCL, 0x456789ABCDEFL );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Public Target Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Public Target Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-13-C [AD Type - Random Target Address]
"""
def gap_adv_bv_13_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-13-C [AD Type - Random Target Address]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.RANDOM_ADDRESS, 0x456789ABCDEFL, 0x123456789ABCL );
        advertiser.responseData = adData.encode( ADType.RANDOM_ADDRESS, 0x123456789ABCL, 0x456789ABCDEFL );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Random Target Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Random Target Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-14-C [AD Type - Advertising Interval]
"""
def gap_adv_bv_14_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-14-C [AD Type - Advertising Interval]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.ADVERTISE_INT, 20 );
        advertiser.responseData = adData.encode( ADType.ADVERTISE_INT, 10 );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - Advertising Interval test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - Advertising Interval test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-15-C [AD Type - LE Bluetooth Device Address]
"""
def gap_adv_bv_15_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-15-C [AD Type - LE Bluetooth Device Address]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABCL, 0 ); # Public Device Address
        advertiser.responseData = adData.encode( ADType.DEVICE_ADDRESS, 0x123456789ABCL, 1 );  # Random Device Address
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - LE Bluetooth Device Address test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - LE Bluetooth Device Address test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-16-C [AD Type - LE Role]
"""
def gap_adv_bv_16_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-16-C [AD Type - LE Role]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.DEVICE_ROLE, ADRole.CENTRAL_PREFERRED );
        advertiser.responseData = adData.encode( ADType.DEVICE_ROLE, ADRole.PERIPHERAL_PREFERRED );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - LE Role test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - LE Role test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/ADV/BV-17-C [AD Type - URI]
"""
def gap_adv_bv_17_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/ADV/BV-17-C [AD Type - URI]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        scanner = Scanner(transport, lowerTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 1, 1);

	adData = ADData();
        advertiser.advertiseData = adData.encode( ADType.URI, u'http://www.bluetooth.org' );
        advertiser.responseData = adData.encode( ADType.URI, u'example://z.com/Ålborg' );
        
        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 1 );
        success = success and scanner.qualifyResponses( 1, advertiser.responseData );
                
        success = success and advertiser.disable();
    except Exception as e: 
        trace.trace(3, "AD Type - URI test failed: %s" % str(e));
        success = False;

    trace.trace(2, "AD Type - URI test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    GAP/CONN/ENC [Testing encryption]
"""
def gap_conn_enc(transport, upperTester, lowerTester, trace):
    trace.trace(2, "GAP/CONN/ENC [Testing encryption]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        ownAddress = Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL );
        peerAddress = Address( IdentityAddressType.PUBLIC, 0x456789ABCDEFL );
        initiator = Initiator(transport, upperTester, lowerTester, trace, ownAddress, peerAddress);
 
        success = advertising = advertiser.enable();
	connected = initiator.connect()
        success = success and connected;
        advertising = not connected;

        pairing = Pairing(transport, trace, initiator, toNumber(upperIRK), toNumber(lowerIRK));
        success = pairing.pair();
        if success:
            trace.trace(6, "Link encrypted using LE Legacy Pairing...");
            success = pairing.pause();
            if success:
                trace.trace(6, "Link re-encrytpted using LE Legacy Pairing...");
            else:
                trace.trace(6, "Failed to re-encrypt link using LE Legacy Pairing!");
        else:
            trace.trace(6, "Failed to encrypt link using LE Legacy Pairing!");

        if connected: 
            connected = not initiator.disconnect(0x3E);
            success = success and not connected;

        if advertising:             
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Testing encryption test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Testing encryption test " + ("PASSED" if success else "FAILED"));
    return success;

__tests__ = { 
    "GAP/DISC/NONM/BV-01-C": gap_disc_nonm_bv_01_c, # [Non-discoverable Mode Non-connectable Mode]
    "GAP/DISC/NONM/BV-02-C": gap_disc_nonm_bv_02_c, # [Non-discoverable Mode Undirected Connectable Mode]
    "GAP/DISC/LIMM/BV-01-C": gap_disc_limm_bv_01_c, # [Limited Discoverable Mode Non-connectable Mode BR/EDR/LE]
    "GAP/DISC/LIMM/BV-02-C": gap_disc_limm_bv_02_c, # [Limited Discoverable Mode Undirected Connectable Mode BR/EDR/LE]
    "GAP/DISC/LIMM/BV-03-C": gap_disc_limm_bv_03_c, # [Limited Discoverable Mode Non-connectable Mode LE Only]
    "GAP/DISC/LIMM/BV-04-C": gap_disc_limm_bv_04_c, # [Limited Discoverable Mode Undirected Connectable Mode LE Only]
    "GAP/DISC/GENM/BV-01-C": gap_disc_genm_bv_01_c, # [General Discoverable Mode Non-connectable Mode BR/EDR/LE]
    "GAP/DISC/GENM/BV-02-C": gap_disc_genm_bv_02_c, # [General Discoverable Mode Undirected Connectable Mode BR/EDR/LE]
    "GAP/DISC/GENM/BV-03-C": gap_disc_genm_bv_03_c, # [General Discoverable Mode Non-connectable Mode LE Only]
    "GAP/DISC/GENM/BV-04-C": gap_disc_genm_bv_04_c, # [General Discoverable Mode Undirected Connectable Mode LE Only]
    "GAP/DISC/LIMP/BV-01-C": gap_disc_limp_bv_01_c, # [Limited Discovery Procedure Find Limited Discoverable Device]
    "GAP/DISC/LIMP/BV-02-C": gap_disc_limp_bv_02_c, # [Limited Discovery Procedure Does not find General Discoverable Device]
    "GAP/DISC/LIMP/BV-04-C": gap_disc_limp_bv_04_c, # [Limited Discovery Procedure Does not find Undirected Connectable Device]
    "GAP/DISC/LIMP/BV-05-C": gap_disc_limp_bv_05_c, # [Limited Discovery Procedure Does not find Directed Connectable Device]
    "GAP/DISC/GENP/BV-01-C": gap_disc_genp_bv_01_c, # [General Discovery Procedure Finding General Discoverable Device]
    "GAP/DISC/GENP/BV-02-C": gap_disc_genp_bv_02_c, # [General Discovery Procedure Finding Limited Discoverable Device]
    "GAP/DISC/GENP/BV-04-C": gap_disc_genp_bv_04_c, # [General Discovery Procedure Does not find Undirected Connectable Device]
    "GAP/DISC/GENP/BV-05-C": gap_disc_genp_bv_05_c, # [General Discovery Procedure Does not find Directed Connectable Device]
    "GAP/DISC/RPA/BV-01-C":  gap_disc_rpa_bv_01_c,  # [Discovery Procedure Find Discoverable Device using Resolvable Private Address]
    "GAP/CONN/NCON/BV-01-C": gap_conn_ncon_bv_01_c, # [Non-Connectable Mode]
    "GAP/CONN/NCON/BV-02-C": gap_conn_ncon_bv_02_c, # [Non-Connectable Mode General Discoverable Mode]
    "GAP/CONN/NCON/BV-03-C": gap_conn_ncon_bv_03_c, # [Non-Connectable Mode Limited Discoverable Mode]
    "GAP/CONN/DCON/BV-01-C": gap_conn_dcon_bv_01_c, # [Directed Connectable Mode]
    "GAP/CONN/UCON/BV-01-C": gap_conn_ucon_bv_01_c, # [Undirected Connectable Mode Non-Discoverable Mode]
    "GAP/CONN/UCON/BV-02-C": gap_conn_ucon_bv_02_c, # [Undirected Connectable Mode General Discoverable Mode]
    "GAP/CONN/UCON/BV-03-C": gap_conn_ucon_bv_03_c, # [Undirected Connectable Mode Limited Discoverable Mode]
    "GAP/CONN/ACEP/BV-01-C": gap_conn_acep_bv_01_c, # [Auto Connection Establishment Procedure Directed Connectable Mode]
    "GAP/CONN/ACEP/BV-03-C": gap_conn_acep_bv_03_c, # [Auto Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
    "GAP/CONN/ACEP/BV-04-C": gap_conn_acep_bv_04_c, # [Auto Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]
    "GAP/CONN/GCEP/BV-01-C": gap_conn_gcep_bv_01_c, # [General Connection Establishment Procedure Directed Connectable Mode]
    "GAP/CONN/GCEP/BV-02-C": gap_conn_gcep_bv_02_c, # [General Connection Establishment Procedure Undirected Connectable Mode]
    "GAP/CONN/GCEP/BV-05-C": gap_conn_gcep_bv_05_c, # [General Connection Establishment Procedure Directed Connectable Mode, Resolvable Private Address, Central Address Resolution]
    "GAP/CONN/GCEP/BV-06-C": gap_conn_gcep_bv_06_c, # [General Connection Establishment Procedure Undirected Connectable Mode, Resolvable Private Address]
    "GAP/ADV/BV-01-C":       gap_adv_bv_01_c,       # [AD Type - Service UUID]
    "GAP/ADV/BV-02-C":       gap_adv_bv_02_c,       # [AD Type - Local Name]
    "GAP/ADV/BV-03-C":       gap_adv_bv_03_c,       # [AD Type - Flags]
    "GAP/ADV/BV-04-C":       gap_adv_bv_04_c,       # [AD Type - Manufacturer Specific Data]
    "GAP/ADV/BV-05-C":       gap_adv_bv_05_c,       # [AD Type - TX Power Level]
    "GAP/ADV/BV-08-C":       gap_adv_bv_08_c,       # [AD Type - Slave Connection Interval Range]
    "GAP/ADV/BV-09-C":       gap_adv_bv_09_c,       # [AD Type - Service  Solicitation]
    "GAP/ADV/BV-10-C":       gap_adv_bv_10_c,       # [AD Type - Service Data]
    "GAP/ADV/BV-11-C":       gap_adv_bv_11_c,       # [AD Type - Apperance]
    "GAP/ADV/BV-12-C":       gap_adv_bv_12_c,       # [AD Type - Public Target Address]
    "GAP/ADV/BV-13-C":       gap_adv_bv_13_c,       # [AD Type - Random Target Address]
    "GAP/ADV/BV-14-C":       gap_adv_bv_14_c,       # [AD Type - Advertising Interval]
    "GAP/ADV/BV-15-C":       gap_adv_bv_15_c,       # [AD Type - LE Bluetooth Device Address]
    "GAP/ADV/BV-16-C":       gap_adv_bv_16_c,       # [AD Type - LE Role]
    "GAP/ADV/BV-17-C":       gap_adv_bv_17_c,       # [AD Type - URI]
    "GAP/CONN/ENC":          gap_conn_enc           # [Testing encryption]
};

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
    
def runTest(test, transport, trace):
    global __tests__;
    
    passed = failed = 0;

    if test.lower() == "all":
        for test in __tests__:
            success = preamble(transport, trace);
            trace.trace(4, "");
            success = success and __tests__[test](transport, 0, 1, trace);

            passed += 1 if success else 0;
            failed += 0 if success else 1;

            trace.trace(4, "");

    elif test in __tests__:
        success = preamble(transport, trace);
        success = success and __tests__[test](transport, 0, 1, trace);
        
        passed += 1 if success else 0;
        failed += 0 if success else 1;

    elif os.path.isfile(test):
        file = open(test, "r");
        for line in file:
            test = line.strip().upper();
            if test in __tests__:
                success = preamble(transport, trace);
                trace.trace(4, "");
                success = success and __tests__[test](transport, 0, 1, trace);

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
                    number_devices = 2,
                    description = "Qualification of GAP.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    success = runTest("all" if args.case is None else args.case, transport, trace);
    return 0 if success else -1;
