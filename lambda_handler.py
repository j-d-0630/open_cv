import json
import boto3

s3 = boto3.resource("s3")

def lambda_handler(event, context):
    # TODO implement
    print(event["time"])
    print(event["detection_result"])
    
    bucket = "for-face-detection-1"
    key = "data/" + "detection_result" + ".txt"
    
    
    if event["detection_result"] == 0:
        file_contents = "{} : 不在！".format(event["time"])
    else:
        file_contents = "{} : ちゃんと勉強してますね！".format(event["time"])

    obj = s3.Object(bucket,key)
    obj.put(Body=file_contents, ContentType="text/plain")
    
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }
