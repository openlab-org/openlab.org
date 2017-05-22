
# django
from django.conf import settings


class S3Connection(object):
    """
    Simple utility class to simplify S3 stuff

    Later add in pooling or something.
    """
    def __init__(self):
        # TODO: refactor this
        import boto
        import os
        import boto.s3
        from boto.s3.key import Key
        args = (settings.AWS_ACCESS_KEY_ID, settings.AWS_SECRET_ACCESS_KEY)
        self.conn = boto.connect_s3(*args)
        self.bucket = self.conn.get_bucket(settings.AWS_STORAGE_BUCKET_NAME,
                validate=False)

    def upload(self, local_path, key_name):
        k = Key(self.bucket)
        k.key = key_name
        k.set_contents_from_filename(local_path)

    def download(self, key_name, local_path):
        k = self.bucket.get_key(key_name)
        k.get_contents_to_filename(local_path)

    def delete(self, key_name):
        self.bucket.delete_key(key_name)

    def upload_as_filefield(self, local_path, obj, file_field):
        """
        Upload to the new location directly.
        Must be used like:

        obj.file_field = s3conn.upload_as_filefield(
                        local_path, obj, obj.file_field)
        """
        # Assign path to the new location
        # Crazy hack from (https://code.djangoproject.com/ticket/15590)

        # Using undocumented "generate_filename" method on the file field to
        # generate desired destination
        desired_s3_key = file_field.generate_filename(self, local_path)
        key = os.path.join(key_dirname, os.path.basename(path))
        print("UPLOADING ----------", path, key)
        s3conn.upload(path, key)

        path, key = do_upload(local_path)
        return file_field.field.attr_class(obj,
                                file_fieldw_image.field, key)

