from components.basic_commands import le_read_number_of_supported_advertising_sets;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Number of Supported Advertising Sets",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Number of Supported Advertising Sets command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read number of supported advertising sets test");
    
    try:
        for i in range(0, transport.n_devices):
            status, NumSets = le_read_number_of_supported_advertising_sets(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Number of Supported Advertising Sets test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Number of Supported Advertising Sets test passed with %i device(s)" %transport.n_devices);
    return 0;
