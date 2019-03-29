from components.basic_commands import read_rssi;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read RSSI",
                    number_devices = 1,
                    description = "Test that we can execute the Read RSSI command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read rssi test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle, rssi = read_rssi(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "Read RSSI test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read RSSI test passed with %i device(s)" %transport.n_devices);
    return 0;
