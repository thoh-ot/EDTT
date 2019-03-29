from components.basic_commands import le_set_scan_parameters;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Scan Parameters",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Scan Parameters command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set scan parameters test");
    
    ScanType = 0;
    interval = 0;
    window = 0;
    AddrType = 0;
    FilterPolicy = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_scan_parameters(transport, i, ScanType, interval, window, AddrType, FilterPolicy, 100);
    except Exception as e:
        trace.trace(1, "LE Set Scan Parameters test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Scan Parameters test passed with %i device(s)" %transport.n_devices);
    return 0;
