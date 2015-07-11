GaeForms
============

Project to automate form validation and normalization on Google App Engine in a Django Forms fashion.

It can be installed from pypi:

```
   pip install gaeforms
```

# How to Use

You can use the project to validate generic forms or those related to NDB Models.
Let's see the first approach.

## Approach 1: Form Class

To validate data you need inherit from Form class.
For this class you must create attributes that you want validate and normalize:

```pyton
class UserForm(Form):
    name = StringField(required=True)
    age = IntegerField()
```

After creating the UserForm class you can use it to instantiate objects representing the form.
You can fill form properties on initialization. Each property can be accessed through its name.

**normalize** method is used to transform the values received from requests as string into its respective model values.

**validate** method is used to validate the values:


```python
>>> from example import UserForm
>>> form = UserForm(name='Joe', age='2')
>>> form.normalize()
{'age': 2, 'name': 'Joe'}
>>> form.localize(name='Foo', age=5)
{'age': u'5', 'name': 'Foo'}
>>> form.name
'Foo'
>>> form.age
u'5'
>>> form.normalize()
{'age': 5, 'name': 'Foo'}
>>> form.validate()
{}
>>> form.name=''
>>> form.validate()
{'name': u'Required field'}
>>> form.age=''
>>> form.normalize()
{'age': None, 'name': ''}
>>> form.validate()
{'name': u'Required field'}
>>> form.age='invalid integer'
>>> form.validate()
{'age': u'Must be integer', 'name': u'Required field'}
```

This can be used to transform and validate any king of data, mainly those not related to a specif Model.
In case of existent Model, the second approach bellow can be used

## Approach 2: Model Based Form

Let's say you already have a model class user as bellow:

```python
class User(Model):
    name = StringProperty(required=True)
    age = IntegerProperty()
```

You could use the **UserForm** from approach 1 to validate and normalize data to this model.
Besides that it would be a boring work rewriting the properties which are already defined on model.
To avoid this work you can inhiret from ModelForm.
You need specify the target model class on attributte **_model_class** as bello:

```python
class UserForm(ModelForm):
    _model_class = User
```
This way you can use the form to validate and transform data from form into model properties and vice versa:

```python
>>> from example import UserForm
>>> form = UserForm(name='Joe', age='2')
>>> form.normalize()
{'age': 2, 'name': 'Joe'}
>>> form.fill_model()
User(age=2, name='Joe')
>>> new_form = UserForm(name=None, age='invalid integer')
>>> new_form.validate()
{'age': u'Must be integer', 'name': u'Required field'}
>>> new_form.fill_with_model(user)
{'age': u'2', 'name': 'Joe'}
>>> new_form.validate()
{}
```

These two approchs give you a clean way to validate your data.
Let's see the already existing Fields on next section:

# Existing Fields

There are some existing Filds on lib to help on the tedious work of validating standart date.
All of then come with interesting options:

* required: If True the field will raise error if the value is None or empty string.
* default: If value to be used as default in case the respective value is None or empty string
* repeated: If True it indicates that the property has a list of values instead of a simple property
* choices: If a list of defined values is provided, values not inside this list are not allowed

Some fields have more interesting values, as you can see bellow:

## StringField

Field to validate and transform strings. It is used in ModelForm if a StringProperty is defined on Model.

Options:

