from django import forms

class DepositForm(forms.Form):
    amount = forms.DecimalField(
        label='Сумма пополнения (руб.)',
        max_digits=10,
        decimal_places=2,
        min_value=1,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '100'})
    )