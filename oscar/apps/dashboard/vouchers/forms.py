from django import forms
from django.db.models.loading import get_model
from django.utils.translation import ugettext_lazy as _

Voucher = get_model('voucher', 'Voucher')
Benefit = get_model('offer', 'Benefit')
Range = get_model('offer', 'Range')


class VoucherForm(forms.Form):
    """
    A specialised form for creating a voucher and offer
    model.
    """
    name = forms.CharField(label=_("Name"))
    code = forms.CharField(label=_("Code"))
    start_date = forms.DateField(label=_("Start date"))
    end_date = forms.DateField(label=_("End date"))
    usage = forms.ChoiceField(choices=Voucher.USAGE_CHOICES)

    benefit_range = forms.ModelChoiceField(
        label=_('Which products get a discount?'),
        queryset=Range.objects.all(),
    )
    type_choices = (
        (Benefit.PERCENTAGE, _('% off products in range')),
        (Benefit.FIXED, _('Fixed amount off products in range')),
    )
    benefit_type = forms.ChoiceField(
        choices=type_choices,
        label=_('Discount type'),
    )
    benefit_value = forms.DecimalField(
        label=_('Discount value'))

    def __init__(self, voucher=None, *args, **kwargs):
        self.voucher = voucher
        super(VoucherForm, self).__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data['code'].strip().upper()
        if not code:
            raise forms.ValidationError(_("Please enter a voucher code"))
        try:
            voucher = Voucher.objects.get(code=code)
        except Voucher.DoesNotExist:
            pass
        else:
            if voucher.id != self.voucher.id:
                raise forms.ValidationError(_("The code '%s' is already in use") % code)
        return code

    def clean(self):
        cleaned_data = super(VoucherForm, self).clean()
        start_date = cleaned_data['start_date']
        end_date = cleaned_data['end_date']
        if end_date < start_date:
            raise forms.ValidationError(_("The start date must be before the end date"))
        return cleaned_data


class VoucherSearchForm(forms.Form):
    name = forms.CharField(required=False)
    code = forms.CharField(required=False)
    is_active = forms.BooleanField(required=False)

    def clean_code(self):
        return self.cleaned_data['code'].upper()
