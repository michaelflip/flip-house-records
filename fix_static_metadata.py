import boto3
import mimetypes

BUCKET_NAME = 'fliphouserecords-media'
PREFIX = 'static/'  # Only touch files inside /static/

s3 = boto3.client('s3')

def guess_mime_type(key):
    mime_type, _ = mimetypes.guess_type(key)
    return mime_type or 'binary/octet-stream'

def fix_metadata():
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=BUCKET_NAME, Prefix=PREFIX)

    updated = 0

    for page in pages:
        for obj in page.get('Contents', []):
            key = obj['Key']
            mime_type = guess_mime_type(key)

            print(f"Fixing: {key} → {mime_type}")

            # Get the existing object so we can preserve the file
            copy_source = {'Bucket': BUCKET_NAME, 'Key': key}

            # Copy the object onto itself with the correct content-type and ACL
            s3.copy_object(
                Bucket=BUCKET_NAME,
                Key=key,
                CopySource=copy_source,
                ContentType=mime_type,
                ACL='public-read',
                MetadataDirective='REPLACE'
            )

            updated += 1

    print(f"\n✅ Updated metadata for {updated} static files.")

if __name__ == '__main__':
    fix_metadata()
