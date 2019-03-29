from components.basic_commands import le_set_resolvable_private_address_timeout;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Resolvable Private Address Timeout",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Resolvable Private Address Timeout command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set resolvable private address timeout test");
    
    RpaTimeout = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_resolvable_private_address_timeout(transport, i, RpaTimeout, 100);
    except Exception as e:
        trace.trace(1, "LE Set Resolvable Private Address Timeout test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Resolvable Private Address Timeout test passed with %i device(s)" %transport.n_devices);
    return 0;
