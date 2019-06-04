from django import forms


class SaleboxBaseForm(forms.Form):
    redirect = forms.CharField(required=False)
    results = forms.CharField(required=False)
    state = forms.CharField(required=False)


# address
class SaleboxAddressAddForm(SaleboxBaseForm):
    default = forms.BooleanField(required=False)
    address_group = forms.CharField(required=False)
    full_name = forms.CharField(max_length=150)
    address_1 = forms.CharField(max_length=150)
    address_2 = forms.CharField(max_length=150, required=False)
    address_3 = forms.CharField(max_length=150, required=False)
    address_4 = forms.CharField(max_length=150, required=False)
    address_5 = forms.CharField(max_length=150, required=False)
    country_state = forms.IntegerField(required=False)
    country = forms.IntegerField(required=False)
    postcode = forms.CharField(max_length=12, required=False)
    phone_1 = forms.CharField(max_length=20, required=False)
    phone_2 = forms.CharField(max_length=20, required=False)
    email = forms.EmailField(required=False)
    string_1 = forms.CharField(max_length=255, required=False)
    string_2 = forms.CharField(max_length=255, required=False)
    tax_id = forms.CharField(max_length=30, required=False)


class SaleboxAddressIDForm(SaleboxBaseForm):
    id = forms.IntegerField()


# basket
class SaleboxBasketBasketForm(SaleboxBaseForm):
    variant_id = forms.IntegerField()
    quantity = forms.IntegerField()
    relative = forms.BooleanField(required=False)


class SaleboxBasketWishlistForm(SaleboxBaseForm):
    variant_id = forms.IntegerField()
    add = forms.BooleanField(required=False)


class SaleboxBasketMigrateForm(SaleboxBaseForm):
    variant_id = forms.IntegerField()
    to_basket = forms.BooleanField(required=False)


# rating
class SaleboxRatingAddForm(SaleboxBaseForm):
    variant_id = forms.IntegerField()
    rating = forms.IntegerField(min_value=0, max_value=100)


class SaleboxRatingRemoveForm(SaleboxBaseForm):
    variant_id = forms.IntegerField()
