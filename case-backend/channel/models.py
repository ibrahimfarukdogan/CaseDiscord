from django.db import models
from group.models import WorkGroup

class DiscordChannel(models.Model):
    TOKEN_TYPE_CHOICES = [
        ("bearer", "Bearer"),
        ("oauth2", "Oauth2"),
        ("id", "ID"),
    ]
    name = models.CharField(max_length=100, verbose_name="Channel Name")
    description = models.TextField(blank=True, null=True, verbose_name="Description")
    discord_id = models.CharField(max_length=255, choices=TOKEN_TYPE_CHOICES, verbose_name="Token Type", default="0")
    added_by_user = models.ForeignKey("authentication.User", on_delete=models.CASCADE, blank=True, null=True, verbose_name="User")
    added_by_group = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Organization")
    token = models.CharField(max_length=500, verbose_name="Token")
    token_type = models.CharField(max_length=255, choices=TOKEN_TYPE_CHOICES, verbose_name="Token Type")
    token_secret = models.CharField(max_length=500, blank=True, null=True, verbose_name="Token Secret")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")
    status = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name}: {self.discord_id}"