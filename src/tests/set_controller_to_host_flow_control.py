from components.basic_commands import set_controller_to_host_flow_control;

"""
    Return the specification which contains information about the command
"""
def spec():
    from components.test_spec import TestSpec;
    spec = TestSpec(name = "Set Controller To Host Flow Control",
                    number_devices = 1,
                    description = "Test that we can execute the Set Controller To Host Flow Control command.");
    return spec;

"""
    Run the command...
"""
def main(args, transport, trace):
    trace.trace(3, "Starting set controller to host flow control test");
    
    FlowEnable = 0;
    
    try:
        for i in range(0, transport.n_devices):
            status = set_controller_to_host_flow_control(transport, i, FlowEnable, 100);
    except Exception as e:
        trace.trace(1, "Set Controller To Host Flow Control test failed: %s" %str(e));
        return 1;

    trace.trace(3, "Set Controller To Host Flow Control test passed with %i device(s)" %transport.n_devices);
    return 0;
