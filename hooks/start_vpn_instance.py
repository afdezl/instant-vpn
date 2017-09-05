from sceptre.hooks import Hook

import time


class StartVpnInstance(Hook):
    def __init__(self, *args, **kwargs):
        super(StartVpnInstance, self).__init__(*args, **kwargs)

    def run(self):
        """
        run is the method called by Sceptre. It should carry out the work
        intended by this hook.

        self.argument is available from the base class and contains the
        argument defined in the sceptre config file (see below)

        The following attributes may be available from the base class:
        self.stack_config  (A dict of data from <stack_name>.yaml)
        self.environment_config  (A dict of data from config.yaml)
        self.connection_manager (A connection_manager)
        """
        response = self.connection_manager.call(
            service="ec2",
            command="describe_instances",
            kwargs={
                "Filters": [
                    {
                        "Name": "tag:Name",
                        "Values": [self.argument]
                    },
                    {
                        "Name": "instance-state-name",
                        "Values": ["running", "stopped", "pending", "stopping"]
                    }
                ]
            }
        )
        reservations = response["Reservations"]
        num_reservations = len(reservations)
        num_instances = len(reservations[0]["Instances"])
        current_state = reservations[0]["Instances"][0]["State"]["Name"]

        if (num_reservations != 1) or (num_instances != 1):
            print("There's more than one match for the OpenVPN instance.")
            print("Aborting.")
            raise Exception("Multiple or no instance matches for OpenVPN.")

        instance_id = response["Reservations"][0]["Instances"][0]["InstanceId"]

        def start_instance():
            self.connection_manager.call(
                service="ec2",
                command="start_instances",
                kwargs={
                    "InstanceIds": [instance_id]
                }
            )

        def wait_for_instance_state(state):
            counter = 0
            while True:
                response = self.connection_manager.call(
                    service="ec2",
                    command="describe_instances",
                    kwargs={
                        "Filters": [
                            {
                                "Name": "tag:Name",
                                "Values": [self.argument]
                            }
                        ]
                    }
                )
                instance = response["Reservations"][0]["Instances"][0]
                if instance["State"]["Name"] == state:
                    break
                if counter > 12:
                    raise Exception(
                        "Instance did not reach the desired state in time.")
                    break
                time.sleep(5)
                counter += 1

        if current_state == "stopped":
            self.logger.info(
                "VPN instance in state: {0}. Waiting to reach: RUNNING".format(
                    current_state.upper()))
            start_instance()
            wait_for_instance_state("running")
        elif current_state == "stopping":
            self.logger.info(
                "VPN instance in state: {0}. Waiting to reach: RUNNING".format(
                    current_state.upper()))
            wait_for_instance_state("stopped")
            start_instance()
            wait_for_instance_state("running")
        elif current_state == "pending":
            self.logger.info(
                "VPN instance in state: {0}. Waiting to reach: RUNNING".format(
                    current_state.upper()))
            wait_for_instance_state("running")
        elif current_state == "running":
            pass
        self.logger.info("VPN instance running, proceeding with update.")
