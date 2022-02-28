from django import forms
from django.contrib.auth.models import User

from main.models import Review, Customer, Order


class CustomerRegistrationForm(forms.ModelForm):
    username = forms.CharField(widget=forms.TextInput)
    first_name = forms.CharField(widget=forms.TextInput)
    last_name = forms.CharField(widget=forms.TextInput)
    password1 = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(widget=forms.PasswordInput)
    email = forms.EmailField(widget=forms.EmailInput)

    class Meta:
        model = Customer

        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken.")
        return username

    def clean(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password1')
        if password2 != password1:
            raise forms.ValidationError("The two passwords do not match")
        return super(CustomerRegistrationForm, self).clean()


class CheckoutForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = [ 'address', 'phone']


class CustomerLoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput)
    password = forms.CharField(widget=forms.PasswordInput)


class CommentForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment', 'rate']