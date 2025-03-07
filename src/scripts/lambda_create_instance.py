# import built-in modules
import base64
import os
import json

# import parsing modules
import httplib2
import html2text

# import gmail modules
from googleapiclient import errors, discovery
from oauth2client import client

# import email modules
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import mimetypes
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase

# import AWS modules
import boto3

# Global Variable
GOLDEN_IMAGES = {
    "base": {
        "ami": "ami-01d5f3f370b275f82",
        "security_group_ids": ["sg-08a17b49bac61e303"]
    }
}
SUBNET_ID = "subnet-01514850617d9c273"
INSTANCE_TYPE = 't2.micro'
KEY_NAME = 'service-catalog'
REGION = 'us-east-1'
MAX_COUNT = 1
MIN_COUNT = 1

SENDER_EMAIL = "vcuservicecatalog@gmail.com"

ec2 = boto3.client('ec2', region_name=REGION)

def lambda_handler(event, context):
    try:
        user_name = event.get("user_name", "rodney")  # Use default if not provided
        user_password = event.get("user_password", "gorams")
        image_type = event.get("image_type", "base")  # Use default if not provided
        user_email = event.get("user_email")
        if not user_email:
            raise Exception("User email not provided.")

        user_data = f'''#!/bin/bash
        USERNAME="{user_name}"
        PASSWORD=$(openssl passwd -6 "{user_password}")
        useradd -m -s /bin/bash "$USERNAME"
        echo "$USERNAME:$PASSWORD" | sudo chpasswd -e
        usermod -aG sudo "$USERNAME"
        '''

        response = ec2.run_instances(
            ImageId=GOLDEN_IMAGES["base"]["ami"],
            InstanceType=INSTANCE_TYPE,
            KeyName=KEY_NAME,
            MaxCount=MAX_COUNT,
            MinCount=MIN_COUNT,
            SubnetId=SUBNET_ID,
            SecurityGroupIds=GOLDEN_IMAGES["base"]["security_group_ids"],
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [{'Key': 'Name', 'Value': 'Test_Lambda'}]
                },
            ],
            UserData=user_data
        )

        # Ensure instance is created
        instances = response.get("Instances", [])
        if not instances:
            raise Exception("Instance creation failed: No instance information returned.")

        instance_id = instances[0]["InstanceId"]

        # Fetch public IP (wait until assigned)
        ec2_resource = boto3.resource('ec2', region_name=REGION)
        instance = ec2_resource.Instance(instance_id)

        instance.wait_until_running()  # Ensure instance is running
        instance.reload()  # Refresh instance data

        public_ip = instance.public_dns_name
        if not public_ip:
            raise Exception("No public IP assigned (Check security group & subnet settings).")

        email_subject = f"Credentials for {image_type} VM - VCU Service Catalog Team"
        html_message = f"""
        <html>
            <body>
                Here are the credentials for your {image_type} Virtual Machine:<br><br>
                Instance ID: {instance_id}<br>
                IP Address: {public_ip}<br>
                username: {user_name}<br>
                password: {user_password}<br><br>
                - VCU Service Catalog Team
            </body>
        </html>
        """

        if SendMessage(
                SENDER_EMAIL, 
                user_email, 
                email_subject, 
                msgHtml=html_message, 
                msgPlain=html_to_plain_text(html_message)) == "Error":
            raise Exception("Error sending email")

        return {
            'statusCode': 200,
            'body': json.dumps({
                'message': 'Instance created successfully!',
                'InstanceId': instance_id,
                'PublicIP': public_ip
            })
        }

    except Exception as e:
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }

'''
FUNCTIONS FOR CREATING AND SEND EMAIL MESSAGE USING GMAIL API
Code from: https://medium.com/@nakulkurane/sending-gmail-on-aws-lambda-via-python-a7fa991a97f1
'''
def get_credentials():
    client_id = os.environ['GMAIL_CLIENT_ID']
    client_secret = os.environ['GMAIL_CLIENT_SECRET']
    refresh_token = os.environ['GMAIL_REFRESH_TOKEN']
    credentials = client.GoogleCredentials(None, 
        client_id, 
        client_secret,
        refresh_token,
        None,
        "https://accounts.google.com/o/oauth2/token",
        'my-user-agent'
    )
    
    return credentials


def SendMessage(sender, to, subject, msgHtml, msgPlain, attachmentFile=None):
    credentials = get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('gmail', 'v1', http=http, cache_discovery=False)
    if attachmentFile:
        message1 = createMessageWithAttachment(sender, to, subject, msgHtml, msgPlain, attachmentFile)
    else:
        message1 = CreateMessageHtml(sender, to, subject, msgHtml, msgPlain)
    result = SendMessageInternal(service, "me", message1)
    return result


def SendMessageInternal(service, user_id, message):
    try:
        message = (service.users().messages().send(userId=user_id, body=message).execute())
        print('Message Id: %s' % message['id'])
        return message
    except errors.HttpError as error:
        print('An error occurred: %s' % error)
        return "Error"


def CreateMessageHtml(sender, to, subject, msgHtml, msgPlain):
    msg = MIMEMultipart('alternative')
    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = to
    msg.attach(MIMEText(msgPlain, 'plain'))
    msg.attach(MIMEText(msgHtml, 'html'))
    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('UTF-8')).decode('ascii')}


def createMessageWithAttachment(
        sender, to, subject, msgHtml, msgPlain, attachmentFile):
    """Create a message for an email.
    Args:
      sender: Email address of the sender.
      to: Email address of the receiver.
      subject: The subject of the email message.
      msgHtml: Html message to be sent
      msgPlain: Alternative plain text message for older email clients
      attachmentFile: The path to the file to be attached.
    Returns:
      An object containing a base64url encoded email object.
    """
    message = MIMEMultipart('mixed')
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject

    messageA = MIMEMultipart('alternative')
    messageR = MIMEMultipart('related')

    messageR.attach(MIMEText(msgHtml, 'html'))
    messageA.attach(MIMEText(msgPlain, 'plain'))
    messageA.attach(messageR)

    message.attach(messageA)

    print("create_message_with_attachment: file: %s" % attachmentFile)
    content_type, encoding = mimetypes.guess_type(attachmentFile)

    if content_type is None or encoding is not None:
        content_type = 'application/octet-stream'
    main_type, sub_type = content_type.split('/', 1)
    if main_type == 'text':
        fp = open(attachmentFile, 'rb')
        msg = MIMEText(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'image':
        fp = open(attachmentFile, 'rb')
        msg = MIMEImage(fp.read(), _subtype=sub_type)
        fp.close()
    elif main_type == 'audio':
        fp = open(attachmentFile, 'rb')
        msg = MIMEAudio(fp.read(), _subtype=sub_type)
        fp.close()
    else:
        fp = open(attachmentFile, 'rb')
        msg = MIMEBase(main_type, sub_type)
        msg.set_payload(fp.read())
        fp.close()
    filename = os.path.basename(attachmentFile)
    msg.add_header('Content-Disposition', 'attachment', filename=filename)
    message.attach(msg)

    return {'raw': base64.urlsafe_b64encode(msg.as_string().encode('UTF-8')).decode('ascii')}

def html_to_plain_text(html):
    plain = html2text.html2text(html)
    return plain
'''
END EMAIL FUNCTIONS
'''