* max_len: maximum number of charaters allowed. Default is 1500 so it matchs with ndb [StringProperty limit](https://cloud.google.com/appengine/docs/python/ndb/properties). A value of none indicates no restrictions towards the max size of string.
* exactly_len: exactly number of characters the string must contain. Default is None indication no restriction.
* min_len: minumum number of characters the string must contain. Default is None indication no restriction.

## EmailField

Field to validate and transform emails. It has the same option as StringField

## KeyField

Field to validate and transform ndb [Keys](https://cloud.google.com/appengine/docs/python/ndb/entities#entity_keys).
Options: kind indicating the related model class. If present, de default transformation use it and the string as an integer id.
If not possible or kind is None, it try using **urlsafe** to make the conversion

## IntegerField

Field to validate and transform Integers. It is respective to IntegerProperty from ndb.
Options:

* lower: the minimum accepted value for the property. Default is None which does not perform validation.
* upper: the maximum accepted value for the property. Default is None which does not perform validation

## BooleanField

Field to validate and transform Booleans values. It is respective to BooleanProperty from ndb.

## FloatField

Field to validate and transform Float values. It is respective to FloatProperty from ndb.
Options:

* lower: the minimum accepted value for the property. Default is None which does not perform validation.
* upper: the maximum accepted value for the property. Default is None which does not perform validation

## DecimalField

Field to validate and transform Decimal values.
It saves the number as a Integer in database, considering the number of decimal places.
On model the attributte is a instance of Decimal class.
It is respective to SimpleDecimal and SimpleCurrency, both extended properties from  property package which will be explained.
Options:

* lower: the minimum accepted value for the property. Default is None which does not perform validation.
* upper: the maximum accepted value for the property. Default is None which does not perform validation.
* decimal_places: indicate the number of decimal places on property. Default is 2.

## DateField

Field to validate and transform date values. In en_US it transforms the string of type dd/mm/yyyy.

## DateTimeField

Field to validate and transform datetime values. In en_US it transforms the string of type dd/mm/yyyy HH:MM:SS.

Those are the common fields. But once some ndb Properties can be extended, some new are created as you can see on next section.

## CepField

Field to validate and transform Brazilian postal codes. It transforms the string of type 12345-678 to 12345678

## CpfField

Field to validate and transform Brazilian personal document identifier. It transforms the string of type 067.687.258-15 to 06768725815 and validates the check digits.

## Cnpj

Property used to define Brazilian companies by the Secretariat of the Federal Revenue of Brazil. It transforms the string of type "69.435.154/0001-02" to 69435154000102 and validates it.

# Extended ndb Properties

Somo default ndb properties does have the same option as fields.
As a example, the IntegerProperty does not have a **lower** nor **upper** options.
Because of this lack of functionalities, the following properties were created on package property:

## StringBounded

This property can be used as substitute of StringProperty. It differs from the original one by the following extra options:

* exactly_len: indicate the exactly length the property must have. Default is None indication no validation.
* min_len: indicate the minimun length the property must have. Default is None indication no validation.
* max_len: indicate the maximum length the property must have. Default is the maximum len allowed on db, currently 1500 indication no validation. None indicates no validation. Usefull when using indexex=False.

## Email

This property is used to distinguish from ordinary String property.
When used, the form will validate the field as an email, using EmailField.

## IntegerBounded

This property can be used as substitute of IntegerProperty. It differs from the original one by the following extra options:

* upper: indicate the maximum allowed value.
* lower: indicate the minimum allowed value.

## FloatBounded

This property can be used as substitute of FloatProperty. It differs from the original one by the following extra options:

* upper: indicate the maximum allowed value.
* lower: indicate the minimum allowed value.

## SimpleDecimal

Property used to describe decimal values with precise decimal places.
On model the attribute is a Decimal instance.
On database it is stored as a integer disregarding the dot, e.g, 1.00 is stored as 100.
Options

* upper: indicate the maximum allowed value.
* lower: indicate the minimum allowed value.
* decimal_places: indicate the precision of decimal. Default is 2.

## SimpleCurrency

Property used to define currency values. It inherits from SimpleDecimal.
The only difference is that **lower** default value is 0 instead of None, e.g. it does not allow negative values.

## Cep

Property used to define Brazilian postal code. It inherits from String. It inherits from String and validate the field as an Cep using CepField.

## Cpf

Property used to define Brazilian personal document identifier. It inherits from String and validate the field as an Cpf using CpfField.

## Cnpj

Property used to define Brazilian companies by the Secretariat of the Federal Revenue of Brazil. It inherits from String and validate the field as an Cnpj using CnpjField.

#Extending Fields - Implementing a field for Brazilian postal code

With these properties and fields it is possible enhance your system validation.
Besides that there are cases in which you would like create your own custom fields.
Let's see how to do it!

## Step 1 - Unit Tests

To show you how extend a Field let's implement a example.
We are going to build a field to validate Brazilian postal code.
It's content is formed by exactly eight numbers.
There can be a hyphen on fifth position.
Bellow you can see the unit tests for it:

```python
class CepFieldTests(unittest.TestCase):
    def test_normalization(self):
        field = CepField()
        self.assertIsNone(field.normalize(''))
        self.assertIsNone(field.normalize(None))
        self.assertEqual('12345678', field.normalize('12345-678'))
        self.assertEqual('12345678', field.normalize('12345678'))

    def test_localization(self):
        field = CepField()
        self.assertEqual('', field.localize(''))
        self.assertEqual('', field.localize(None))
        self.assertEqual('12345-678', field.localize('12345678'))

    def test_validate(self):
        field = CepField()
        field._set_attr_name('d')
        self.assertIsNone(field.validate('12345678'))
        self.assertIsNone(field.validate('12345-678'))
        self.assertIsNone(field.validate('1234567-8'))
        self.assertEqual('CEP must have exactly 8 characters', field.validate('1234567'))
        self.assertEqual('CEP must have exactly 8 characters', field.validate('123456789'))
        self.assertEqual('CEP must contain only numbers', field.validate('1234567a'))
```

## Step 2 - Inheriting from a BaseField or another Existing Field

Your custom field must inherit from BaseField or another Field class as bellow:

```python
from webapp2_extras.i18n import gettext as _


class CepField(BaseField):
    def valiate_field(self, value):
        if value:
            value = self.normalize_field(value)
            if len(value) != 8:
                return _('CEP must have exactly 8 characters')
            try:
                int(value)
            except:
                return _('CEP must contain only numbers')
        return super(CepField, self).validate_field(value)

    def normalize_field(self, value):
        if value:
            return value.replace('-', '')
        elif value == '':
            value = None
        return super(CepField, self).normalize_field(value)


    def localize_field(self, value):
        if value:
            return '%s-%s' % (value[:5], value[5:])
        return super(CepField, self).localize_field(value)
```

There are three important methods which must be overridden and we are going to see them on next subsections.

## Step 3: Override **normalize_field**

To implement the field we need to override **normalize_field**.
This method receive a string, the commom format from a web request, and must transform in a respective database value.
We want to save a string with only its characaters, e.g, without hyphen.
So the overriden method is bellow:

```python
    def normalize_field(self, value):
        if value:
            return value.replace('-', '')
        elif value == '':
            value = None
        return super(CepField, self).normalize_field(value)
```

Note that on last the method from super class is executed, so it can handle some other commom cases of normalization.
One example is using default value if it is provided.

## Step 4: Override **localize_field**

Another method that need be overridde is **localize_field**.
It receives need receive a value from db and transform it in a string.
It does the exactly opposite of **normalize_field**.
This value is commonly presented to final user and must be formatted accordingly.
So the hyphen was inserted on sixth position:

```python
def localize_field(self, value):
        if value:
            return '%s-%s' % (value[:5], value[5:])
        return super(CepField, self).localize_field(value)
```

Note that on last line the parent **localize_field** method was called.
This way the method can handle another commom cases, e.g,, transforming None value on empty string.

## Step 5: Override **validate_field**

Another method that need be overridde is **validate_field**.
It receives a string value and must perform validation.
A string containing the error message must be returned if there is error.
So this was the result:

```python
    def valiate_field(self, value):
        if value:
            value = self.normalize_field(value)
            if len(value) != 8:
                return _('CEP must have exactly 8 characters')
            try:
                int(value)
            except:
                return _('CEP must contain only numbers')
        return super(CepField, self).validate_field(value)
```

As on previous methods, the last line execute the respective parent method.
This way the field validate some other common cases such as not allowing empty string if the field is required.

Another important thing is realize that the internationalization function is been used to return the message.
Thus the error messages can be translated to another languages, as we are going to see on Internationalization section.

The steps here are enough to create a new field. But let's see how to link the field to a database value.

# Linking Fields with Database Properties

The existing default ndb properties are very simple covering only some kind of validations.
But the framework allow Property extensions and it can be combined with Fields from gae forms.
The subsection bellow show hos to do it.

## Step 1: Extending a Property

The ndb ORM, initially written by Guido Van Rossum, allow Property extension as described in its [documentation](https://cloud.google.com/appengine/docs/python/ndb/subclassprop).
So the class CepProperty is created to represent a Brazilian postal code with its validation.
It must inherits from the target database class, StringProperty in this case.
The **_validate** method is overriden accordingly to CEP rules:

```python
class CepProperty(StringProperty):
    """
    Class related with Brazilian postal code (CEP)
    """
    def _validate(self, value):
        if len(value) != 8:
            raise BoundaryError('%s should have exactly 8 characters' % value)
```

The validation is done on property again so people using only the property, and not the form validation, can still have their data consistent.

## Step 2: Connecting Property with a Field

Once we have CepProperty and CepField, it is desirable that models containing the properties can use the field and performing a form validation.
So the function registry is used as bellow:

```python
from gaeforms.country.br.field import CepField
from gaeforms.ndb.form import registry


class CepProperty(StringProperty):
    """
    Class related with Brazilian postal code (CEP)
    """

    def _validate(self, value):
        if len(value) != 8:
            raise BoundaryError('%s should have exactly 8 characters' % value)


registry(CepProperty, CepField)
```

Once this is done, you can use your custom property to build models and form:

```python
class Address(Model):
    cep = CepProperty(required=True)


class AddressForm(ModelForm):
    _model_class = Address
```

After model creation, you can use it to perform data validation and normalization:

```python
>>> form = AddressForm(cep='12345-678')
>>> form.fill_model()
Address(cep=u'12345678')
>>> form.cep = '123456789'
>>> form.validate()
{'cep': u'CEP must have exactly 8 characters'}
>>> form.cep = '1234567a'
>>> form.validate()
{'cep': u'CEP must contain only numbers'}
>>> form.localize(cep='12345678')
{'cep': u'12345-678'}
```

# Validating compound fields

Sometimes the validation is not related with only one field, there can be dependency between different fields.
To perform this kind of validation you can override validate method from Form or ModelForm.
As an example, let's say our previous Address has a boolean field indicating if cep must be present or not.
We could change the classes as follows:

```python
class Address(Model):
    cep_declared = BooleanProperty(default=False)
    cep = CepProperty()


class AddressForm(ModelForm):
    _model_class = Address

    def validate(self):
        errors = super(AddressForm, self).validate()
        normalized_dct = self.normalize()
        if normalized_dct['cep_declared'] == True and not self.cep:
            errors['cep'] = 'If CEP is declared it should not be empty'
        return errors
```

Once the form is changed it can handle the custom validation:

```python
>>> form = AddressForm(cep_declared=False, cep='')
>>> form.validate()
{}
>>> form.cep_declared = True
>>> form.validate()
{u'cep': u'If CEP is declared it should not be empty'}
>>> form.cep_declared = False
>>> form.fill_model()
Address(cep=None, cep_declared=False)
```

So now you can validate your data on Google App Engine like a boss ;)