from components.basic_commands import read_buffer_size;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Buffer Size",
                    number_devices = 1,
                    description = "Test that we can execute the Read Buffer Size command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read buffer size test");
    
    try:
        for i in range(0, transport.n_devices):
            status, AclMaxLen, ScoMaxLen, AclMaxNum, ScoMaxNum = read_buffer_size(transport, i, 100);
    except Exception as e:
        trace.trace(1, "Read Buffer Size test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Buffer Size test passed with %i device(s)" %transport.n_devices);
    return 0;
