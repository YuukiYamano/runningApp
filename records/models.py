from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone

from .weather import GROUP_LABELS, WEATHER_GROUPS


def format_pace(duration_min, distance_km):
    """1km あたりのペースを 6'08" の形式で返す。距離が 0 なら None。"""
    if not distance_km:
        return None
    total_seconds = duration_min * 60 / float(distance_km)
    return f"{int(total_seconds // 60)}'{int(total_seconds % 60):02d}\""


class Profile(models.Model):
    """ユーザーごとの設定。今は「よく走る都市」だけ。"""

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    default_city = models.CharField("よく走る都市", max_length=100, blank=True)

    def __str__(self):
        return f"{self.user.username} のプロフィール"


class RunRecord(models.Model):
    """ランニング・散歩の 1 件の記録。"""

    ACTIVITY_CHOICES = [("run", "ランニング"), ("walk", "散歩")]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="run_records")
    activity_type = models.CharField("種別", max_length=10, choices=ACTIVITY_CHOICES)
    date = models.DateField("日付", default=timezone.localdate)
    distance_km = models.DecimalField("距離", max_digits=5, decimal_places=2)
    duration_min = models.PositiveIntegerField("時間")
    city = models.CharField("都市", max_length=100)
    memo = models.TextField("メモ", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-date", "-created_at"]

    def __str__(self):
        return f"{self.date} {self.get_activity_type_display()} {self.distance_km}km"

    @property
    def pace(self):
        """1km あたりのペース。距離が 0 なら None。"""
        return format_pace(self.duration_min, self.distance_km)

    @property
    def weather_group(self):
        """天気の色グループ。天気がない記録は "none"。"""
        return self.weather.group if hasattr(self, "weather") else "none"


class Weather(models.Model):
    """記録した日の天気。記録 1 件につき 0 件または 1 件。"""

    record = models.OneToOneField(RunRecord, on_delete=models.CASCADE, related_name="weather")
    main = models.CharField(max_length=50)
    description = models.CharField(max_length=100)
    icon = models.CharField(max_length=10)
    temp = models.DecimalField(max_digits=4, decimal_places=1)
    humidity = models.IntegerField()
    wind_speed = models.DecimalField(max_digits=4, decimal_places=1)
    fetched_at = models.DateTimeField()

    def __str__(self):
        return f"{self.record_id} の天気: {self.main}"

    @property
    def group(self):
        """clear / cloud / rain のどれか。"""
        return WEATHER_GROUPS.get(self.main, "cloud")

    @property
    def group_label(self):
        return GROUP_LABELS[self.group]
