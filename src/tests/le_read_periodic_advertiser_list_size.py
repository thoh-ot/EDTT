from components.basic_commands import le_read_periodic_advertiser_list_size;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Read Periodic Advertiser List Size",
                    number_devices = 1,
                    description = "Test that we can execute the LE Read Periodic Advertiser List Size command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le read periodic advertiser list size test");
    
    try:
        for i in range(0, transport.n_devices):
            status, ListSize = le_read_periodic_advertiser_list_size(transport, i, 100);
    except Exception as e:
        trace.trace(1, "LE Read Periodic Advertiser List Size test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Read Periodic Advertiser List Size test passed with %i device(s)" %transport.n_devices);
    return 0;
