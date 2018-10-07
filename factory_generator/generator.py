import os

from django.conf import settings
from django.template.loader import render_to_string

from factory_generator import VERSION
from factory_generator.fields_faker import FIELD_FAKER_MAP
from factory_generator.utils import import_from_string

NORMALIZE_FIELD_MAP = getattr(settings, 'FACTORY_NORMALIZE_FIELD_MAP', {})


IGNORE_FIELDS = [
    'ManyToOneRel',
    'ManyToManyRel',
    'OneToOneRel',
    'AutoField',
    'BigAutoField'
] + getattr(settings, 'FACTORY_IGNORE_FIELDS', [])


class FactoryFieldGenerator:

    """
    Given a `field` and a `model` this class generates
    the proper corresponding factory property
    """

    def __init__(self, field, model):
        self.field = field
        self.model = model
        self.root_dir = getattr(settings, 'FACTORY_ROOT_DIR', 'model_factories')
        super(FactoryFieldGenerator, self).__init__()

    @property
    def is_ignored(self):
        """
        Return `True` if the the field should be ignored to not appear in the factory class
        """
        if self.field_class in IGNORE_FIELDS:
            return True
        if not self.field.editable and getattr(settings, 'FACTORY_IGNORE_NON_EDITABLE_FIELDS', True):
            return True
        return False

    @property
    def field_faker_string(self):
        return FIELD_FAKER_MAP[self.field_class]

    @property
    def field_faker_class(self):
        return import_from_string(self.field_faker_string)

    @property
    def need_timezone(self):
        """
        Return `True` if the current field is one of 
        `DateTimeField`, `TimeField`, `DateField` or `DurationField' types
        And so need to import `pytz` for the factory
        """
        return self.field_faker_class.need_timezone

    @property
    def has_choices(self):
        """
        Return `True` if the field has a `choices` attribute
        """
        return hasattr(self.field, 'choices') and len(self.field.choices) > 0

    @property
    def field_class(self):
        """
        Get the class of the field and normalize it to
        match a native Django model field class
        """
        if self.has_choices:
            return 'ChoiceField'
        class_name = self.field.__class__.__name__
        if class_name in NORMALIZE_FIELD_MAP:
            return NORMALIZE_FIELD_MAP[class_name]
        return class_name

    @property
    def base_context(self):
        """
        Return the context to render the base factory class
        """
        res = {
            'field': self.field,
            'model_name': self.model.__name__
        }
        return res

    def render_choices_list(self):
        """
        For a field that has a `choices` attribute
        render the list of choices
        """
        return render_to_string('factory_generator/choiceslist.py-tpl', self.base_context)

    def render(self):
        """
        Render the appropriate template to get the field definition
        """
        faker = self.field_faker_class(self.model, self.field)
        return faker.render()


class PathMixin:

    """
    Mixin to compute path with the following structure :
    - root_directory_path:
        - root_init_file_path
        - app_directory_path:
            - app_init_file_path
            - app_base_directory_path:
                - app_base_init_file_path
    """

    def __init__(self):
        """
        Set the `root_dir` with the `FACTORY_DIR` settings or default
        to `model_factories`
        """
        self.root_dir = getattr(settings, 'FACTORY_ROOT_DIR', 'model_factories')
        super(PathMixin, self).__init__()

    @property
    def root_directory_path(self):
        """
        Return the root ./ directory full path
        """
        return os.path.join(settings.BASE_DIR, self.root_dir)

    @property
    def root_init_file_path(self):
        """
        Return the root ./__init__.py file full path
        """
        return os.path.join(self.root_directory_path, '__init__.py')

    @property
    def app_directory_path(self):
        """
        Return the ./app/ directory full path
        """
        return os.path.join(self.root_directory_path, self.app_label)

    @property
    def app_init_file_path(self):
        """
        Return the ./app/__init__.py file full path
        """
        return os.path.join(self.app_directory_path, '__init__.py')

    @property
    def app_base_directory_path(self):
        """
        Return the ./app/base/ directory full path
        """
        return os.path.join(self.root_directory_path, self.app_label, 'base')

    @property
    def app_base_init_file_path(self):
        """
        Return the ./app/base/__init__.py file full path
        """
        return os.path.join(self.app_base_directory_path, '__init__.py')


