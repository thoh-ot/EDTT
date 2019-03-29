from components.basic_commands import read_local_version_information;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Read Local Version Information",
                    number_devices = 1,
                    description = "Test that we can execute the Read Local Version Information command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting read local version information test");
    
    try:
        for i in range(0, transport.n_devices):
            status, HCIVersion, HCIRevision, LMPVersion, manufacturer, LMPSubversion = read_local_version_information(transport, i, 100);
    except Exception as e:
        trace.trace(1, "Read Local Version Information test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Read Local Version Information test passed with %i device(s)" %transport.n_devices);
    return 0;
