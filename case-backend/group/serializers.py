from rest_framework import serializers
from group.models import WorkGroup, GroupMembers

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model= WorkGroup
        fields=['group_name','created_at','description']
        read_only_fields = ["created_at"]
    
class GroupMemberSerializer(serializers.ModelSerializer):
    class Meta:
        model= GroupMembers
        fields=['member','added_to_group','role','created_at']
        read_only_fields = ['created_at']
    
    def validate_role(self, data):
        CHOICE_DICT = dict(GroupMembers.MEMBER_TYPE_CHOICES)
        print("choice: ", CHOICE_DICT)
        if not (data in CHOICE_DICT):
            raise serializers.ValidationError({"Invalid Choice": f"Choice field is not valid. Valid choices {CHOICE_DICT}"})
        return data
    

class RemoveGroupMemberSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    
class RoleMemberGroupSerializer(serializers.Serializer):
    email = serializers.CharField(required=True)
    role = serializers.CharField(required=True)
    
    def validate_role(self, data):
        CHOICE_DICT = dict(GroupMembers.MEMBER_TYPE_CHOICES)
        print("choice: ", CHOICE_DICT)
        if not (data in CHOICE_DICT):
            raise serializers.ValidationError({"Invalid Choice": f"Choice field is not valid. Valid choices {CHOICE_DICT}"})
        return data


 