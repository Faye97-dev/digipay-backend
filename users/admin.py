from django.contrib import admin
from django import forms
from .models import MyUser, Responsable, Agent, Employee, Agent, Transaction, Transfert, Compensation, Client, ClientDigiPay, Vendor, Notification, TransfertDirect, PreTransaction
from .models import Cagnote, ParticipantsCagnote, TransfertCagnote, GroupPayement, BeneficiaresGrpPayement, SysAdmin, Facturier, ServicesInterFacturier, CreditManager
from api.models import Agence, Commune
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField
from django.core.exceptions import ValidationError

# Register your models here.
admin.site.register(Agence)
admin.site.register(Responsable)
admin.site.register(Employee)
admin.site.register(Agent)
admin.site.register(Commune)
admin.site.register(SysAdmin)

admin.site.register(Transaction)
admin.site.register(Transfert)
admin.site.register(Compensation)

admin.site.register(Client)
admin.site.register(ClientDigiPay)
admin.site.register(Vendor)
admin.site.register(Facturier)
admin.site.register(CreditManager)
admin.site.register(ServicesInterFacturier)

admin.site.register(Notification)
admin.site.register(PreTransaction)
admin.site.register(TransfertDirect)

admin.site.register(Cagnote)
admin.site.register(ParticipantsCagnote)
admin.site.register(TransfertCagnote)

admin.site.register(GroupPayement)
admin.site.register(BeneficiaresGrpPayement)

'''
class UserCreationForm(forms.ModelForm):
    """A form for creating new users. Includes all the required
    fields, plus a repeated password."""
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username', 'first_name',
                  'last_name', 'role', 'date_naissance')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user
'''


class UserChangeForm(forms.ModelForm):
    """A form for updating users. Includes all the fields on
    the user, but replaces the password field with admin's
    disabled password hash display field.
    """
    #password = ReadOnlyPasswordHashField()

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Password confirmation', widget=forms.PasswordInput)

    class Meta:
        model = MyUser
        fields = ('username', 'first_name', 'last_name', 'role',
                  'is_active', 'is_staff', 'date_naissance', 'identifiant', 'compte_banquaire')

    def clean_password2(self):
        # Check that the two password entries match
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):
        # Save the provided password in hashed format
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserAdmin(BaseUserAdmin):
    # The forms to add and change user instances
    form = UserChangeForm
    '''add_form = UserCreationForm'''

    # The fields to be used in displaying the User model.
    # These override the definitions on the base UserAdmin
    # that reference specific fields on auth.User.
    list_display = ('username', 'role', 'is_active', 'is_staff')
    list_filter = ('is_active', 'role')
    fieldsets = (
        (None, {'fields': ('username', 'password1', 'password2')}),
        ('Personal info', {'fields': ('first_name', 'last_name',
                                      'date_naissance', 'identifiant', 'compte_banquaire')}),
        ('Permissions', {
         'fields': ('is_active', 'is_staff', 'role')}),
    )
    # add_fieldsets is not a standard ModelAdmin attribute. UserAdmin
    # overrides get_fieldsets to use this attribute when creating a user.
    '''
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )
    '''
    search_fields = ('username',)
    ordering = ('username',)
    filter_horizontal = ()


# Now register the new UserAdmin...
admin.site.register(MyUser, UserAdmin)
# ... and, since we're not using Django's built-in permissions,
# unregister the Group model from admin.
admin.site.unregister(Group)
