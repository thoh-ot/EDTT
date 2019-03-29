from components.basic_commands import le_transmitter_test;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Transmitter Test",
                    number_devices = 1,
                    description = "Test that we can execute the LE Transmitter Test command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le transmitter test test");
    
    TxCh = 0;
    TestDataLen = 0;
    PktPayload = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_transmitter_test(transport, i, TxCh, TestDataLen, PktPayload, 100);
    except Exception as e:
        trace.trace(1, "LE Transmitter Test test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Transmitter Test test passed with %i device(s)" %transport.n_devices);
    return 0;
