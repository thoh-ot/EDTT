from components.basic_commands import set_event_mask_page_2;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Set Event Mask Page 2",
                    number_devices = 1,
                    description = "Test that we can execute the Set Event Mask Page 2 command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting set event mask page 2 test");
    
    EventsPage2 = [0 for i in range(8)];
    
    try:
        for i in range(0, transport.n_devices):
            status = set_event_mask_page_2(transport, i, EventsPage2, 100);
    except Exception as e:
        trace.trace(1, "Set Event Mask Page 2 test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Set Event Mask Page 2 test passed with %i device(s)" %transport.n_devices);
    return 0;
