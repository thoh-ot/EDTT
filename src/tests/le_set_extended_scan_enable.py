from components.basic_commands import le_set_extended_scan_enable;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Extended Scan Enable",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Extended Scan Enable command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set extended scan enable test");
    
    enable = 0;
    FilterDup = 0;
    duration = 0;
    period = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_extended_scan_enable(transport, i, enable, FilterDup, duration, period, 100);
    except Exception as e:
        trace.trace(1, "LE Set Extended Scan Enable test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Extended Scan Enable test passed with %i device(s)" %transport.n_devices);
    return 0;
