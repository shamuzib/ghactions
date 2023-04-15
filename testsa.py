[RDS_ACUUtilization_Per_DB]
namespace = AWS/RDS
metric_name = ACUUtilization
dimensions = DBInstanceIdentifier:{DBInstanceIdentifier}
thresholds = 75,90
period = 300

[RDS_AuroraReplicaLag_Per_Instance]
namespace = AWS/RDS
metric_name = AuroraReplicaLag
dimensions = DBInstanceIdentifier:{DBInstanceIdentifier}
thresholds = 5000,25000
period = 300

[RDS_CPUUtilization_Per_Instance]
namespace = AWS/RDS
metric_name = CPUUtilization
dimensions = DBInstanceIdentifier:{DBInstanceIdentifier}
thresholds = 75,90
period = 300

[RDS_ServerlessDBCapacity_Per_Cluster]
namespace = AWS/RDS
metric_name = ServerlessDBCapacity
dimensions = DBClusterIdentifier:riskvire-prod-aurora-2
thresholds = 75,90
period = 300

[RDS_ACUUtilization_Per_Cluster]
namespace = AWS/RDS
metric_name = ACUUtilization
dimensions = DBClusterIdentifier:riskvire-prod-aurora-2
thresholds = 75,90
period = 300

[RDS_CPUUtilization_Per_Cluster]
namespace = AWS/RDS
metric_name = CPUUtilization
dimensions = DBClusterIdentifier:riskvire-prod-aurora-2
thresholds = 75,90
period = 300



import boto3
import configparser

# Read the configuration file
config = configparser.ConfigParser()
config.read('config.ini')

# Set up the client for CloudWatch
cloudwatch = boto3.client('cloudwatch')

# Helper function to create an alarm
def create_alarm(metric_name, namespace, dimensions, alarm_name, alarm_description, comparison_operator, thresholds, period):
    response = cloudwatch.put_metric_alarm(
        AlarmName=alarm_name,
        AlarmDescription=alarm_description,
        ActionsEnabled=True,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic='Average',
        Dimensions=dimensions,
        Period=period,
        EvaluationPeriods=1,
        Threshold=thresholds[0],
        ComparisonOperator=comparison_operator,
        AlarmActions=['arn:aws:sns:us-east-1:123456789012:my-topic-1']
    )

    # Create the second alarm for critical threshold
    response = cloudwatch.put_metric_alarm(
        AlarmName=alarm_name + '-Critical',
        AlarmDescription=alarm_description + ' (critical)',
        ActionsEnabled=True,
        MetricName=metric_name,
        Namespace=namespace,
        Statistic='Average',
        Dimensions=dimensions,
        Period=period,
        EvaluationPeriods=1,
        Threshold=thresholds[1],
        ComparisonOperator=comparison_operator,
        AlarmActions=['arn:aws:sns:us-east-1:123456789012:my-topic-2']
    )

    return response

# Create alarms for RDS ACUUtilization per DB metric
for section in config.sections():
    if 'RDS_ACUUtilization_Per_DB' in section:
        db_instance_identifier = section.split('_')[-1]
        metric_name = config.get(section, 'metric_name')
        namespace = config.get(section, 'namespace')
        thresholds = list(map(int, config.get(section, 'thresholds').split(',')))
        dimensions = [
            {
                'Name': 'DBInstanceIdentifier',
                'Value': db_instance_identifier
            }
        ]
        period = int(config.get(section, 'period'))
        alarm_name = f'RDS-{metric_name}-{db_instance_identifier}'
        alarm_description = f'Alarm for {metric_name} on RDS instance {db_instance_identifier}'
        comparison_operator = 'GreaterThanThreshold'
        create_alarm(metric_name, namespace, dimensions, alarm_name, alarm_description, comparison_operator, thresholds, period)

# Create alarms for RDS AuroraReplicaLag per instance metric
for section in config.sections():
    if 'RDS_AuroraReplicaLag_Per_Instance' in section:
        db_instance_identifier = section.split('_')[-1]
        metric_name = config.get(section, 'metric_name')
        namespace = config.get(section, 'namespace')
        thresholds = list(map(int, config.get(section, 'thresholds').split(',')))
        dimensions = [
            {
                'Name': 'DBInstanceIdentifier',
                'Value': db_instance_identifier
            },
            {
                'Name': 'EngineName',
                'Value': 'aurora'
            },
            {
                'Name': 'Role',
                'Value': 'READER'
            }
        ]
        period = int(config.get(section, 'period'))
        alarm_name = f'RDS-{metric_name}-{db_instance_identifier}-READER'
        alarm_description = f'Alarm for {metric_name} on Aurora reader node {db_instance_identifier}'
        comparison_operator = 'GreaterThanThreshold'
        create_alarm(metric_name, namespace, dimensions, alarm_name, alarm_description, comparison_operator, thresholds, period
