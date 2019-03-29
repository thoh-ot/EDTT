from components.basic_commands import le_set_extended_scan_parameters;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Extended Scan Parameters",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Extended Scan Parameters command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set extended scan parameters test");
    
    OwnAddrType = 0;
    FilterPolicy = 0;
    phys = 0;
    PType = [0 for i in range(0)];
    PInterval = [0 for i in range(0)];
    PWindow = [0 for i in range(0)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_extended_scan_parameters(transport, i, OwnAddrType, FilterPolicy, phys, PType, PInterval, PWindow, 100);
    except Exception as e:
        trace.trace(1, "LE Set Extended Scan Parameters test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Extended Scan Parameters test passed with %i device(s)" %transport.n_devices);
    return 0;