class FactoryModelGenerator(PathMixin):

    """
    Given a model `MyModel` in the app `app`, this class can generate files to 
    define factory classes:
    - model_factories/app/mymodel.py defining MyModelFactoryBase
    - model_factories/app/base/mymodel.py defining MyModelFactory
    - model_factories/app/base/__init__.py

    MyModelFactory is a subclass of MyModelFactoryBase so that
    generated code can easily be overrided
    """

    def __init__(self, model):
        self.model = model
        self.app_label = model._meta.app_label  # needed for PathMixin
        self.model_filename = "{filename}.py".format(
            filename=self.model.__name__.lower())
        super(FactoryModelGenerator, self).__init__()

    @property
    def fields(self):
        """
        Return the list of fields for the given model
        """
        return [f for f in self.model._meta.get_fields()]

    @property
    def factory_name(self):
        """
        Return the class name for `[Model]Factory`
        """
        return "{model_name}Factory".format(model_name=self.model.__name__)

    @property
    def factory_base_name(self):
        """
        Return the class name for `[Model]FactoryBase`
        """
        return "{factory_name}Base".format(factory_name=self.factory_name)

    @property
    def context_init(self):
        """
        Get the context needed for the definition of the `__init__.py` file
        """
        module_path = "{root_dir}.{app_label}.{model_lower}".format(
            root_dir=self.root_dir,
            app_label=self.model._meta.app_label,
            model_lower=self.model.__name__.lower()
        )
        return {
            'module': module_path,
            'factory': self.factory_name
        }

    @property
    def context_base(self):
        """
        Get the context needed for the definition of the `[Model]FactoryBase` class
        """
        res = {
            'model_name': self.model.__name__,
            'model_module': self.model.__module__,
            'factory_name': self.factory_name,
            'factory_base_name': self.factory_base_name,
            'need_timezone': False,
            'version': VERSION,
            'fields': [],
            'choices': [],
            'unique': [],
            'unique_kwargs': ''
        }
        for field in self.fields:
            factory = FactoryFieldGenerator(field, self.model)
            if factory.is_ignored:
                continue
            if hasattr(field, 'unique') and field.unique:
                res['unique'].append(field.name)
            if factory.has_choices:
                res['choices'].append(factory.render_choices_list())
            if factory.need_timezone:
                res['need_timezone'] = True
            res['fields'].append(factory)
            if res['unique']:
                res['unique_kwargs'] = ', '.join(
                    '%r' % key for key in res['unique']) + ','
        return res

    @property
    def context(self):
        """
        Get the context needed for the definition of the `[Model]Factory` class
        """
        factory_module_path = "{root_dir}.{app_label}.base.{model_lower}".format(
            root_dir=self.root_dir,
            app_label=self.model._meta.app_label,
            model_lower=self.model.__name__.lower()
        )
        res = {
            'model_name': self.model.__name__,
            'factory_module': factory_module_path,
            'factory_name': self.factory_name,
            'factory_base_name': self.factory_base_name,
            'version': VERSION
        }
        return res

    def bootstrap_root_dir(self):
        """
        Create the directory defined in `FACTORY_DIR` (default to model_factories)
        And create and empty `__init__.py` file to make this directory a python module
        """
        if not os.path.exists(self.root_directory_path):
            os.makedirs(self.root_directory_path)
            open(self.root_init_file_path, 'a').close()

    def bootstrap_app_dirs(self):
        """
        Create the following directories and files for the app of the current model:
        - app_directory_path:
            - app_base_directory_path:
                - app_base_init_file_path
        """
        if not os.path.exists(self.app_directory_path):
            os.makedirs(self.app_directory_path)
        if not os.path.exists(self.app_base_directory_path):
            os.makedirs(self.app_base_directory_path)
            open(self.app_base_init_file_path, 'a').close()

    @property
    def render_base(self):
        """
        Get the definition of the `[Model]FactoryBase` class
        """
        return render_to_string('factory_generator/base-factory.py-tpl', self.context_base)

    @property
    def render(self):
        """
        Get the definition of the `[Model]Factory` class
        """
        return render_to_string('factory_generator/factory.py-tpl', self.context)

    @property
    def app_base_factory_file_path(self):
        """
        Return the factory file path, eg:
        - model_factories/app/base/model.py
        """
        return os.path.join(self.app_base_directory_path, self.model_filename)

    @property
    def app_factory_file_path(self):
        """
        Return the factory file path, eg:
        - model_factories/app/model.py
        """
        return os.path.join(self.app_directory_path, self.model_filename)

    def create_base_factory_file(self):
        """
        Create the file containing the `[Model]FactoryBase` class at the following path
        - model_factories/app/base/model.py
        """
        with open(self.app_base_factory_file_path, 'w', encoding='utf-8') as base_factory_file:
            base_factory_file.write(self.render_base)

    def create_factory_file(self):
        """
        Create the file containing the `[Model]Factory` class at the following path
        - model_factories/app/model.py
        """
        if not os.path.exists(self.app_factory_file_path):
            with open(self.app_factory_file_path, 'w', encoding='utf-8') as factory_file:
                factory_file.write(self.render)

    def create_files(self):
        """
        Create factories files and directories for the given model
        """
        self.bootstrap_root_dir()
        self.bootstrap_app_dirs()
        self.create_base_factory_file()
        self.create_factory_file()


class FactoryAppGenerator(PathMixin):

    """
    Generate factories for each model for the given app
    And once all factories for this app are generated, create
    the `__init__.py` file which import all factories
    """

    def __init__(self, app):
        self.app = app
        self.app_label = app.label  # needed for PathMixin
        super(FactoryAppGenerator, self).__init__()

    def render_init_file(self, context):
        """
        Render the content of `__init__.py` file which imports all factories
        """
        return render_to_string('factory_generator/app-init.py-tpl', context)

    def create_init_file(self, imports):
        """
        Create or override the file `__init__.py` which imports all factories
        """
        if imports:
            with open(self.app_init_file_path, 'w', encoding='utf-8') as init_file:
                init_file.write(self.render_init_file({
                    'imports': imports,
                    'version': VERSION,
                }))

    def create_files(self):
        """
        Generate factories for each model in the app defined in `self.app`
        And once all factories for this app are generated, create
        the `__init__.py` file which import all factories
        """
        imports = []
        created_files = []
        for model in self.app.get_models():
            factory_model_generator = FactoryModelGenerator(model)
            factory_model_generator.create_files()
            imports.append(factory_model_generator.context_init)
            created_files.append(factory_model_generator.app_factory_file_path)
        self.create_init_file(imports)
        return created_files
