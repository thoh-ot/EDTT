# -*- coding: utf-8 -*-
import random;
import os;
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

class Role(IntEnum):
    MASTER = 0
    SLAVE  = 1
    
def __check_command_complete_event(transport, idx, trace):
    eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
    showEvent(event, eventData, trace);
    return (event == Events.BT_HCI_EVT_CMD_COMPLETE);

"""
    HCI/GEV/BV-01-C [Unsupported Commands on each supported controller]
"""
def hci_gev_bv_01_c(transport, idx, trace):
    trace.trace(2, "HCI/GEV/BV-01-C [Unsupported Commands on each supported controller]");

    try:
        lap = toArray(0x9E8B00, 3)
        length = 1;
        NumRsp = 0;

        status = inquire(transport, idx, lap, length, NumRsp, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1);

        FlowEnable = 0;
        
        status = set_controller_to_host_flow_control(transport, idx, FlowEnable, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        AclMtu = ScoMtu = 23;
        AclPkts = ScoPkts = 6;

        status = host_buffer_size(transport, idx, AclMtu, ScoMtu, AclPkts, ScoPkts, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        NumHandles = 0;
        HHandle = [0 for i in range(NumHandles)];
        HCount = [0 for i in range(NumHandles)];

        status = host_number_of_completed_packets(transport, idx, NumHandles, HHandle, HCount, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = read_buffer_size(transport, idx, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        
        status = read_rssi(transport, idx, handle, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        le = 0;
        simul = 0;
        
        status = write_le_host_support(transport, idx, le, simul, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        props = 0;
        PrimMinInterval = [0 for _ in range(3)];
        PrimMaxInterval = [0 for _ in range(3)];
        PrimChannelMap = 0;
        OwnAddrType = 0;
        PeerAddrType = 0;
        AVal = [0 for _ in range(6)];
        FilterPolicy = 0;
        TxPower = 0;
        PrimAdvPhy = 0;
        SecAdvMaxSkip = 0;
        SecAdvPhy = 0;
        sid = 0;
        ScanReqNotifyEnable = 0;

        status = le_set_extended_advertising_parameters(transport, idx, handle, props, PrimMinInterval, PrimMaxInterval, PrimChannelMap, OwnAddrType, PeerAddrType, AVal, FilterPolicy, TxPower, PrimAdvPhy, SecAdvMaxSkip, SecAdvPhy, sid, ScanReqNotifyEnable, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        op = 0;
        FragPref = 0;
        dataLength = 0;
        data = [0 for _ in range(251)];

        status = le_set_extended_advertising_data(transport, idx, handle, op, FragPref, dataLength, data, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        op = 0;
        FragPref = 0;
        dataLength = 0;
        data = [0 for _ in range(251)];
        
        status = le_set_extended_scan_response_data(transport, idx, handle, op, FragPref, dataLength, data, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        enable = 0;
        SetNum = 0;
        SHandle = [0 for i in range(SetNum)];
        SDuration = [0 for i in range(SetNum)];
        SMaxExtAdvEvts = [0 for i in range(SetNum)];
    
        status = le_set_extended_advertising_enable(transport, idx, enable, SetNum, SHandle, SDuration, SMaxExtAdvEvts, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_read_maximum_advertising_data_length(transport, idx, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_read_number_of_supported_advertising_sets(transport, idx, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;

        status = le_remove_advertising_set(transport, idx, handle, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_clear_advertising_sets(transport, idx, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        MinInterval = 0;
        MaxInterval = 0;
        props = 0;
        
        status = le_set_periodic_advertising_parameters(transport, idx, handle, MinInterval, MaxInterval, props, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        op = 0;
        dataLength = 251;
        data = [0 for i in range(dataLength)];

        status = le_set_periodic_advertising_data(transport, idx, handle, op, dataLength, data, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        enable = 0;
        handle = 0;
    
        status = le_set_periodic_advertising_enable(transport, idx, enable, handle, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        OwnAddrType = 0;
        FilterPolicy = 0;
        phys = 0;
        PType = [0 for i in range(phys)];
        PInterval = [0 for i in range(phys)];
        PWindow = [0 for i in range(phys)];

        status = le_set_extended_scan_parameters(transport, idx, OwnAddrType, FilterPolicy, phys, PType, PInterval, PWindow, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        enable = 0;
        FilterDup = 0;
        duration = 0;
        period = 0;

        status = le_set_extended_scan_enable(transport, idx, enable, FilterDup, duration, period, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        FilterPolicy = 0;
        OwnAddrType = 0;
        PeerAddrType = 0;
        AVal = [0 for i in range(6)];
        phys = 0;
        PInterval = [0 for i in range(phys)];
        PWindow = [0 for i in range(phys)];
        PConnIntervalMin = [0 for i in range(phys)];
        PConnIntervalMax = [0 for i in range(phys)];
        PConnLatency = [0 for i in range(phys)];
        PSupervisionTimeout = [0 for i in range(phys)];
        PMinCeLen = [0 for i in range(phys)];
        PMaxCeLen = [0 for i in range(phys)];

        status = le_extended_create_connection(transport, idx, FilterPolicy, OwnAddrType, PeerAddrType, AVal, phys, PInterval, PWindow, PConnIntervalMin, PConnIntervalMax, PConnLatency, PSupervisionTimeout, PMinCeLen, PMaxCeLen, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        FilterPolicy = 0;
        sid = 0;
        AddrType = 0;
        AVal = [0 for i in range(6)];
        skip = 0;
        SyncTimeout = 0;
        unused = 0;

        status = le_periodic_advertising_create_sync(transport, idx, FilterPolicy, sid, AddrType, AVal, skip, SyncTimeout, unused, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_periodic_advertising_create_sync_cancel(transport, idx, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        handle = 0;
        
        status = le_periodic_advertising_terminate_sync(transport, idx, handle, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        AddrType = 0;
        AVal = [0 for i in range(6)];
        sid = 0;

        status = le_add_device_to_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        AddrType = 0;
        AVal = [0 for i in range(6)];
        sid = 0;

        status = le_remove_device_from_periodic_advertiser_list(transport, idx, AddrType, AVal, sid, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_clear_periodic_advertiser_list(transport, idx, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_read_periodic_advertiser_list_size(transport, idx, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;

        status = le_read_rf_path_compensation(transport, idx, 100)[0];
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;
        
        TxPathComp = 0;
        RxPathComp = 0;
        
        status = le_write_rf_path_compensation(transport, idx, TxPathComp, RxPathComp, 100);
        success = __check_command_complete_event(transport, idx, trace) and (status == 1) and success;
        
    except Exception as e: 
        trace.trace(3, "Unsupported Commands on each supported controller test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Unsupported Commands on each supported controller test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CFC/BV-02-C [Buffer Size]
"""
def hci_cfc_bv_02_c(transport, idx, trace):
    trace.trace(2, "HCI/CFC/BV-02-C [Buffer Size]");

    try:
        status, LeMaxLen, LeMaxNum = le_read_buffer_size(transport, idx, 100);
        trace.trace(6, "LE Read Buffer Size Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        if LeMaxLen == 0 and LeMaxNum == 0:
            status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = read_buffer_size(transport, idx, 100);
            trace.trace(6, "Read Buffer Size Command returns status: 0x%02X" % status);
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "Buffer Size Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Buffer Size Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CIN/BV-01-C [Read Local Supported Features Command]
"""
def hci_cin_bv_01_c(transport, idx, trace):
    trace.trace(2, "HCI/CIN/BV-01-C [Read Local Supported Features Command]");

    try:
        status, features = read_local_supported_features(transport, idx, 100);
        trace.trace(6, "Read Local Supported Features Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        if success:
            showFeatures(features, trace);
    except Exception as e: 
        trace.trace(3, "Read Local Supported Features Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Read Local Supported Features Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CIN/BV-03-C [Read Local Supported Commands Command]
"""
def hci_cin_bv_03_c(transport, idx, trace):
    trace.trace(2, "HCI/CIN/BV-03-C [Read Local Supported Commands Command]");

    try:
        status, commands = read_local_supported_commands(transport, idx, 100);
        trace.trace(6, "Read Local Supported Commands Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        if success:
            showCommands(commands, trace);
    except Exception as e: 
        trace.trace(3, "Read Local Supported Commands Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Read Local Supported Commands Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CIN/BV-04-C [Read Local Version Information Command]
"""
def hci_cin_bv_04_c(transport, idx, trace):
    trace.trace(2, "HCI/CIN/BV-04-C [Read Local Version Information Command]");

    try:
        status, HCIVersion, HCIRevision, LMPVersion, manufacturer, LMPSubversion = read_local_version_information(transport, idx, 100);
        trace.trace(6, "Read Local Version Information Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        if success:
            trace.trace(6, "HCI Version:    %i" % HCIVersion);
            trace.trace(6, "HCI Revision:   0x%04X" % HCIRevision);
            trace.trace(6, "LMP Version:    %i" % LMPVersion);
            trace.trace(6, "LMP Subversion: 0x%04X" % LMPSubversion);
            trace.trace(6, "Manufacturer:   0x%04X" % manufacturer);
    except Exception as e: 
        trace.trace(3, "Read Local Version Information Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Read Local Version Information Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CIN/BV-06-C [White List Size]
"""
def hci_cin_bv_06_c(transport, idx, trace):
    trace.trace(2, "HCI/CIN/BV-06-C [White List Size]");

    try:
        status = le_clear_white_list(transport, idx, 100);
        trace.trace(6, "LE Clear White List Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status, WlSize = le_read_white_list_size(transport, idx, 100);
        trace.trace(6, "LE Read White List Size Command returns status: 0x%02X list size: %i" % (status, WlSize));
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        for n in range(WlSize+1):
            AddrType = 0;
            AVal = [random.randint(0,255) for _ in range(6)];
            if n < WlSize:
                lastAVal = AVal
            status = le_add_device_to_white_list(transport, idx, AddrType, AVal, 100);
            trace.trace(6, "LE Add Device to White List Command returns status: 0x%02X" % status);
            success = success and ((status == 0) if n < WlSize else (status == 7));
            eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

        status = le_remove_device_from_white_list(transport, idx, AddrType, lastAVal, 100);    
        trace.trace(6, "LE Remove Device from White List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status = le_add_device_to_white_list(transport, idx, AddrType, lastAVal, 100);
        trace.trace(6, "LE Add Device to White List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "White List Size test failed: %s" % str(e));
        success = False;

    trace.trace(2, "White List Size test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CIN/BV-09-C [Read LE Public Key Validation Feature Bit]
"""
def hci_cin_bv_09_c(transport, idx, trace):
    trace.trace(2, "HCI/CIN/BV-09-C [Read LE Public Key Validation Feature Bit]");

    try:
        status, features = le_read_local_supported_features(transport, idx, 100);
        trace.trace(6, "LE Read Local Supported Features Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        showLEFeatures(features, trace);
    except Exception as e: 
        trace.trace(3, "Read LE Public Key Validation Feature Bit test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Read LE Public Key Validation Feature Bit test " + ("PASSED" if success else "FAILED"));
    return success;
    
"""
    HCI/CCO/BV-07-C [BR/EDR Not Supported]
"""
def hci_cco_bv_07_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-07-C [BR/EDR Not Supported]");

    try:
        status = inquire(transport, idx, toArray(0x9E8B00, 3), 1, 1, 100);
        trace.trace(6, "Inquire Command returns status: 0x%02X" % status);
        success = status == 1; # Unknown HCI Command (0x01)
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_STATUS or event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "BR/EDR Not Supported test failed: %s" % str(e));
        success = False;

    trace.trace(2, "BR/EDR Not Supported test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-09-C [LE Set Data Length]

    Note: Requires that CONFIG_BT_CTLR_DATA_LENGTH_MAX=60 is set in the prj.conf file for the ptt_app.
"""
def hci_cco_bv_09_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/CCO/BV-09-C [LE Set Data Length]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        success = advertiser.enable();

        connected = initiator.connect();
        success = success and connected;

        if connected:
            TxOctets = 60
            TxTime = 728
            status, handle = le_set_data_length(transport, upperTester, initiator.handles[0], TxOctets, TxTime, 100);
            trace.trace(6, "LE Set Data Length Command returns status: 0x%02X handle: 0x%04X" % (status, handle));
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);
            """
                If parameters have changed - both upper- and lower-Tester will receive a LE Data Length Change event
            """
            if has_event(transport, upperTester, 200):
                eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
                showEvent(event, eventData, trace);
        
            if has_event(transport, lowerTester, 200):
                eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
                success = success and (event == Events.BT_HCI_EVT_LE_META_EVENT) and (subEvent == MetaEvents.BT_HCI_EVT_LE_DATA_LEN_CHANGE);
                showEvent(event, eventData, trace);
            """
                Note: Disconnect can generate another LE Data Length Change event...
            """
            success = success and initiator.disconnect(0x3E);

        else:
            advertiser.disable();

    except Exception as e: 
        trace.trace(3, "LE Set Data Length test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Set Data Length test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-10-C [LE Read Suggested Default Data Length Command]
"""
def hci_cco_bv_10_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-10-C [LE Read Suggested Default Data Length Command]");

    try:
        status, maxTxOctets, maxTxTime = le_read_suggested_default_data_length(transport, idx, 100);
        trace.trace(6, "LE Read Suggested Default Data Length Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctets, maxTxOctets));
        trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTime, maxTxTime));
    except Exception as e: 
        trace.trace(3, "LE Read Suggested Default Data Length Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Suggested Default Data Length Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-11-C [LE Write Suggested Default Data Length Command]
"""
def hci_cco_bv_11_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-11-C [LE Write Suggested Default Data Length Command]");

    try:
        maxTxOctetsIn = (0x001B + 0x00FB)/2; maxTxTimeIn = (0x0148 + 0x4290)/2;
        status = le_write_suggested_default_data_length(transport, idx, maxTxOctetsIn, maxTxTimeIn, 100);
        trace.trace(6, "LE Write Suggested Default Data Length Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctetsIn, maxTxOctetsIn));
        trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTimeIn, maxTxTimeIn));

        status, maxTxOctetsOut, maxTxTimeOut = le_read_suggested_default_data_length(transport, idx, 100);
        trace.trace(6, "LE Read Suggested Default Data Length Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "Maximum number of transmitted payload octets: 0x%04X (%d)" % (maxTxOctetsOut, maxTxOctetsOut));
        trace.trace(6, "Maximum packet transmission time: 0x%04X (%d) microseconds" % (maxTxTimeOut, maxTxTimeOut));

        success = success and (maxTxOctetsOut == maxTxOctetsIn) and (maxTxTimeOut == maxTxTimeIn);
    except Exception as e: 
        trace.trace(3, "LE Write Suggested Default Data Length Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Write Suggested Default Data Length Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-12-C [LE Remove Device From Resolving List Command]
"""
def hci_cco_bv_12_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-12-C [LE Remove Device From Resolving List Command]");

    try:
        peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABCL);
        status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
        trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status = le_remove_device_from_resolving_list(transport, idx, peerAddress.type, peerAddress.address, 100);
        trace.trace(6, "LE Remove Device from Resolving List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "LE Remove Device From Resolving List Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Remove Device From Resolving List Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-13-C [LE Clear Resolving List Command]
"""
def hci_cco_bv_13_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-13-C [LE Clear Resolving List Command]");

    try:
        peerAddress = Address(SimpleAddressType.PUBLIC, 0x456789ABCDEFL);
        status = le_add_device_to_resolving_list(transport, idx, peerAddress.type, peerAddress.address, lowerIRK, upperIRK, 100);
        trace.trace(6, "LE Add Device to Resolving List Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status = le_clear_resolving_list(transport, idx, 100);
        trace.trace(6, "LE Clear Resolving List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "LE Clear Resolving List Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Clear Resolving List Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-14-C [LE Read Resolving List Size Command]
"""
def hci_cco_bv_14_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-14-C [LE Read Resolving List Size Command]");

    try:
        status, listSize = le_read_resolving_list_size(transport, idx, 100);
        trace.trace(6, "LE Read Resolving List Size Command returns status: 0x%02X" % status);
        success = (status == 0) and (listSize > 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "Resolving List Size returned: %d" % listSize);
    except Exception as e: 
        trace.trace(3, "LE Read Resolving List Size Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Resolving List Size Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-15-C [LE Set Default PHY Command]
"""
def hci_cco_bv_15_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-15-C [LE Set Default PHY Command]");

    try:
        status = le_set_default_phy(transport, idx, 3, 0, 0, 100);
        trace.trace(6, "LE Set Default PHY Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "LE Set Default PHY Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Set Default PHY Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-16-C [LE Read Periodic Advertiser List Size Command]
"""
def hci_cco_bv_16_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-16-C [LE Read Periodic Advertiser List Size Command]");

    try:
        status, listSize = le_read_periodic_advertiser_list_size(transport, idx, 100);
        trace.trace(6, "LE Read Periodic Advertiser List Size Command returns status: 0x%02X" % status);
        success = (status == 0) and (listSize > 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "Periodic Advertiser List Size returned: %d" % listSize);
    except Exception as e: 
        trace.trace(3, "LE Read Periodic Advertiser List Size Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Periodic Advertiser List Size Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-17-C [LE Add/Remove/Clear Periodic Advertiser List Commands]
"""
def hci_cco_bv_17_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-17-C [LE Add/Remove/Clear Periodic Advertiser List Commands]");

    try:
        status = le_clear_periodic_advertiser_list(transport, idx, 100);
        trace.trace(6, "LE Clear Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        peerAddress = Address(SimpleAddressType.PUBLIC, 0x123456789ABCL);
        status = le_add_device_to_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
        trace.trace(6, "LE Add Device to Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status = le_remove_device_from_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
        trace.trace(6, "LE Remove Device from Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        
        status = le_remove_device_from_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
        trace.trace(6, "LE Remove Device from Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = success and (status == 0x42);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        
        status = le_add_device_to_periodic_advertiser_list(transport, idx, peerAddress.type, peerAddress.address, 1, 100);
        trace.trace(6, "LE Add Device to Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        status = le_clear_periodic_advertiser_list(transport, idx, 100);
        trace.trace(6, "LE Clear Periodic Advertiser List Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
    except Exception as e: 
        trace.trace(3, "LE Add/Remove/Clear Periodic Advertiser List Commands test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Add/Remove/Clear Periodic Advertiser List Commands test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CCO/BV-18-C [LE Read Transmit Power Command]
"""
def hci_cco_bv_18_c(transport, idx, trace):
    trace.trace(2, "HCI/CCO/BV-18-C [LE Read Transmit Power Command]");

    try:
        status, minTxPower, maxTxPower = le_read_transmit_power(transport, idx, 100);
        trace.trace(6, "LE Read Transmit Power Command returns status: 0x%02X" % status);
        success = (status == 0) and (-127 <= minTxPower) and (minTxPower <= 126) and (-127 <= maxTxPower) and (maxTxPower <= 126) and (minTxPower <= maxTxPower);
        eventTime, event, subEvent, eventData = get_event(transport, idx, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        trace.trace(6, "LE Read Transmit Power Command returned range: [%d, %d] dBm." % (minTxPower, maxTxPower));
    except Exception as e: 
        trace.trace(3, "LE Read Transmit Power Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Transmit Power Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DDI/BV-03-C [Set Advertising Enable]
"""
def hci_ddi_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DDI/BV-03-C [Set Advertising Enable]");

    try:
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( SimpleAddressType.PUBLIC );
        scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 5 );

        success = success and advertiser.disable();
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyReports( 1 );
        
    except Exception as e: 
        trace.trace(3, "Set Advertising Enable test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Set Advertising Enable test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DDI/BV-04-C [Set Scan Enable]
"""
def hci_ddi_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DDI/BV-04-C [Set Scan Enable]");

    try:
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( SimpleAddressType.PUBLIC );
        scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 5 );

        scanner.monitor();
        success = success and not scanner.qualifyReports( 1 );

        success = success and advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Set Scan Enable test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Set Scan Enable test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DDI/BI-02-C [Reject Invalid Advertising Parameters]
"""
def hci_ddi_bi_02_c(transport, upperTester, trace):
    trace.trace(2, "HCI/DDI/BI-02-C [Reject Invalid Advertising Parameters]");

    try:
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.NON_CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];

        advertiser.minInterval = 32-2;
        advertiser.maxInterval = 32-1;
        
        successA = not advertiser.enable();
        successA = successA and (advertiser.status == 0x12);

        if not successA:
            advertiser.disable();

        advertiser.minInterval = 32+1;
        advertiser.maxInterval = 32;
        
        successB = not advertiser.enable();
        successB = successB and (advertiser.status == 0x11);

        success = successA and successB;
        
    except Exception as e: 
        trace.trace(3, "Reject Invalid Advertising Parameters test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reject Invalid Advertising Parameters test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/HFC/BV-04-C [LE Set Event Mask]
"""
def hci_hfc_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/HFC/BV-04-C [LE Set Event Mask]");

    try:
        """ Bit:   5  4  4  3  2  1  0  0
                   6  8  0  2  4  6  8  0
                0x20 00 00 00 00 00 80 10 ~ Bits 4, 15, 61 (Disconnection Complete Event, Hardware Error Event, LE Meta Event)
        """
        events = [0x10, 0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x20];
        
        status = set_event_mask(transport, upperTester, events, 100);
        trace.trace(6, "Set Event Mask Command returns status: 0x%02X" % status);
        success = status == 0;
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        """ Bit:  5  4  4  3  2  1  0  0
                  6  8  0  2  4  6  8  0
               0x00 00 00 00 00 07 FF FD ~ All except 'LE Channel Selection Algorithm Event and LE Advertising Report Event'                  
        """
        events = [0xFD, 0xFF, 0x07, 0x00, 0x00, 0x00, 0x00, 0x00];
        
        status = le_set_event_mask(transport, upperTester, events, 100);
        trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        """
        status = le_set_event_mask(transport, lowerTester, events, 100);
        trace.trace(6, "LE Set Event Mask Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        """
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( SimpleAddressType.PUBLIC );
        scanner = Scanner(transport, upperTester, trace, ScanType.ACTIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5, 5);
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyResponses( 5 );
        success = success and not scanner.qualifyReports( 5 );
        
        transport.wait(100);
        
        success = success and initiator.connect();

        transport.wait(500);
        
        if success:
            success = success and initiator.disconnect(0x3E);

    except Exception as e: 
        trace.trace(3, "LE Set Event Mask test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Set Event Mask test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CM/BV-01-C [LE Read Peer Resolvable Address Command]
"""
def hci_cm_bv_01_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/CM/BV-01-C [LE Read Peer Resolvable Address Command]");

    try:
        """
            Add Public address of lowerTester and upperTester to the Resolving List
        """
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

        for iutRole in [ Role.MASTER, Role.SLAVE ]:
            ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL if iutRole is Role.MASTER else 0x123456789ABCL);
            peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL if iutRole is Role.MASTER else 0x456789ABCDEFL);
            if iutRole == Role.MASTER:        
                advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
            else:
                advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
            advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
            initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
            if iutRole == Role.MASTER:        
                initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
            else:
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
            success = success and advertiser.enable();

            connected = success and initiator.connect();
            success = success and connected;

            peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );        
            status, RPA = le_read_peer_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
            trace.trace(6, "LE Read Peer Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

            if iutRole == Role.MASTER:        
                success = success and (initiator.peerRPA() == RPA);
            else:
                success = success and (initiator.localRPA() == RPA);
        
            transport.wait(200);
        
            if connected:
                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

    except Exception as e: 
        trace.trace(3, "LE Read Peer Resolvable Address Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Peer Resolvable Address Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CM/BV-02-C [LE Read Local Resolvable Address Command]
"""
def hci_cm_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/CM/BV-02-C [LE Read Local Resolvable Address Command]");

    try:
        """
            Add Public address of lowerTester and upperTester to the Resolving List
        """
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

        for iutRole in [ Role.MASTER, Role.SLAVE ]:
            ownAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC, 0x456789ABCDEFL if iutRole is Role.MASTER else 0x123456789ABCL);
            peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL if iutRole is Role.MASTER else 0x456789ABCDEFL);
            if iutRole == Role.MASTER:        
                advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
            else:
                advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_LDC_DIRECTED, ownAddress, peerAddress);
            advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        
            initiatorAddress = Address( ExtendedAddressType.RESOLVABLE_OR_PUBLIC );
            if iutRole == Role.MASTER:        
                initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
            else:
                initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( IdentityAddressType.PUBLIC_IDENTITY, toNumber(ownAddress.address) ));
            success = success and advertiser.enable();

            connected = success and initiator.connect();
            success = success and connected;

            peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );        
            status, RPA = le_read_local_resolvable_address(transport, upperTester, peerAddress.type, peerAddress.address, 100);
            trace.trace(6, "LE Read Local Resolvable Address Command returns status: 0x%02X RPA: %s" % (status, formatAddress(RPA)));
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

            if iutRole == Role.MASTER:        
                success = success and (initiator.localRPA() == RPA);
            else:
                success = success and (initiator.peerRPA() == RPA);
        
            transport.wait(200);
        
            if connected:
                connected = not initiator.disconnect(0x3E);
                success = success and not connected;

    except Exception as e: 
        trace.trace(3, "LE Read Local Resolvable Address Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read Local Resolvable Address Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/CM/BV-03-C [LE Read PHY Command]
"""
def hci_cm_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/CM/BV-03-C [LE Read PHY Command]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        success = advertiser.enable();

        success = success and initiator.connect();

        if success:
            status, handle, TxPhy, RxPhy = le_read_phy(transport, upperTester, initiator.handles[0], 100);
            trace.trace(6, "LE Read PHY Command returns status: 0x%02X handle: 0x%04X TxPHY: %d RxPHY: %d" % (status, handle, TxPhy, RxPhy));
            success = success and (status == 0);
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
            showEvent(event, eventData, trace);

        if success:
            success = success and initiator.disconnect(0x3E);

    except Exception as e: 
        trace.trace(3, "LE Read PHY Command test failed: %s" % str(e));
        success = False;

    trace.trace(2, "LE Read PHY Command test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DSU/BV-02-C [Reset in Advertising State]
"""
def hci_dsu_bv_02_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DSU/BV-02-C [Reset in Advertising State]");

    try:
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( SimpleAddressType.PUBLIC );
        scanner = Scanner(transport, lowerTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 5 );

        status = reset(transport, upperTester, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        """
            Verify that the IUT has stopped Advertising
        """
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyReports( 5 );
        
    except Exception as e: 
        trace.trace(3, "Reset in Advertising State test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reset in Advertising State test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DSU/BV-03-C [Reset to Slave]
"""
def hci_dsu_bv_03_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DSU/BV-03-C [Reset to Slave]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x456789ABCDEFL );
        advertiser = Advertiser(transport, upperTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, lowerTester, upperTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x123456789ABCL ));
        success = advertiser.enable();

        success = success and initiator.connect();

        transport.wait(200);
        
        status = reset(transport, upperTester, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        """
           There might be pending disconnect events lying around...
        """
        while has_event(transport, lowerTester, 200):
            eventTime, event, subEvent, eventData = get_event(transport, lowerTester, 100);
            showEvent(event, eventData, trace);
            if event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
                status, handle, reason = disconnectComplete(eventData);
                success = success and (reason == 0x08); # Connection Timeout

        while has_event(transport, upperTester, 200):
            eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
            showEvent(event, eventData, trace);
            if event == Events.BT_HCI_EVT_DISCONN_COMPLETE:
                status, handle, reason = disconnectComplete(eventData);
                success = success and (reason == 0x08); # Connection Timeout
        
    except Exception as e: 
        trace.trace(3, "Reset to Slave test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reset to Slave test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DSU/BV-04-C [Reset in Scanning State]
"""
def hci_dsu_bv_04_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DSU/BV-04-C [Reset in Scanning State]");

    try:
        ownAddress = Address( SimpleAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        ownAddress = Address( SimpleAddressType.PUBLIC );
        scanner = Scanner(transport, upperTester, trace, ScanType.PASSIVE, AdvertisingReport.ADV_IND, ownAddress, ScanningFilterPolicy.FILTER_NONE, 5);

        success = advertiser.enable();

        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and scanner.qualifyReports( 5 );

        status = reset(transport, upperTester, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        """
            Verify that the IUT has stopped Advertising
        """
        success = success and scanner.enable();
        scanner.monitor();
        success = success and scanner.disable();
        success = success and not scanner.qualifyReports( 5 );
        
    except Exception as e: 
        trace.trace(3, "Reset in Scanning State test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reset in Scanning State test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DSU/BV-05-C [Reset in Initiating State]
"""
def hci_dsu_bv_05_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DSU/BV-05-C [Reset in Initiating State]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));

        success = initiator.preConnect();

        status = reset(transport, upperTester, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);

        success = success and advertiser.enable();

        success = success and not initiator.postConnect();

        success = success and advertiser.disable();

    except Exception as e: 
        trace.trace(3, "Reset in Initiating State test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reset in Initiating State test " + ("PASSED" if success else "FAILED"));
    return success;

"""
    HCI/DSU/BV-06-C [Reset to Master]
"""
def hci_dsu_bv_06_c(transport, upperTester, lowerTester, trace):
    trace.trace(2, "HCI/DSU/BV-06-C [Reset to Master]");

    try:
        ownAddress = Address( ExtendedAddressType.PUBLIC );
        peerAddress = Address( SimpleAddressType.PUBLIC, 0x123456789ABCL );
        advertiser = Advertiser(transport, lowerTester, trace, AdvertiseChannel.ALL_CHANNELS, Advertising.CONNECTABLE_UNDIRECTED, ownAddress, peerAddress, AdvertisingFilterPolicy.FILTER_NONE);
        advertiser.responseData = [ 0x04, 0x09 ] + [ ord(char) for char in "IUT" ];
        initiatorAddress = Address( ExtendedAddressType.PUBLIC );
        initiator = Initiator(transport, upperTester, lowerTester, trace, initiatorAddress, Address( ExtendedAddressType.PUBLIC, 0x456789ABCDEFL ));
        success = advertiser.enable();

        success = success and initiator.connect();

        transport.wait(200);
        
        status = reset(transport, upperTester, 100);
        trace.trace(6, "Reset Command returns status: 0x%02X" % status);
        success = success and (status == 0);
        eventTime, event, subEvent, eventData = get_event(transport, upperTester, 100);
        success = success and (event == Events.BT_HCI_EVT_CMD_COMPLETE);
        showEvent(event, eventData, trace);
        
    except Exception as e: 
        trace.trace(3, "Reset to Master test failed: %s" % str(e));
        success = False;

    trace.trace(2, "Reset to Master test " + ("PASSED" if success else "FAILED"));
    return success;

_spec = {};
_spec["HCI/CCO/BV-07-C"] = \
    TestSpec(name = "HCI/CCO/BV-07-C", number_devices = 2,
             description = "[BR/EDRNotSupported]",
             test_private = hci_cco_bv_07_c);
_spec["HCI/CCO/BV-09-C"] = \
    TestSpec(name = "HCI/CCO/BV-09-C", number_devices = 2,
             description = "[LESetDataLength]",
             test_private = hci_cco_bv_09_c);
_spec["HCI/CCO/BV-10-C"] = \
    TestSpec(name = "HCI/CCO/BV-10-C", number_devices = 2,
             description = "[LEReadSuggestedDefaultDataLengthCommand]",
             test_private = hci_cco_bv_10_c);
_spec["HCI/CCO/BV-11-C"] = \
    TestSpec(name = "HCI/CCO/BV-11-C", number_devices = 2,
             description = "[LEWriteSuggestedDefaultDataLengthCommand]",
             test_private = hci_cco_bv_11_c);
_spec["HCI/CCO/BV-12-C"] = \
    TestSpec(name = "HCI/CCO/BV-12-C", number_devices = 2,
             description = "[LERemoveDeviceFromResolvingListCommand]",
             test_private = hci_cco_bv_12_c);
_spec["HCI/CCO/BV-13-C"] = \
    TestSpec(name = "HCI/CCO/BV-13-C", number_devices = 2,
             description = "[LEClearResolvingListCommand]",
             test_private = hci_cco_bv_13_c);
_spec["HCI/CCO/BV-14-C"] = \
    TestSpec(name = "HCI/CCO/BV-14-C", number_devices = 2,
             description = "[LEReadResolvingListSizeCommand]",
             test_private = hci_cco_bv_14_c);
_spec["HCI/CCO/BV-15-C"] = \
    TestSpec(name = "HCI/CCO/BV-15-C", number_devices = 2,
             description = "[LESetDefaultPHYCommand]",
             test_private = hci_cco_bv_15_c);
#_spec["HCI/CCO/BV-16-C"] = \
#    TestSpec(name = "HCI/CCO/BV-16-C", number_devices = 2,
#             description = "[LEReadPeriodicAdvertiserListSizeCommand]",
#             test_private = hci_cco_bv_16_c);
#_spec["HCI/CCO/BV-17-C"] = \
#    TestSpec(name = "HCI/CCO/BV-17-C", number_devices = 2,
#             description = "[LEAdd/Remove/ClearPeriodicAdvertiserListCommands]",
#             test_private = hci_cco_bv_17_c);
_spec["HCI/CCO/BV-18-C"] = \
    TestSpec(name = "HCI/CCO/BV-18-C", number_devices = 2,
             description = "[LEReadTransmitPowerCommand]",
             test_private = hci_cco_bv_18_c);
_spec["HCI/CFC/BV-02-C"] = \
    TestSpec(name = "HCI/CFC/BV-02-C", number_devices = 2,
             description = "[BufferSize]",
             test_private = hci_cfc_bv_02_c);
_spec["HCI/CIN/BV-01-C"] = \
    TestSpec(name = "HCI/CIN/BV-01-C", number_devices = 2,
             description = "[ReadLocalSupportedFeaturesCommand]",
             test_private = hci_cin_bv_01_c);
_spec["HCI/CIN/BV-03-C"] = \
    TestSpec(name = "HCI/CIN/BV-03-C", number_devices = 2,
             description = "[ReadLocalSupportedCommandsCommand]",
             test_private = hci_cin_bv_03_c);
_spec["HCI/CIN/BV-04-C"] = \
    TestSpec(name = "HCI/CIN/BV-04-C", number_devices = 2,
             description = "[ReadLocalVersionInformationCommand]",
             test_private = hci_cin_bv_04_c);
_spec["HCI/CIN/BV-06-C"] = \
    TestSpec(name = "HCI/CIN/BV-06-C", number_devices = 2,
             description = "[WhiteListSize]",
             test_private = hci_cin_bv_06_c);
_spec["HCI/CIN/BV-09-C"] = \
    TestSpec(name = "HCI/CIN/BV-09-C", number_devices = 2,
             description = "[ReadLEPublicKeyValidationFeatureBit]",
             test_private = hci_cin_bv_09_c);
_spec["HCI/CM/BV-01-C"] = \
    TestSpec(name = "HCI/CM/BV-01-C", number_devices = 2,
             description = "[LEReadPeerResolvableAddressCommand]",
             test_private = hci_cm_bv_01_c);
_spec["HCI/CM/BV-02-C"] = \
    TestSpec(name = "HCI/CM/BV-02-C", number_devices = 2,
             description = "[LEReadLocalResolvableAddressCommand]",
             test_private = hci_cm_bv_02_c);
_spec["HCI/CM/BV-03-C"] = \
    TestSpec(name = "HCI/CM/BV-03-C", number_devices = 2,
             description = "[LEReadPHYCommand]",
             test_private = hci_cm_bv_03_c);
_spec["HCI/DDI/BI-02-C"] = \
    TestSpec(name = "HCI/DDI/BI-02-C", number_devices = 2,
             description = "[RejectInvalidAdvertisingParameters]",
             test_private = hci_ddi_bi_02_c);
_spec["HCI/DDI/BV-03-C"] = \
    TestSpec(name = "HCI/DDI/BV-03-C", number_devices = 2,
             description = "[SetAdvertisingEnable]",
             test_private = hci_ddi_bv_03_c);
_spec["HCI/DDI/BV-04-C"] = \
    TestSpec(name = "HCI/DDI/BV-04-C", number_devices = 2,
             description = "[SetScanEnable]",
             test_private = hci_ddi_bv_04_c);
_spec["HCI/DSU/BV-02-C"] = \
    TestSpec(name = "HCI/DSU/BV-02-C", number_devices = 2,
             description = "[ResetinAdvertisingState]",
             test_private = hci_dsu_bv_02_c);
_spec["HCI/DSU/BV-03-C"] = \
    TestSpec(name = "HCI/DSU/BV-03-C", number_devices = 2,
             description = "[ResettoSlave]",
             test_private = hci_dsu_bv_03_c);
_spec["HCI/DSU/BV-04-C"] = \
    TestSpec(name = "HCI/DSU/BV-04-C", number_devices = 2,
             description = "[ResetinScanningState]",
             test_private = hci_dsu_bv_04_c);
_spec["HCI/DSU/BV-05-C"] = \
    TestSpec(name = "HCI/DSU/BV-05-C", number_devices = 2,
             description = "[ResetinInitiatingState]",
             test_private = hci_dsu_bv_05_c);
_spec["HCI/DSU/BV-06-C"] = \
    TestSpec(name = "HCI/DSU/BV-06-C", number_devices = 2,
             description = "[ResettoMaster]",
             test_private = hci_dsu_bv_06_c);
_spec["HCI/GEV/BV-01-C"] = \
    TestSpec(name = "HCI/GEV/BV-01-C", number_devices = 2,
             description = "[UnsupportedCommandsoneachsupportedcontroller]",
             test_private = hci_gev_bv_01_c);
_spec["HCI/HFC/BV-04-C"] = \
    TestSpec(name = "HCI/HFC/BV-04-C", number_devices = 2,
             description = "[LESetEventMask]",
             test_private = hci_hfc_bv_04_c);

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
    success = preamble(transport, trace);
    test_f = test_spec.test_private;
    if test_f.__code__.co_argcount > 3:
        success = success and test_f(transport, 0, 1, trace);
    else:        
        success = success and test_f(transport, 0, trace);
    return not success
