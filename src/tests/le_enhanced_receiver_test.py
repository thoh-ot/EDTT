from components.basic_commands import le_enhanced_receiver_test;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Enhanced Receiver Test",
                    number_devices = 1,
                    description = "Test that we can execute the LE Enhanced Receiver Test command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le enhanced receiver test test");
    
    RxCh = 0;
    phy = 0;
    ModIndex = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_enhanced_receiver_test(transport, i, RxCh, phy, ModIndex, 100);
    except Exception as e:
        trace.trace(1, "LE Enhanced Receiver Test test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Enhanced Receiver Test test passed with %i device(s)" %transport.n_devices);
    return 0;
