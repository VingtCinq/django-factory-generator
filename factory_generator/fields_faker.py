from django.conf import settings
from django.template.loader import render_to_string


class FieldFaker:
    """
    Base class to return faker and kwargs
    for a given model field

    :faker - the Faker method to be called
    :faker_kwargs - the kwargs to be passed to the faker method
    :unquote_kwargs - the kwargs that need to be displayed without quote
    :template - the template to use to render the Faker field
    """
    faker_class = ''
    faker_kwargs = []
    unquote_kwargs = []
    need_timezone = False
    template = "factory_generator/default.py-tpl"

    def __init__(self, model, field):
        self.model = model
        self.field = field
        self.root_dir = getattr(settings, 'FACTORY_ROOT_DIR', 'model_factories')
        super(FieldFaker, self).__init__()

    @property
    def context(self):
        """
        Return the context needed to properly define the faker
        """
        return {
            'faker_class': self.get_faker_class(),
            'faker_kwargs': self.get_faker_kwargs(),
            'field': self.field
        }
    
    def render(self):
        return render_to_string(self.template, self.context)

    def get_faker_class(self):
        return self.faker_class

    def get_faker_kwargs(self):
        """
        Get kwargs for the faker instance
        """
        if len(self.faker_kwargs) == 0:
            return ''
        kwargs = {}
        for kwarg in self.faker_kwargs:
            method = "get_{kwarg}".format(kwarg=kwarg)
            if hasattr(self, method):
                kwargs[kwarg] = getattr(self, method)()
            else:
                if hasattr(self, kwarg):
                    kwargs[kwarg] = getattr(self, kwarg)
                else:
                    raise ValueError('Missing property `{kwarg}` or method `get_{kwarg}`for `{class_name}`'.format(
                        class_name=self.__class__.__name__,
                        kwarg=kwarg
                    ))
        arr = []
        for (key,val) in kwargs.items():
            if key in self.unquote_kwargs:
                arr.append("{!s}={!s}".format(key,val))
            else:
                arr.append("{!s}={!r}".format(key,val))
        return ', '.join(arr)


class BigIntegerFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "min", "max"]
    provider = "random_int"
    
    def get_min(self):
        return -9223372036854775808

    def get_max(self):
        return 9223372036854775807


class BinaryFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "length"]
    provider = "binary"
    length = 300


class BooleanFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "elements"]
    provider = "random_element"

    def get_elements(self):
        if self.field.null:
            return (None, True, False)
        else:
            return (True, False)


class CharFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "max_chars"]
    provider = "pystr"

    def get_max_chars(self):
        return self.field.max_length


class ChoiceFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "elements"]
    unquote_kwargs = ["elements"]
    provider = "random_element"

    def get_elements(self):
        return "{field_name}_CHOICES".format(
            field_name = self.field.name.upper()
        )


class DateFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "end_datetime", "tzinfo"]
    unquote_kwargs = ["tzinfo"]
    provider = "date_time"
    need_timezone = True

    def get_end_datetime(self):
        return None
    
    def get_tzinfo(self):
        return "timezone.get_current_timezone()"


class DateTimeFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "end_datetime", "tzinfo"]
    provider = "date_time"
    unquote_kwargs = ["tzinfo"]
    need_timezone = True

    def get_end_datetime(self):
        return None
    
    def get_tzinfo(self):
        return "timezone.get_current_timezone()"


class DecimalFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "left_digits", "right_digits", "positive"]
    provider = "pydecimal"

    def get_positive(self):
        return None

    def get_left_digits(self):
        return self.field.max_digits - self.field.decimal_places

    def get_right_digits(self):
        return self.field.decimal_places


class DurationFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "end_datetime"]
    provider = "time_delta"

    need_timezone = True

    def get_end_datetime(self):
        return None


class EmailFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "safe_email"


class FileFieldFaker(FieldFaker):
    faker_class = "factory.django.FileField"


class FilePathFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "file_path"

class FloatFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "left_digits", "right_digits", "positive"]
    provider = "pyfloat"

    def get_positive(self):
        return None

    def get_left_digits(self):
        return None

    def get_right_digits(self):
        return None


class ForeignKeyFaker(FieldFaker):
    faker_class = "factory.SubFactory"
    faker_kwargs = ["factory"]

    def get_factory(self):
        to = self.field.remote_field.model.__name__
        app_label = self.field.remote_field.model._meta.app_label
        return "{root_dir}.{app_label}.{to}Factory".format(
            root_dir=self.root_dir,
            app_label=app_label,
            to=to
        )


class ImageFieldFaker(FieldFaker):
    faker_class = "factory.django.ImageField"


class IntegerFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "min", "max"]
    provider = "random_int"
    
    def get_min(self):
        return -2147483648

    def get_max(self):
        return 2147483647


class GenericIPAddressFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]

    def get_provider(self):
        if self.field.protocol == 'both':
            return random.choice(['ipv4', 'ipv6'])
        if self.field.protocol == 'IPv4':
            return 'ipv4'
        if self.field.protocol == 'IPv4':
            return 'ipv6'


class ManyToManyFieldFaker(FieldFaker):
    faker_class = None
    template = "factory_generator/manytomany.py-tpl"


class NullBooleanFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "elements"]
    provider = "random_element"
    elements = (None, True, False)


class OneToOneFieldFaker(FieldFaker):
    faker_class = "factory.SubFactory"
    faker_kwargs = ["factory"]

    def get_factory(self):
        to = self.field.remote_field.model.__name__
        app_label = self.field.remote_field.model._meta.app_label
        return "{root_dir}.{app_label}.{to}Factory".format(
            root_dir=self.root_dir,
            app_label=app_label,
            to=to
        )


class PositiveIntegerFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "min", "max"]
    provider = "random_int"
    
    def get_min(self):
        return 0

    def get_max(self):
        return 2147483647


class PositiveSmallIntegerFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "min", "max"]
    provider = "random_int"
    
    def get_min(self):
        return 0

    def get_max(self):
        return 32767


class SlugFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "slug"


class SmallIntegerFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "min", "max"]
    provider = "random_int"
    
    def get_min(self):
        return -32768

    def get_max(self):
        return 32767


class TextFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "text"


class TimeFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider", "end_datetime"]
    provider = "time_object"
    end_datetime = None
    need_timezone = True


class URLFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "url"


class UUIDFieldFaker(FieldFaker):
    faker_class = "factory.Faker"
    faker_kwargs = ["provider"]
    provider = "uuid4"


BASE_FIELD_FAKER_MAP = {
    "BigIntegerField": "factory_generator.fields_faker.BigIntegerFieldFaker",
    "BinaryField": "factory_generator.fields_faker.BinaryFieldFaker",
    "BooleanField": "factory_generator.fields_faker.BooleanFieldFaker",
    "CharField": "factory_generator.fields_faker.CharFieldFaker",
    "ChoiceField": "factory_generator.fields_faker.ChoiceFieldFaker",
    "DateField": "factory_generator.fields_faker.DateFieldFaker",
    "DateTimeField": "factory_generator.fields_faker.DateTimeFieldFaker",
    "DecimalField": "factory_generator.fields_faker.DecimalFieldFaker",
    "DurationField": "factory_generator.fields_faker.DurationFieldFaker",
    "EmailField": "factory_generator.fields_faker.EmailFieldFaker",
    "FileField": "factory_generator.fields_faker.FileFieldFaker",
    "FilePathField": "factory_generator.fields_faker.FilePathFieldFaker",
    "FloatField": "factory_generator.fields_faker.FloatFieldFaker",
    "ForeignKey": "factory_generator.fields_faker.ForeignKeyFaker",
    "ImageField": "factory_generator.fields_faker.ImageFieldFaker",
    "IntegerField": "factory_generator.fields_faker.IntegerFieldFaker",
    "GenericIPAddressField": "factory_generator.fields_faker.GenericIPAddressFieldFaker",
    "ManyToManyField": "factory_generator.fields_faker.ManyToManyFieldFaker",
    "NullBooleanField": "factory_generator.fields_faker.NullBooleanFieldFaker",
    "OneToOneField": "factory_generator.fields_faker.OneToOneFieldFaker",
    "PositiveIntegerField": "factory_generator.fields_faker.PositiveIntegerFieldFaker",
    "PositiveSmallIntegerField": "factory_generator.fields_faker.PositiveSmallIntegerFieldFaker",
    "SlugField": "factory_generator.fields_faker.SlugFieldFaker",
    "SmallIntegerField": "factory_generator.fields_faker.SmallIntegerFieldFaker",
    "TextField": "factory_generator.fields_faker.TextFieldFaker",
    "TimeField": "factory_generator.fields_faker.TimeFieldFaker",
    "URLField": "factory_generator.fields_faker.URLFieldFaker",
    "UUIDField": "factory_generator.fields_faker.UUIDFieldFaker",
}

def get_field_faker_map():
    base_field_faker_map = getattr(settings, 'FACTORY_FIELD_FAKER_MAP', {})
    field_faker_map = BASE_FIELD_FAKER_MAP.copy()
    field_faker_map.update(base_field_faker_map)
    return field_faker_map

FIELD_FAKER_MAP = get_field_faker_map()