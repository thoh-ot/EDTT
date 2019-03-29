from components.basic_commands import write_authenticated_payload_timeout;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Write Authenticated Payload Timeout",
                    number_devices = 1,
                    description = "Test that we can execute the Write Authenticated Payload Timeout command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting write authenticated payload timeout test");
    
    handle = 0;
    AuthPayloadTimeout = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle = write_authenticated_payload_timeout(transport, i, handle, AuthPayloadTimeout, 100);
    except Exception as e:
        trace.trace(1, "Write Authenticated Payload Timeout test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Write Authenticated Payload Timeout test passed with %i device(s)" %transport.n_devices);
    return 0;
