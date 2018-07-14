from rest_framework import serializers

from tunga_uploads.models import Upload
from tunga_utils.serializers import SimplestUserSerializer, CreateOnlyCurrentUserDefault


class UploadSerializer(serializers.ModelSerializer):
    user = SimplestUserSerializer(
        required=False, read_only=True, default=CreateOnlyCurrentUserDefault()
    )
    url = serializers.CharField(required=False, read_only=True, source='file.url')
    name = serializers.SerializerMethodField(required=False, read_only=True)
    size = serializers.IntegerField(required=False, read_only=True, source='file.size')
    display_size = serializers.SerializerMethodField(required=False, read_only=True)

    class Meta:
        model = Upload
        fields = '__all__'

    def get_name(self, obj):
        return obj.file.name.split('/')[-1]

    def get_display_size(self, obj):
        filesize = obj.file.size
        converter = {'KB': 10 ** 3, 'MB': 10 ** 6, 'GB': 10 ** 9, 'TB': 10 ** 12}
        units = ['TB', 'GB', 'MB', 'KB']

        for label in units:
            conversion = converter[label]
            if conversion and filesize > conversion:
                return '%s %s' % (round(filesize / conversion, 2), label)
        return '%s %s' % (filesize, 'bytes')
