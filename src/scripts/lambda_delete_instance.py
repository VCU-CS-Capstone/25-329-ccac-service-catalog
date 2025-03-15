import json
import boto3

REGION = 'us-east-1'

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    try:
        # Get the instance_id from the event
        instance_id = event.get('instance_id')
        
        if not instance_id:
            raise ValueError("No instance_id provided in the event")

        # Terminate the instance
        response = ec2.terminate_instances(InstanceIds=[instance_id])

        # Check if the termination was successful
        terminating_instances = response['TerminatingInstances']
        if not terminating_instances:
            raise Exception("Instance termination failed: No instance information returned.")

        terminated_instance = terminating_instances[0]
        current_state = terminated_instance['CurrentState']['Name']

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Instance termination initiated successfully!',
                'InstanceId': instance_id,
                'CurrentState': current_state
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
