from components.basic_commands import le_set_default_phy;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Default PHY",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Default PHY command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set default phy test");
    
    AllPhys = 0;
    TxPhys = 0;
    RxPhys = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_default_phy(transport, i, AllPhys, TxPhys, RxPhys, 100);
    except Exception as e:
        trace.trace(1, "LE Set Default PHY test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Default PHY test passed with %i device(s)" %transport.n_devices);
    return 0;
