from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView, ListView, TemplateView

from .forms import SignUpForm
from .models import Profile, RunRecord


class TopView(TemplateView):
    """トップページ。ログイン済みなら記録一覧へ送る。"""

    template_name = "records/top.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect("record_list")
        return super().dispatch(request, *args, **kwargs)


class SignUpView(CreateView):
    """ユーザー登録。登録後は Profile を作り、自動ログインして一覧へ。"""

    form_class = SignUpForm
    template_name = "records/signup.html"
    success_url = reverse_lazy("record_list")

    def form_valid(self, form):
        user = form.save()
        Profile.objects.create(user=user)
        login(self.request, user)
        messages.success(self.request, "アカウントを作成しました。")
        return redirect(self.success_url)


class RecordListView(LoginRequiredMixin, ListView):
    """記録一覧。中身はフェーズ 2 で作る。"""

    model = RunRecord
    template_name = "records/record_list.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        return RunRecord.objects.filter(user=self.request.user)
