from components.basic_commands import le_set_data_length;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Data Length",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Data Length command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set data length test");
    
    handle = 0;
    TxOctets = 0;
    TxTime = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_data_length(transport, i, handle, TxOctets, TxTime, 100);
    except Exception as e:
        trace.trace(1, "LE Set Data Length test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Data Length test passed with %i device(s)" %transport.n_devices);
    return 0;
