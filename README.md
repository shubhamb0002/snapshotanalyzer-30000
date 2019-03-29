# snapshotanalyzer-30000

Demo project to manage EC2 instances snapshots

## About

This project is a demo and uses boto3 to manage the AWS EC2 instances snapshots.

## Configuring

Shotty uses configuration file generated by the AWS cli. e.g.

` aws configure --profile shotty`

## Running

 `pipenv run "python/python.py <command>
 --Project=PROJECT"`

 *Command* is list, start or stop
 *Project* is optional
