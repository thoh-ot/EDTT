from components.basic_commands import host_number_of_completed_packets;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Host Number Of Completed Packets",
                    number_devices = 1,
                    description = "Test that we can execute the Host Number Of Completed Packets command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting host number of completed packets test");
    
    NumHandles = 0;
    HHandle = [0 for i in range(0)];
    HCount = [0 for i in range(0)];
    
    try:
        for i in range(0, transport.n_devices):
            host_number_of_completed_packets(transport, i, NumHandles, HHandle, HCount, 100);
    except Exception as e:
        trace.trace(1, "Host Number Of Completed Packets test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Host Number Of Completed Packets test passed with %i device(s)" %transport.n_devices);
    return 0;
