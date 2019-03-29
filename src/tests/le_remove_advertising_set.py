from components.basic_commands import le_remove_advertising_set;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Remove Advertising Set",
                    number_devices = 1,
                    description = "Test that we can execute the LE Remove Advertising Set command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le remove advertising set test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_remove_advertising_set(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "LE Remove Advertising Set test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Remove Advertising Set test passed with %i device(s)" %transport.n_devices);
    return 0;
