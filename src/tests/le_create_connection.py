from components.basic_commands import le_create_connection;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Create Connection",
                    number_devices = 1,
                    description = "Test that we can execute the LE Create Connection command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le create connection test");
    
    ScanInterval = 0;
    ScanWindow = 0;
    FilterPolicy = 0;
    PeerAddrType = 0;
    AVal = [0 for i in range(6)];
    OwnAddrType = 0;
    ConnIntervalMin = 0;
    ConnIntervalMax = 0;
    ConnLatency = 0;
    SupervisionTimeout = 0;
    MinCeLen = 0;
    MaxCeLen = 0;
    
    try:
        for i in range(0, transport.n_devices):
            le_create_connection(transport, i, ScanInterval, ScanWindow, FilterPolicy, PeerAddrType, AVal, OwnAddrType, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen, 100);
    except Exception as e:
        trace.trace(1, "LE Create Connection test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Create Connection test passed with %i device(s)" %transport.n_devices);
    return 0;
