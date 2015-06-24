gaeforms
============

Project to automate form validation and normalization on Google App Engine in a Django Forms fashion.

It can be installed from pypi:

```
   pip install gaeforms
```

# How t Use

You can use the project to validate generic forms or those related to NDB Models.
Lets see the first approach.

## Form Class

To validate data you need inherit from Form class. 
For this class you must create attributes that you want validate and normalize:

```python
class UserForm(Form):
    name = StringField(required=True)
    age = IntegerField()
```

After creating the UserForm class you can use it to instantiate objects representing the form.
You can fill form properties on initialization. Each property can be accessed through its name.

normalize method is used to transform the values received from requests as string into its respective model values.
 
validate method is used to validate the values:


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

