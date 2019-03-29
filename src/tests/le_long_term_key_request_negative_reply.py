from components.basic_commands import le_long_term_key_request_negative_reply;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Long Term Key Request Negative Reply",
                    number_devices = 1,
                    description = "Test that we can execute the LE Long Term Key Request Negative Reply command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le long term key request negative reply test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle = le_long_term_key_request_negative_reply(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "LE Long Term Key Request Negative Reply test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Long Term Key Request Negative Reply test passed with %i device(s)" %transport.n_devices);
    return 0;
