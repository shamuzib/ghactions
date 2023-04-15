[RDS_ACUUtilization_per_DB]
thresholds = 75,90
period = 300
dimension_DBInstanceIdentifier = db-instance-1

[RDS_AuroraReplicaLag_per_DB_on_reader_node]
thresholds = 5000,25000
period = 60
dimension_DBInstanceIdentifier = db-instance-1
dimension_EngineMode = provisioned
dimension_ReadEndpoint = reader

[RDS_CPUUtilization_per_DB]
thresholds = 75,90
period = 300
dimension_DBInstanceIdentifier = db-instance-1

[RDS_ServerlessDBCapacity_riskview-prod-aurora-2]
thresholds = 75,90
period = 300
dimension_DBClusterIdentifier = riskview-prod-aurora-2

[RDS_ACUUtilization_riskvire-prod-aurora-2]
thresholds = 75,90
period = 300
dimension_DBClusterIdentifier = riskview-prod-aurora-2

[RDS_CPUUtilization_riskvire-prod-aurora-2]
thresholds = 75,90
period = 300
dimension_DBClusterIdentifier = riskview-prod-aurora-2




import boto3
import configparser

def create_cloudwatch_alarms(config_file):
    # Read the configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch')

    # Loop through the alarms defined in the configuration file
    for section in config.sections():
        # Get the alarm properties from the configuration file
        metric_name = section.split('_', 1)[1]
        threshold_warning, threshold_critical = map(int, config.get(section, 'thresholds').split(','))
        period = int(config.get(section, 'period'))
        dimensions = [{key: value} for key, value in config.items(section) if key.startswith('dimension_')]

        # Check if the alarm already exists
        alarm_name = f"{metric_name} alarm"
        response = cloudwatch.describe_alarms(AlarmNames=[alarm_name])
        alarms = response['MetricAlarms']

        if len(alarms) > 0:
            print(f"Alarm '{alarm_name}' already exists. Skipping...")
            continue

        # Create the CloudWatch alarm
        print(f"Creating alarm '{alarm_name}'...")
        cloudwatch.put_metric_alarm(
            AlarmName=alarm_name,
            AlarmDescription=f"{metric_name} metric threshold exceeded",
            ActionsEnabled=False,
            MetricName=metric_name,
            Namespace='AWS/RDS',
            Statistic='Average',
            Dimensions=dimensions,
            Period=period,
            EvaluationPeriods=1,
            Threshold=threshold_warning,
            ComparisonOperator='GreaterThanThreshold',
            AlarmActions=[],
            OKActions=[],
            InsufficientDataActions=[]
        )

        # Create the critical threshold alarm
        critical_alarm_name = f"{metric_name} critical alarm"
        print(f"Creating alarm '{critical_alarm_name}'...")
        cloudwatch.put_metric_alarm(
            AlarmName=critical_alarm_name,
            AlarmDescription=f"{metric_name} metric threshold exceeded",
            ActionsEnabled=False,
            MetricName=metric_name,
            Namespace='AWS/RDS',
            Statistic='Average',
            Dimensions=dimensions,
            Period=period,
            EvaluationPeriods
