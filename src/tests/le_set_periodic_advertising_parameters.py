from components.basic_commands import le_set_periodic_advertising_parameters;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Periodic Advertising Parameters",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Periodic Advertising Parameters command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set periodic advertising parameters test");
    
    handle = 0;
    MinInterval = 0;
    MaxInterval = 0;
    props = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_periodic_advertising_parameters(transport, i, handle, MinInterval, MaxInterval, props, 100);
    except Exception as e:
        trace.trace(1, "LE Set Periodic Advertising Parameters test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Periodic Advertising Parameters test passed with %i device(s)" %transport.n_devices);
    return 0;
