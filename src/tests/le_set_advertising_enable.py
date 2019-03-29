from components.basic_commands import le_set_advertising_enable;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Advertising Enable",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Advertising Enable command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set advertising enable test");
    
    enable = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_advertising_enable(transport, i, enable, 100);
    except Exception as e:
        trace.trace(1, "LE Set Advertising Enable test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Advertising Enable test passed with %i device(s)" %transport.n_devices);
    return 0;
