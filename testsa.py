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
from configparser import ConfigParser

# Function to create CloudWatch alarms based on configurations specified in config.ini file
def create_cloudwatch_alarms():
    # Read configuration from file
    config = ConfigParser()
    config.read('config.ini')

    # Create CloudWatch client
    cloudwatch = boto3.client('cloudwatch')

    # Loop through all sections in the configuration file
    for section in config.sections():
        # Extract configuration parameters
        metric_name = section.split("_")[1]
        cluster_name = section.split("_")[-1]
        thresholds = config.get(section, "thresholds").split(",")
        period = int(config.get(section, "period"))
        db_instance_identifier = config.get(section, "dimension_DBInstanceIdentifier", fallback=None)

        # Check if specified alarm already exists
        alarms = cloudwatch.describe_alarms(AlarmNamePrefix=f"{metric_name} {cluster_name}")
        if len(alarms['MetricAlarms']) > 0:
            print(f"Alarm '{metric_name} {cluster_name}' already exists. Skipping creation.")
            continue

        # Set threshold values based on configuration
        threshold_warning = float(thresholds[0])
        threshold_critical = float(thresholds[1])

        # Define dimensions for the alarm based on configuration
        dimensions = []
        if db_instance_identifier:
            dimensions.append({
                'Name': 'DBInstanceIdentifier',
                'Value': db_instance_identifier
            })

        # Create the warning threshold alarm
        warning_alarm_name = f"{metric_name} warning alarm"
        print(f"Creating alarm '{warning_alarm_name}'...")
        cloudwatch.put_metric_alarm(
            AlarmName=warning_alarm_name,
            AlarmDescription=f"{metric_name} metric threshold exceeded",
            ActionsEnabled=False,
            MetricName=metric_name,
            Namespace='AWS/RDS',
            Statistic='Average',
            Dimensions=dimensions,
            Period=period,
            EvaluationPeriods=2,
            Threshold=threshold_warning,
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
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
            EvaluationPeriods=3,
            Threshold=threshold_critical,
            ComparisonOperator='GreaterThanThreshold',
            TreatMissingData='notBreaching'
        )
