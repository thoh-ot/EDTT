from components.basic_commands import le_receiver_test;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Receiver Test",
                    number_devices = 1,
                    description = "Test that we can execute the LE Receiver Test command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le receiver test test");
    
    RxCh = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_receiver_test(transport, i, RxCh, 100);
    except Exception as e:
        trace.trace(1, "LE Receiver Test test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Receiver Test test passed with %i device(s)" %transport.n_devices);
    return 0;
