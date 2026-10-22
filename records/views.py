import calendar
from decimal import Decimal

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, DetailView, ListView, TemplateView

from .forms import RecordForm, SignUpForm
from .models import Profile, RunRecord, Weather, format_pace
from .weather import GROUP_LABELS, fetch_weather

BAR_MAX_PX = 56  # 月のサマリーの棒の最大の高さ


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


def build_month_summary(user):
    """今月の合計・棒グラフ用の全日分リストを作る。"""
    today = timezone.localdate()
    last_day = calendar.monthrange(today.year, today.month)[1]

    month_records = (
        RunRecord.objects.filter(user=user, date__year=today.year, date__month=today.month)
        .select_related("weather")
        .order_by("created_at")  # 同じ日は最初の記録の天気を使う
    )

    # 日ごとに距離を合計する
    days = {d: {"distance": Decimal("0"), "group": None} for d in range(1, last_day + 1)}
    total_distance = Decimal("0")
    total_duration = 0
    for record in month_records:
        day = days[record.date.day]
        day["distance"] += record.distance_km
        if day["group"] is None:
            day["group"] = record.weather_group
        total_distance += record.distance_km
        total_duration += record.duration_min

    max_distance = max((d["distance"] for d in days.values()), default=Decimal("0"))
    bars = []
    for number, day in days.items():
        if day["distance"] > 0:
            height = max(4, float(day["distance"] / max_distance) * BAR_MAX_PX)
            title = f"{today.month}月{number}日 {day['distance']:.1f}km {GROUP_LABELS[day['group']]}"
        else:
            height = 0
            title = f"{today.month}月{number}日 記録なし"
        bars.append({"day": number, "group": day["group"] or "none", "height": round(height, 1), "title": title})

    hours, minutes = divmod(total_duration, 60)
    return {
        "year": today.year,
        "month": today.month,
        "last_day": last_day,
        "total_distance": total_distance,
        "count": month_records.count(),
        "duration_text": f"{hours}時間{minutes}分" if hours else f"{minutes}分",
        "pace": format_pace(total_duration, total_distance),
        "bars": bars,
    }


class RecordListView(LoginRequiredMixin, ListView):
    """記録一覧（自分の記録のみ）。今月のサマリーつき。"""

    template_name = "records/record_list.html"
    context_object_name = "records"
    paginate_by = 10

    def get_queryset(self):
        return RunRecord.objects.filter(user=self.request.user).select_related("weather")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["summary"] = build_month_summary(self.request.user)
        return context


class RecordDetailView(LoginRequiredMixin, DetailView):
    """記録の詳細。他人の記録は 404 になる。"""

    template_name = "records/record_detail.html"

    def get_queryset(self):
        return RunRecord.objects.filter(user=self.request.user).select_related("weather")


class RecordCreateView(LoginRequiredMixin, CreateView):
    """記録の新規登録。今日の日付なら天気も取得して保存する。"""

    form_class = RecordForm
    template_name = "records/record_form.html"

    def get_initial(self):
        # 都市の初期値はプロフィールの「よく走る都市」
        profile = Profile.objects.filter(user=self.request.user).first()
        return {"activity_type": "run", "city": profile.default_city if profile else ""}

    def form_valid(self, form):
        form.instance.user = self.request.user  # user はフォームから受け取らない
        response = super().form_valid(form)  # 記録を保存する
        messages.success(self.request, "記録しました。")

        # 無料プランは現在の天気しか取れないので、今日の記録だけ取得する
        if self.object.date == timezone.localdate():
            data = fetch_weather(self.object.city)
            if data:
                Weather.objects.create(record=self.object, fetched_at=timezone.now(), **data)
            else:
                messages.warning(self.request, "天気を取得できませんでした。記録は保存されています。")
        return response

    def get_success_url(self):
        return reverse("record_detail", kwargs={"pk": self.object.pk})
