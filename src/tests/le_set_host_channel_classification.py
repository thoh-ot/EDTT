from components.basic_commands import le_set_host_channel_classification;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Set Host Channel Classification",
                    number_devices = 1,
                    description = "Test that we can execute the LE Set Host Channel Classification command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le set host channel classification test");
    
    ChMap = [0 for i in range(5)];
    
    try:
        for i in range(0, transport.n_devices):
            status = le_set_host_channel_classification(transport, i, ChMap, 100);
    except Exception as e:
        trace.trace(1, "LE Set Host Channel Classification test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Set Host Channel Classification test passed with %i device(s)" %transport.n_devices);
    return 0;
