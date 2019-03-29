from components.basic_commands import le_remote_connection_parameter_request_negative_reply;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Remote Connection Parameter Request Negative Reply",
                    number_devices = 1,
                    description = "Test that we can execute the LE Remote Connection Parameter Request Negative Reply command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le remote connection parameter request negative reply test");
    
    handle = 0;
    reason = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle = le_remote_connection_parameter_request_negative_reply(transport, i, handle, reason, 100);
    except Exception as e:
        trace.trace(1, "LE Remote Connection Parameter Request Negative Reply test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Remote Connection Parameter Request Negative Reply test passed with %i device(s)" %transport.n_devices);
    return 0;
