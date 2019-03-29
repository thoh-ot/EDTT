from components.basic_commands import le_test_end;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Test End",
                    number_devices = 1,
                    description = "Test that we can execute the LE Test End command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le test end test");
    
    try:
        for i in range(0, transport.n_devices):
            status, RxPktCount = le_test_end(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Test End test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Test End test passed with %i device(s)" %transport.n_devices);
    return 0;
