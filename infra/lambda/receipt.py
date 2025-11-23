# Lambda

import json
import boto3
import os
import urllib.parse
import uuid
from datetime import datetime
import pg8000.native

rekognition = boto3.client("rekognition")
secrets_manager = boto3.client("secretsmanager")

DB_HOST = os.environ.get("DB_HOST")
DB_SECRET_NAME = os.environ.get("DB_SECRET_NAME")


def get_db_connection():
    try:
        secret_value = secrets_manager.get_secret_value(SecretId=DB_SECRET_NAME)
        secret = json.loads(secret_value["SecretString"])

        conn = pg8000.native.Connection(
            user=secret["username"],
            password=secret["password"],
            host=DB_HOST,
            database="fridger",
            port=5432,
        )
        return conn
    except Exception as e:
        print(f"Error connecting to database: {e}")
        raise e


def handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    bucket = event["Records"][0]["s3"]["bucket"]["name"]
    key = urllib.parse.unquote_plus(
        event["Records"][0]["s3"]["object"]["key"], encoding="utf-8"
    )

    try:
        response = rekognition.detect_text(
            Image={"S3Object": {"Bucket": bucket, "Name": key}}
        )

        detected_text_lines = []
        for item in response["TextDetections"]:
            if item["Type"] == "LINE":
                detected_text_lines.append(item["DetectedText"])

        print(f"Detected text: {detected_text_lines}")

        receipt_id = str(uuid.uuid4())

        conn = get_db_connection()

        # TODO: receipt 테이블 만들지 고민중
        insert_query = """
        INSERT INTO receipts (id, image_url, upload_time, raw_text_data, status)
        VALUES (:id, :image_url, :upload_time, :raw_text_data, :status)
        """

        conn.run(
            insert_query,
            id=receipt_id,
            image_url=f"s3://{bucket}/{key}",
            upload_time=datetime.utcnow(),
            raw_text_data=json.dumps(detected_text_lines),
            status="ANALYZED",
        )

        conn.close()

        print(f"Saved receipt {receipt_id} to RDS")
        return {
            "statusCode": 200,
            "body": json.dumps(f"Successfully saved receipt: {receipt_id}"),
        }

    except Exception as e:
        print(f"Error processing {key}: {e}")
        raise e
