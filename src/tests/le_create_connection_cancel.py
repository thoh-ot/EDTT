from components.basic_commands import le_create_connection_cancel;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Create Connection Cancel",
                    number_devices = 1,
                    description = "Test that we can execute the LE Create Connection Cancel command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le create connection cancel test");
    
    try:
        for i in range(0, transport.n_devices):
            status = le_create_connection_cancel(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Create Connection Cancel test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Create Connection Cancel test passed with %i device(s)" %transport.n_devices);
    return 0;
