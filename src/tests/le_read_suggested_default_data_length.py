from components.basic_commands import le_read_suggested_default_data_length;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Suggested Default Data Length",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Suggested Default Data Length command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read suggested default data length test");
    
    try:
        for i in range(0, transport.n_devices):
            status, MaxTxOctets, MaxTxTime = le_read_suggested_default_data_length(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Suggested Default Data Length test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Suggested Default Data Length test passed with %i device(s)" %transport.n_devices);
    return 0;
