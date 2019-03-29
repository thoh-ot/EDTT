from components.basic_commands import le_clear_resolving_list;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Clear Resolving List",
                    number_devices = 1,
                    description = "Test that we can execute the LE Clear Resolving List command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le clear resolving list test");
    
    try:
        for i in range(0, transport.n_devices):
            status = le_clear_resolving_list(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Clear Resolving List test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Clear Resolving List test passed with %i device(s)" %transport.n_devices);
    return 0;
