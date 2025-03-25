from storages.backends.s3boto3 import S3Boto3Storage

class PublicMediaStorage(S3Boto3Storage):
    location = ''  # leave empty so files aren't put in a 'media/' subfolder unless you want that
    file_overwrite = False  # keeps the same filename, doesn't rename
    default_acl = 'public-read'

    def get_available_name(self, name, max_length=None):
        # Prevent Django from renaming the file if it exists — instead overwrite
        if self.exists(name):
            self.delete(name)
        return name

class MediaStorage(S3Boto3Storage):
    location = ''
    file_overwrite = False
    default_acl = 'public-read'
