from django.db import models

from django.dispatch import receiver
from django.db.models.signals import  post_delete



class WorkGroup(models.Model):
    group_name = models.CharField(max_length=255, verbose_name="Title", unique=True)
    description = models.TextField(verbose_name="Description", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    def __str__(self):
        return f"{self.group_name}: {self.pk}"
        
class GroupMembers(models.Model):
    MEMBER_TYPE_CHOICES = [
        ("admin", "Admin"),
        ("member", "Member"),
    ]
    member = models.ForeignKey("authentication.User", on_delete=models.CASCADE, blank=True, null=True, verbose_name="User")
    added_to_group = models.ForeignKey(WorkGroup, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Organization")
    role = models.CharField(max_length=255, choices=MEMBER_TYPE_CHOICES, verbose_name="Token Type")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Created Date")

    def __str__(self):
        return f"{self.member}: {self.added_to_group}"
    
@receiver(post_delete, sender=GroupMembers)
def admin_check(sender, instance, **kwargs):
    group= WorkGroup.objects.get(pk=instance.added_to_group_id)
    if not GroupMembers.objects.filter(added_to_group=group, role="admin"):
        group.delete()