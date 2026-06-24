# apps/accounts/forms.py
import re
from django import forms
from django.contrib.auth.password_validation import validate_password
from .models import User
from .constants import UGANDA_DISTRICT_CHOICES, SPECIALIZATION_CHOICES


class RegisterForm(forms.Form):
    """
    Full registration form with server-side validation.
    Validates Uganda phone numbers, password strength, and uniqueness.
    """
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'}),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
    )
    phone = forms.CharField(
        max_length=15, required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+256700000000'}),
    )
    user_type = forms.ChoiceField(
        choices=User.USER_TYPES,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    location = forms.ChoiceField(
        choices=[('', '— Select District —')] + [
            (district, district)
            for region, districts in [
                ('Central', ['Buikwe', 'Bukomansimbi', 'Buvuma', 'Gomba', 'Kalangala', 'Kalungu', 'Kampala', 'Kayunga', 'Kiboga', 'Kyankwanzi', 'Luweero', 'Lwengo', 'Lyantonde', 'Masaka', 'Mityana', 'Mpigi', 'Mubende', 'Mukono', 'Nakaseke', 'Nakasongola', 'Rakai', 'Sembabule', 'Wakiso']),
                ('Eastern', ['Amuria', 'Budaka', 'Bududa', 'Bugiri', 'Bugweri', 'Bukedea', 'Bukwa', 'Bulambuli', 'Busia', 'Buyende', 'Iganga', 'Jinja', 'Kaberamaido', 'Kaliro', 'Kamuli', 'Kapchorwa', 'Katakwi', 'Kibuku', 'Kumi', 'Kween', 'Luuka', 'Manafwa', 'Mayuge', 'Mbale', 'Namayingo', 'Namisindwa', 'Namutumba', 'Ngora', 'Pallisa', 'Serere', 'Sironko', 'Soroti', 'Tororo']),
                ('Northern', ['Abim', 'Adjumani', 'Agago', 'Alebtong', 'Amolatar', 'Amudat', 'Amuru', 'Apac', 'Arua', 'Dokolo', 'Gulu', 'Kaabong', 'Kitgum', 'Koboko', 'Kole', 'Kotido', 'Kwania', 'Lamwo', 'Lira', 'Maracha', 'Moroto', 'Moyo', 'Madi-Okollo', 'Nakapiripirit', 'Napak', 'Nebbi', 'Nwoya', 'Obongi', 'Omoro', 'Otuke', 'Oyam', 'Pader', 'Pakwach', 'Terego', 'Yumbe', 'Zombo']),
                ('Western', ['Buhweju', 'Buliisa', 'Bundibugyo', 'Bushenyi', 'Hoima', 'Ibanda', 'Isingiro', 'Kabale', 'Kabarole', 'Kagadi', 'Kakumiro', 'Kamwenge', 'Kanungu', 'Kasese', 'Kibaale', 'Kikuube', 'Kiruhura', 'Kiryandongo', 'Kisoro', 'Kitagwenda', 'Kyegegwa', 'Kyenjojo', 'Masindi', 'Mbarara', 'Mitooma', 'Ntoroko', 'Ntungamo', 'Rubanda', 'Rubirizi', 'Rukiga', 'Rukungiri', 'Sheema', 'Rwampara']),
            ]
            for district in districts
        ],
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create a strong password'}),
    )
    password2 = forms.CharField(
        label='Confirm password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repeat password'}),
    )

    # Farmer-specific (optional)
    farm_name = forms.CharField(
        max_length=200, required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your farm name'}),
    )
    farm_size = forms.DecimalField(
        min_value=0, required=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Size in acres'}),
    )
    specialization = forms.ChoiceField(
        choices=[('', '— Select Specialization (optional) —')] + SPECIALIZATION_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exists():
            raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        # Accept Uganda formats: +256XXXXXXXXX, 0XXXXXXXXX, 256XXXXXXXXX
        cleaned = re.sub(r'[\s\-()]', '', phone)
        if not re.match(r'^(\+256|256|0)[3-9]\d{8}$', cleaned):
            raise forms.ValidationError(
                'Enter a valid Uganda phone number (e.g. +256700123456 or 0700123456).'
            )
        return cleaned

    def clean_password(self):
        password = self.cleaned_data.get('password', '')
        # Use Django's built-in validators (MinLength, Common, Numeric)
        validate_password(password)
        return password

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            self.add_error('password2', 'Passwords do not match.')
        return cleaned_data


class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            'username', 'email', 'user_type', 'phone',
            'whatsapp_number', 'district', 'specialization',
            'address', 'profile_picture',
        ]
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'whatsapp_number': forms.TextInput(attrs={'class': 'form-control'}),
            'district': forms.Select(attrs={'class': 'form-control'}),
            'specialization': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control-file'}),
        }