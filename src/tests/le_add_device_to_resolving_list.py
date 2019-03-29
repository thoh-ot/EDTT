from components.basic_commands import le_add_device_to_resolving_list;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Add Device to Resolving List",
                    number_devices = 1,
                    description = "Test that we can execute the LE Add Device to Resolving List command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le add device to resolving list test");
    
    PeerIdAddrType = 0;
    AVal = [0 for i in range(6)];
    PeerIrk = [0 for i in range(16)];
    LocalIrk = [0 for i in range(16)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_add_device_to_resolving_list(transport, i, PeerIdAddrType, AVal, PeerIrk, LocalIrk, 100);
    except Exception as e:
        trace.trace(1, "LE Add Device to Resolving List test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Add Device to Resolving List test passed with %i device(s)" %transport.n_devices);
    return 0;
