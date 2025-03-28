from storages.backends.s3boto3 import S3Boto3Storage

class StaticStorage(S3Boto3Storage):
    location = 'static'
    default_acl = 'public-read'

class MediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False
    default_acl = 'public-read'

class PublicMediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False
    default_acl = 'public-read'

    def get_available_name(self, name, max_length=None):
        if self.exists(name):
            self.delete(name)
        return name
