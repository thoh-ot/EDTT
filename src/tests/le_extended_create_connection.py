from components.basic_commands import le_extended_create_connection;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Extended Create Connection",
                    number_devices = 1,
                    description = "Test that we can execute the LE Extended Create Connection command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le extended create connection test");
    
    FilterPolicy = 0;
    OwnAddrType = 0;
    PeerAddrType = 0;
    AVal = [0 for i in range(6)];
    phys = 0;
    PInterval = [0 for i in range(0)];
    PWindow = [0 for i in range(0)];
    PConnIntervalMin = [0 for i in range(0)];
    PConnIntervalMax = [0 for i in range(0)];
    PConnLatency = [0 for i in range(0)];
    PSupervisionTimeout = [0 for i in range(0)];
    PMinCeLen = [0 for i in range(0)];
    PMaxCeLen = [0 for i in range(0)];
    
    try:
        for i in range(0, transport.n_devices):
            le_extended_create_connection(transport, i, FilterPolicy, OwnAddrType, PeerAddrType, AVal, phys, PInterval, PWindow, PConnIntervalMin, PConnIntervalMax, PConnLatency, PSupervisionTimeout, PMinCeLen, PMaxCeLen, 100);
    except Exception as e:
        trace.trace(1, "LE Extended Create Connection test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Extended Create Connection test passed with %i device(s)" %transport.n_devices);
    return 0;
