from components.basic_commands import reset;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Reset",
                    number_devices = 1,
                    description = "Test that we can execute the Reset command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting reset test");
    
    try:
        for i in range(0, transport.n_devices):
            status = reset(transport, i, 100);
    except Exception as e:
        trace.trace(1, "Reset test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Reset test passed with %i device(s)" %transport.n_devices);
    return 0;
