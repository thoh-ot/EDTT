from components.basic_commands import read_remote_version_information;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Remote Version Information",
                    number_devices = 1,
                    description = "Test that we can execute the Read Remote Version Information command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read remote version information test");
    
    handle = 0;
    
    try:
        for i in range(0, transport.n_devices):
            read_remote_version_information(transport, i, handle, 100);
    except Exception as e:
        trace.trace(1, "Read Remote Version Information test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Remote Version Information test passed with %i device(s)" %transport.n_devices);
    return 0;
