from components.basic_commands import le_remote_connection_parameter_request_reply;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Remote Connection Parameter Request Reply",
                    number_devices = 1,
                    description = "Test that we can execute the LE Remote Connection Parameter Request Reply command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le remote connection parameter request reply test");
    
    handle = 0;
    IntervalMin = 0;
    IntervalMax = 0;
    latency = 0;
    timeout = 0;
    MinCeLen = 0;
    MaxCeLen = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status, handle = le_remote_connection_parameter_request_reply(transport, i, handle, IntervalMin, IntervalMax, latency, timeout, MinCeLen, MaxCeLen, 100);
    except Exception as e:
        trace.trace(1, "LE Remote Connection Parameter Request Reply test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Remote Connection Parameter Request Reply test passed with %i device(s)" %transport.n_devices);
    return 0;
