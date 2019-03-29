from components.basic_commands import le_read_peer_resolvable_address;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Peer Resolvable Address",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Peer Resolvable Address command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read peer resolvable address test");
    
    PeerIdAddrType = 0;
    AVal = [0 for i in range(6)];
    
    try:
        for i in range(0, transport.n_devices):
            status, PeerRpaVal = le_read_peer_resolvable_address(transport, i, PeerIdAddrType, AVal, 100);
    except Exception as e:
        trace.trace(1, "LE Read Peer Resolvable Address test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Peer Resolvable Address test passed with %i device(s)" %transport.n_devices);
    return 0;
