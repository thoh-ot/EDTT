from components.basic_commands import le_read_channel_map;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Channel Map",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Channel Map command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read channel map test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle, ChMap = le_read_channel_map(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "LE Read Channel Map test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Channel Map test passed with %i device(s)" %transport.n_devices);
    return 0;
