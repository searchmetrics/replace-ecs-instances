#!/usr/bin/python

import boto3, time, sys, getopt

class ECSConnector:
    def __init__(self, profileName, clusterName, autoScalingGroupName):
        self.profileName = profileName
        self.clusterName = clusterName
        self.autoScalingGroupName = autoScalingGroupName
        session = boto3.Session(profile_name=profileName)
        self.asgClient = session.client("autoscaling")
        self.ecsClient = session.client("ecs")
        self.oldInstances = self.ecsClient.list_container_instances(cluster=self.clusterName, status="ACTIVE")
        response = self.asgClient.describe_auto_scaling_groups(AutoScalingGroupNames=[self.autoScalingGroupName])
        self.maxSize = response['AutoScalingGroups'][0]['MaxSize']

    def startNewInstances(self):
        print("Adding instances")
        self.asgClient.update_auto_scaling_group(
            AutoScalingGroupName=self.autoScalingGroupName,
            MaxSize=self.maxSize * 2
        )
        self.asgClient.set_desired_capacity(
            AutoScalingGroupName=self.autoScalingGroupName,
            DesiredCapacity=len(self.oldInstances["containerInstanceArns"]) * 2,
            HonorCooldown=True,
        )

        print("Wait for instances to get healthy")
        while len(self.ecsClient.list_container_instances(cluster=self.clusterName, status="ACTIVE")["containerInstanceArns"]
        ) == len(self.oldInstances["containerInstanceArns"]):
            print("Still waiting...")
            time.sleep(30)

    def drainTasks(self):
        print("Draining tasks from old instances")
        self.ecsClient.update_container_instances_state(
            cluster=self.clusterName,
            containerInstances=self.oldInstances["containerInstanceArns"],
            status="DRAINING",
        )

        runningTaskCount = 1
        while runningTaskCount != 0:
            print("Still draining tasks...")
            time.sleep(30)
            response = self.ecsClient.describe_container_instances(
                cluster=self.clusterName, containerInstances=self.oldInstances["containerInstanceArns"]
            )
            runningTaskCount = 0
            for instance in response["containerInstances"]:
                runningTaskCount = runningTaskCount + instance["runningTasksCount"]

    def terminateOldInstances(self):
        print("Terminating old instances")
        response = self.ecsClient.describe_container_instances(
                        cluster=self.clusterName, containerInstances=self.oldInstances["containerInstanceArns"]
                    )
        for instance in response["containerInstances"]:
            print(
                self.asgClient.terminate_instance_in_auto_scaling_group(
                    InstanceId=instance["ec2InstanceId"], ShouldDecrementDesiredCapacity=True
                )["Activity"]["Description"]
            )
        self.asgClient.update_auto_scaling_group(
            AutoScalingGroupName=self.autoScalingGroupName,
            MaxSize=self.maxSize
        )

def main(argv):
    profileName = ''
    clusterName = ''
    autoScalingGroupName = ''
    try:
        opts, args = getopt.getopt(argv,"p:c:a:",["profile=","cluster=","autoscalinggroup="])
    except getopt.GetoptError as error:
        print(error)
        sys.exit(2)

    if len(opts) != 3:
        print("Usage: python replace_instances.py -p <profile-name> -c <cluster-name> -a <asg-name>")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-p", "--profile"):
            profileName = arg
        elif opt in ("-c", "--cluster"):
            clusterName = arg
        elif opt in ("-a", "--autoscalinggroup"):
            autoScalingGroupName = arg


    ecsConnector = ECSConnector(profileName=profileName, clusterName=clusterName, autoScalingGroupName=autoScalingGroupName)
    ecsConnector.startNewInstances()
    ecsConnector.drainTasks()
    ecsConnector.terminateOldInstances()

if __name__ == "__main__":
    main(sys.argv[1:])