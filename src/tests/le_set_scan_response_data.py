from components.basic_commands import le_set_scan_response_data;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Scan Response Data",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Scan Response Data command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set scan response data test");
    
    len = 0;
    data = [0 for i in range(31)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_scan_response_data(transport, i, len, data, 100);
    except Exception as e:
        trace.trace(1, "LE Set Scan Response Data test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Scan Response Data test passed with %i device(s)" %transport.n_devices);
    return 0;
