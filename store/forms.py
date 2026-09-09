
from django import forms
from .models import Product, SellerApplication


class SellerProductForm(forms.ModelForm):

    class Meta:
        model = Product
        exclude = ['seller']

        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 5
            }),
        }


class SellerApplicationForm(forms.ModelForm):

    class Meta:
        model = SellerApplication

        fields = [
            'full_name',
            'store_name',
            'phone',
            'address',
            'city',
            'state',
            'pincode',
            'seller_type',
            'products_to_sell',
            'description',
        ]

        widgets = {
            'address': forms.Textarea(attrs={
                'rows': 4
            }),

            'description': forms.Textarea(attrs={
                'rows': 5
            }),

            'products_to_sell': forms.TextInput(attrs={
                'placeholder': 'Example: Smartphones, Mobile Accessories'
            }),
        }
class SellerStoreUpdateForm(forms.ModelForm):

    class Meta:
        model = SellerApplication

        fields = [
            'store_name',
            'phone',
            'address',
            'city',
            'state',
            'pincode',
            'products_to_sell',
            'description',
        ]

        widgets = {
            'store_name': forms.TextInput(attrs={
                'placeholder': 'Enter your store name'
            }),

            'phone': forms.TextInput(attrs={
                'placeholder': 'Enter phone number'
            }),

            'address': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Enter store address'
            }),

            'city': forms.TextInput(attrs={
                'placeholder': 'Enter city'
            }),

            'state': forms.TextInput(attrs={
                'placeholder': 'Enter state'
            }),

            'pincode': forms.TextInput(attrs={
                'placeholder': 'Enter pincode'
            }),

            'products_to_sell': forms.TextInput(attrs={
                'placeholder': 'Example: Smartphones, Mobile Accessories'
            }),

            'description': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Tell customers about your store'
            }),
        }