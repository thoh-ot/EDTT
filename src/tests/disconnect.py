from components.basic_commands import disconnect;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Disconnect",
                    number_devices = 1,
                    description = "Test that we can execute the Disconnect command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting disconnect test");
    
    handle = 0;
    reason = 0;
    
    try:
        for i in range(0, transport.n_devices):
            disconnect(transport, i, handle, reason, 100);
    except Exception as e:
        trace.trace(1, "Disconnect test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Disconnect test passed with %i device(s)" %transport.n_devices);
    return 0;
