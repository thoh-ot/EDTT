from components.basic_commands import le_set_advertising_parameters;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Advertising Parameters",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Advertising Parameters command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set advertising parameters test");
    
    MinInterval = 0;
    MaxInterval = 0;
    type = 0;
    OwnAddrType = 0;
    DirectAddrType = 0;
    AVal = [0 for i in range(6)];
    ChannelMap = 0;
    FilterPolicy = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_advertising_parameters(transport, i, MinInterval, MaxInterval, type, OwnAddrType, DirectAddrType, AVal, ChannelMap, FilterPolicy, 100);
    except Exception as e:
        trace.trace(1, "LE Set Advertising Parameters test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Advertising Parameters test passed with %i device(s)" %transport.n_devices);
    return 0;
