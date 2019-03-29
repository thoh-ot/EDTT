from components.basic_commands import le_connection_update;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Connection Update",
                    number_devices = 1,
                    description = "Test that we can execute the LE Connection Update command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le connection update test");
    
    handle = 0;
    ConnIntervalMin = 0;
    ConnIntervalMax = 0;
    ConnLatency = 0;
    SupervisionTimeout = 0;
    MinCeLen = 0;
    MaxCeLen = 0;
    
    try:
        for i in range(0, transport.n_devices):
            le_connection_update(transport, i, handle, ConnIntervalMin, ConnIntervalMax, ConnLatency, SupervisionTimeout, MinCeLen, MaxCeLen, 100);
    except Exception as e:
        trace.trace(1, "LE Connection Update test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Connection Update test passed with %i device(s)" %transport.n_devices);
    return 0;
