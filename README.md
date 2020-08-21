# replace-ecs-instances
Ansible role to replace running instances of an ECS cluster.

## Requirements

* python-libraries: botocore, boto3 (on the host that executes the role)
* AWS credentials with the permissions to create CloudFormation stacks and all corresponding AWS resources, either as
  * environment variables **AWS_ACCESS_KEY_ID** and **AWS_SECRET_ACCESS_KEY** or as
  * profile in the file `~/.aws/credentials`, referring to the profile identifier with the variable 
    **ecs_service_profile**

## Install the role via Ansible Galaxy

If you want to install a specific version in a collection with other roles using a role file:
```sh
$ ansible-galaxy install -r roles.yml
```
*roles.yml*
```YAML
  - name: replace-ecs-instances-1.1
    src: git@github.com:searchmetrics/replace-ecs-instances.git
    scm: git
    version: "1.1"
```
* also see the [Ansible Galaxy documentation](http://docs.ansible.com/ansible/galaxy.html) and the 
[Ansible Galaxy introduction](https://galaxy.ansible.com/intro)

## Role Variables

### mandatory

* **aws_profile**
  * description: AWS profile name
  * example: "dataprovisioning"
* **ecs_cluster_clustername**
  * description: AWS ECS cluster name
  * example: "a_very_good_cluster_name"
* **ecs_cluster_autoscalinggroupname**
  * description: Name of the autoscaling group related to the cluster
  * example: "a_very_good_cluster_name-ASG"
* **aws_ecs_replace_nodes_enabled**
  * description: Switch to enable or disable role / replacement
  * example: "true"
