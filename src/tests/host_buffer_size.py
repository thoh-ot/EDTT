from components.basic_commands import host_buffer_size;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Host Buffer Size",
                    number_devices = 1,
                    description = "Test that we can execute the Host Buffer Size command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting host buffer size test");
    
    AclMtu = 0;
    ScoMtu = 0;
    AclPkts = 0;
    ScoPkts = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = host_buffer_size(transport, i, AclMtu, ScoMtu, AclPkts, ScoPkts, 100);
    except Exception as e:
        trace.trace(1, "Host Buffer Size test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Host Buffer Size test passed with %i device(s)" %transport.n_devices);
    return 0;
