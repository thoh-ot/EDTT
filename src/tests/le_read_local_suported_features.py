from components.basic_commands import le_read_local_supported_features;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Local Supported Features",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Local Supported Features command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read local supported features test");
    
    try:
        for i in range(0, transport.n_devices):
            status, features = le_read_local_supported_features(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Local Supported Features test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Local Supported Features test passed with %i device(s)" %transport.n_devices);
    return 0;
