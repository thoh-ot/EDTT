from components.basic_commands import le_read_buffer_size;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Buffer Size",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Buffer Size command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read buffer size test");
    
    try:
        for i in range(0, transport.n_devices):
            status, LeMaxLen, LeMaxNum = le_read_buffer_size(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Buffer Size test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Buffer Size test passed with %i device(s)" %transport.n_devices);
    return 0;
