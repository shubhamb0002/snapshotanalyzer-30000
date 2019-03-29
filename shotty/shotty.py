import boto3
import click

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

@click.group()
def cli():
    "shotty manages snapshots"

@cli.group('volumes')
def volumes():
    "Commands for Volumes"

@volumes.command('list')
@click.option('--Project', default=None, help="Only volumes for project (tag Project:<name>)")
def list_volumes(project):
    "List EC2 Volumes"

    instances = filter_instances(project)

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
def list_volumes(project):
    "List Volumes Snapshots"

    instances = filter_instances(project)

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
    return

@cli.group('instances')
def instances():
        "Commands for instances "

@instances.command('snapshots', help="Create snapshots of all volumes")
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
def create_snapshots(project):
    "Create snapshots for EC2 instances"

    instances = filter_instances(project)

    for i in instances.all():
        for v in i.volumes.all():
            print("Creating snapshots of {0}".format(v.id))
            v.create_snapshot(Description="created by an snapshotAlyzer 30000")
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
def stop_instances(project):
    "Stop EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Stoping....{0}".format(i.id))
        i.stop()

    return


@instances.command('start')
@click.option('--Project', default=None, help="Only instances for project (tag Project:<name>)")
def start_instances(project):
    "Start EC2 instances"

    instances = filter_instances(project)

    for i in instances:
        print("Starting...{0}".format(i.id))
        i.start()

    return

if __name__ == '__main__':
    cli()
