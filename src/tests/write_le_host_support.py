from components.basic_commands import write_le_host_support;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Write LE Host Support",
                    number_devices = 1,
                    description = "Test that we can execute the Write LE Host Support command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting write le host support test");
    
    le = 0;
    simul = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = write_le_host_support(transport, i, le, simul, 100);
    except Exception as e:
        trace.trace(1, "Write LE Host Support test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Write LE Host Support test passed with %i device(s)" %transport.n_devices);
    return 0;
