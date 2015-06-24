gaeforms
============

Project to automate form validation and normalization on Google App Engine in a Django Forms fashion.

It can be installed from pypi:

```
   pip install gaeforms
```

# How t Use

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

# Existing 

There are some existing Filds on lib to help on the tedious work of validating standart date.
All of then come with interesting options:

* required: If True the field will raise error if the value is None or empty string.
* default: If value to be used as default in case the respective value is None or empty string
* repeated: If True it indicates that the property has a list of values instead of a simple property
* choices: If a list of defined values is provided, values not inside this list are not allowed

Some fields have more interesting values, as you can see bellow:
* max_len: maximum number of charaters allowed. Default is 1500 so it matchs with ndb [StringProperty limit](https://cloud.google.com/appengine/docs/python/ndb/properties). A value of none indicates no restrictions towards the max size of string.
* exactly_len: exactly number of characters the string must contain. Default is None indication no restriction.
* min_len: minumum number of characters the string must contain. Default is None indication no restriction.

## StringField

Field to validate and transform strings. Options:
* 