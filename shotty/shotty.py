import boto3
import click
import botocore

session = boto3.Session(profile_name='shotty')
ec2 = session.resource('ec2')

def filter_instances(project):
    instances = []

    if project:
     filters = [{'Name':'tag:Project', 'Values':[project]}]
     instances = ec2.instances.filter(Filters=filters)

    else:
        instances = ec2.instances.all()

    return instances

def snapshot_pending(volume):
    snapshot = list(volume.snapshots.all())
    return snapshot and snapshot[0].state == "pending"

@click.group()
def cli():
    "shotty manages snapshots"

@cli.group('volumes')
def volumes():
    "Commands for Volumes"

@volumes.command('list')
@click.option('--Project', default=None, help="Only volumes for project (tag Project:<name>)")
@click.option('--instance_id', default=None, help="Only volumes associated with that instance id")
def list_volumes(project, instance_id):
    "List EC2 Volumes"

    instances = filter_instances(project)
    instance_id = str(instance_id)
    instance = ec2.Instance(instance_id)  #It will get the instance resources
    if instance_id:
        for j in instance.volumes.all():
                print(', '.join((
                    j.id,
                    instance.id,
                    j.state,
                    str(j.size) + "GiB",
                    j.encrypted and "Encrypted" or "Not Encrypted"
                )))

    else:
        for i in instances:
            for j in i.volumes.all():
                    print(', '.join((
                        j.id,
                        i.id,
                        j.state,
                        str(j.size) + "GiB",
                        j.encrypted and "Encrypted" or "Not Encrypted"
                    )))
    return


@cli.group('snapshots')
def snapshots():
    "Commands for Snapshots"

@snapshots.command('list')
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--all', 'list_all', default=False, is_flag=True,
help="List all snapshots for the volumes, not just the recent one")
@click.option('--instance_id', default=None, help="Only snapshots associated with that instance id")
def list_snapshots(project, list_all, instance_id):
    "List Volumes Snapshots"

    instances = filter_instances(project)
    instance_id = str(instance_id)
    instance = ec2.Instance(instance_id)  #It will get the instance resources

    if instance_id:
        for j in instance.volumes.all():
            for s in j.snapshots.all():
                print(', '.join((
                    s.id,
                    j.id,
                    instance.id,
                    s.state,
                    s.progress,
                    s.start_time.strftime("%c"),
                )))
                if s.state == "completed" and not list_all: break

    else:
        for i in instances:
            for j in i.volumes.all():
                    for s in j.snapshots.all():
                        print(', '.join((
                            s.id,
                            j.id,
                            i.id,
                            s.state,
                            s.progress,
                            s.start_time.strftime("%c"),
                        )))
                        if s.state == "completed" and not list_all: break
    return

@cli.group('instances')
def instances():
        "Commands for instances "

@instances.command('snapshots', help="Create snapshots of all volumes")
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True, help="Force Reboot the instances")
def create_snapshots(project, force):
    "Create snapshots for EC2 instances"

    if project or force:

            instances = filter_instances(project)

            for i in instances.all():
                print("checking the status")
                status = i.state['Name']
                print("Stoping...{0}".format(i.id))

                try:
                    i.stop()
                    i.wait_until_stopped()

                except botocore.exceptions.ClientError as e:
                    print("Could not stop {0} ".format(i.id) + str(e))
                    continue

                for v in i.volumes.all():
                    if snapshot_pending(v):
                        print("Skipping the snapshot creation for .... {0}, creation already in progress!! ".format(v.id))
                        continue
                    print("Creating snapshots of {0}".format(v.id))

                    try:
                        v.create_snapshot(Description="created by an snapshotAlyzer 30000")

                    except botocore.exceptions.ClientError as e:
                        print("Could not created snapshot for {0} ".format(v.id) + str(e))
                        continue

                print("checking the status")
                if status == 'running':
                    print("Starting...{0}".format(i.id))
                    i.start()
                    i.wait_until_running()
                else:
                    print("Instance state was {0}, Leaving it to previous state".format(i.state['Name']))
            print("Job is done!!")
    else:
        print("Please define --Project or --force tag in command")

    return

@instances.command('list')
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
def list_instances(project):
    "List EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        tags = {t['Key']: t['Value'] for t in i.tags or [] }
        print(', '.join((
            i.id,
            i.instance_type,
            i.placement['AvailabilityZone'],
            i.state['Name'],
            i.public_dns_name,
            tags.get('Project', '<no project>')
            )))
    return

@instances.command('stop')
@click.option('--Project', default=None, help="only instances for Project (tag Project:<name>)")
@click.option('--force', is_flag=True, help="Force Reboot the instances")
def stop_instances(project, force):
    "Stop EC2 instances"

    if project or force:

        instances = filter_instances(project)

        for i in instances:
            print("Stoping....{0}".format(i.id))
            try:
                i.stop()

            except botocore.exceptions.ClientError as e:
                print("Cloud not stop {0} ".format(i.id) + str(e))
                continue

    else:
        print("Please define --Project or --force tag in command")

    return


@instances.command('start')
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
@click.option('--force', is_flag=True, help="Force Reboot the instances")
def start_instances(project, force):
    "Start EC2 instances"

    if project or force:

        instances = filter_instances(project)

        for i in instances:
            print("Starting...{0}".format(i.id))
            try:
                i.start()

            except botocore.exceptions.ClientError as e:
                print("Could not start {0} ".format(i.id) + str(e))
                continue

    else:
        print("Please define --Project or --force tag in command")

    return

@instances.command('reboot')
@click.option('--Project', default=None, help="only instances for project (tag Project:<ame>)")
@click.option('--force', is_flag=True, help="Force Reboot the instances")
def reboot_instances(project, force):
    "Reboot EC2 instances"

    if project or force:

        instances = filter_instances(project)

        for i in instances:
            print("Rebooting.... {0} ".format(i.id))
            try:
                i.reboot()

            except botocore.exceptions.ClientError as e:
                print("Could not reboot {0} ".format(i.id) + str(e))
                continue

    else:
        print("Please define --Project or --force tag in command")

    return

if __name__ == '__main__':
    cli()
