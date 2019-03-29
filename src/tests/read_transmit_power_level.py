from components.basic_commands import read_transmit_power_level;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Transmit Power Level",
                    number_devices = 1,
                    description = "Test that we can execute the Read Transmit Power Level command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read transmit power level test");
    
    handle = 0;
    type = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle, TxPowerLevel = read_transmit_power_level(transport, i, handle, type, 100);
    except Exception as e:
        trace.trace(1, "Read Transmit Power Level test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Transmit Power Level test passed with %i device(s)" %transport.n_devices);
    return 0;
