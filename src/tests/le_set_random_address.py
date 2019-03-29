from components.basic_commands import le_set_random_address;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Random Address",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Random Address command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set random address test");
    
    BdaddrVal = [0 for i in range(6)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_random_address(transport, i, BdaddrVal, 100);
    except Exception as e:
        trace.trace(1, "LE Set Random Address test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Random Address test passed with %i device(s)" %transport.n_devices);
    return 0;
