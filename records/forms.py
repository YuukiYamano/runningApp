from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone

from .models import RunRecord


class SignUpForm(UserCreationForm):
    """Django 標準の UserCreationForm に Bootstrap のクラスだけ足したもの。"""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ["username"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class LoginForm(AuthenticationForm):
    """ログインフォーム。見た目を揃えるためにクラスを付けるだけ。"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"


class RecordForm(forms.ModelForm):
    """記録の新規登録・編集フォーム。user はここでは受け取らない。"""

    class Meta:
        model = RunRecord
        fields = ["activity_type", "date", "distance_km", "duration_min", "city", "memo"]
        widgets = {
            "activity_type": forms.Select(attrs={"class": "form-select"}),
            "date": forms.DateInput(attrs={"class": "form-control", "type": "date"}, format="%Y-%m-%d"),
            "distance_km": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "duration_min": forms.NumberInput(attrs={"class": "form-control"}),
            "city": forms.TextInput(attrs={"class": "form-control"}),
            "memo": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
        }

    def clean_distance_km(self):
        distance = self.cleaned_data["distance_km"]
        if distance <= 0 or distance > 100:
            raise forms.ValidationError("距離は 0 より大きく 100 以下の値を入力してください。")
        return distance

    def clean_duration_min(self):
        duration = self.cleaned_data["duration_min"]
        if duration < 1 or duration > 1440:
            raise forms.ValidationError("時間は 1 分以上 1440 分以下で入力してください。")
        return duration

    def clean_date(self):
        date = self.cleaned_data["date"]
        if date > timezone.localdate():
            raise forms.ValidationError("未来の日付は入力できません。")
        return date

    def clean_city(self):
        city = self.cleaned_data["city"].strip()
        if not city:
            raise forms.ValidationError("都市名を入力してください。")
        return city

    def clean_memo(self):
        memo = self.cleaned_data["memo"]
        if len(memo) > 1000:
            raise forms.ValidationError("メモは 1000 文字以内で入力してください。")
        return memo
