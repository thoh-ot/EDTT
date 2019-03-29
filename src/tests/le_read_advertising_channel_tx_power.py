from components.basic_commands import le_read_advertising_channel_tx_power;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Advertising Channel TX Power",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Advertising Channel TX Power command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read advertising channel tx power test");
    
    try:
        for i in range(0, transport.n_devices):
            status, TxPowerLevel = le_read_advertising_channel_tx_power(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Advertising Channel TX Power test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Advertising Channel TX Power test passed with %i device(s)" %transport.n_devices);
    return 0;
