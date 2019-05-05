import re
import unidecode

from django.core.exceptions import ValidationError
from django.core.files.storage import FileSystemStorage
from django.db import models
from django.dispatch import receiver
from django.urls import reverse
from unidecode import unidecode

from omr import services


def get_valid_name(name):
    name = str(name).strip()  # Strip start/end whitespaces
    name = unidecode(name)  # Convert to ascii, e.g. é becomes e
    name = re.sub(r'[:\\\/]', '-', name)  # Convert : \ and / to -
    name = re.sub(r'(?u)[^-\w. ]', '', name)  # Remove everything else that's not a standard character
    return name


class CustomStorage(FileSystemStorage):
    def get_valid_name(self, name):
        return get_valid_name(name)


class File(models.Model):
    def file_path(self, filename):
        return '/'.join(['LDraw models', get_valid_name(self.model.__str__()), filename])

    model_number = models.CharField(max_length=50, help_text='Full model number including suffix, e.g. 8110-1')
    model = models.ForeignKey(to='Set', editable=False, null=True, blank=True, on_delete=models.CASCADE, related_name='files')
    is_main_model = models.BooleanField(default=True)
    alternate_model = models.CharField(max_length=100, null=True, blank=True)
    author = models.ForeignKey(to='Author', on_delete=models.CASCADE, related_name='files')
    missing_parts = models.BooleanField(default=False)
    missing_patterns = models.BooleanField(default=False)
    missing_stickers = models.BooleanField(default=False)
    notes = models.TextField(null=True, blank=True)
    added = models.DateTimeField(auto_now_add=True, editable=False)
    modified = models.DateTimeField(auto_now=True, editable=False)
    file = models.FileField(upload_to=file_path, storage=CustomStorage())

    def is_complete(self):
        if not self.missing_parts and not self.missing_patterns and not self.missing_stickers:
            return True
        else:
            return False

    def main_or_alternate_str(self):
        if self.is_main_model:
            return 'Main model'
        return self.alternate_model

    def file_header(self):
        try:
            with open(self.file.path, encoding='utf8') as file:
                header_complete = False
                lines = file.readlines()
                linenumber = 0
                header = []

                while not header_complete:
                    line = lines[linenumber]
                    if line[0].isdigit():
                        if int(line[0]) > 0:
                            header_complete = True
                        else:
                            header.append(line)
                    else:
                        header.append(line)
                    linenumber += 1
                return header
        except:
            error = ['Error: file could not be found or read']
            return error

    def get_absolute_url(self):
        return reverse('file_detail', args=[str(self.id)])

    def clean(self):
        if not self.is_main_model and not self.alternate_model:
            raise ValidationError({
                'alternate_model': ['Please fill in an alternate model name']
            })

        set_info = services.get_set(set_num=self.model_number)
        if set_info.get('detail'):
            raise ValidationError({
                'model_number': ['This set cannot be found on Rebrickable']
            })

    def save(self, *args, **kwargs):
        if not Set.objects.filter(set_num=self.model_number).exists():
            new_set_info = services.get_set(self.model_number)
            theme = services.get_root_theme(new_set_info.get('theme_id')).get('name')

            if not Theme.objects.filter(name=theme).exists():
                Theme.objects.create(name=theme)

            Set.objects.create(set_num=self.model_number, name=new_set_info.get('name'),
                               theme=Theme.objects.get(name=theme), year=new_set_info.get('year'),
                               set_img_url=new_set_info.get('set_img_url'))

        self.model = Set.objects.get(set_num=self.model_number)

        super(File, self).save(*args, **kwargs)

    def __str__(self):
        return f'{self.model} - {self.author}'

    class Meta:
        ordering = ['model']


class Author(models.Model):
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    nickname = models.CharField(max_length=50, null=True, blank=True)

    def __str__(self):
        if self.nickname:
            return f'{self.first_name} {self.last_name} [{self.nickname}]'
        return f'{self.first_name} {self.last_name}'

    class Meta:
        ordering = ['first_name']


@receiver(models.signals.post_delete, sender=File)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `File` object is deleted.
    """
    if instance.file:
        instance.file.delete(save=False)


@receiver(models.signals.pre_save, sender=File)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `File` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = sender.objects.get(pk=instance.pk).file
    except sender.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        old_file.delete(save=False)


########################################################################################################
# The models below are just for caching purposes, the information is retrieved via the Rebrickable API #
########################################################################################################

class Theme(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']


class Set(models.Model):
    set_num = models.CharField(max_length=50)  # Is a charfield because we include the -1 -2 suffix
    name = models.CharField(max_length=255)
    theme = models.ForeignKey('Theme', on_delete=models.CASCADE, related_name='sets')
    year = models.IntegerField()
    set_img_url = models.URLField(null=True, blank=True)

    def __str__(self):
        return f'{self.set_num} - {self.name}'

    class Meta:
        ordering = ['set_num']
