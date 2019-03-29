from components.basic_commands import le_set_extended_advertising_data;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Extended Advertising Data",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Extended Advertising Data command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set extended advertising data test");
    
    handle = 0;
    op = 0;
    FragPref = 0;
    len = 0;
    data = [0 for i in range(251)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_extended_advertising_data(transport, i, handle, op, FragPref, len, data, 100);
    except Exception as e:
        trace.trace(1, "LE Set Extended Advertising Data test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Extended Advertising Data test passed with %i device(s)" %transport.n_devices);
    return 0;
