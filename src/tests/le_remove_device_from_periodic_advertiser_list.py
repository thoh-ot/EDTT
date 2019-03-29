from components.basic_commands import le_remove_device_from_periodic_advertiser_list;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "LE Remove Device From Periodic Advertiser List",
                    number_devices = 1,
                    description = "Test that we can execute the LE Remove Device From Periodic Advertiser List command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting le remove device from periodic advertiser list test");
    
    AddrType = 0;
    AVal = [0 for i in range(6)];
    sid = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = le_remove_device_from_periodic_advertiser_list(transport, i, AddrType, AVal, sid, 100);
    except Exception as e:
        trace.trace(1, "LE Remove Device From Periodic Advertiser List test failed: %s" %str(e));
        return 1;

    trace.trace(3, "LE Remove Device From Periodic Advertiser List test passed with %i device(s)" %transport.n_devices);
    return 0;
