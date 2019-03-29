from components.basic_commands import read_authenticated_payload_timeout;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Authenticated Payload Timeout",
                    number_devices = 1,
                    description = "Test that we can execute the Read Authenticated Payload Timeout command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read authenticated payload timeout test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle, AuthPayloadTimeout = read_authenticated_payload_timeout(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "Read Authenticated Payload Timeout test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Authenticated Payload Timeout test passed with %i device(s)" %transport.n_devices);
    return 0;
