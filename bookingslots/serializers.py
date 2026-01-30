from rest_framework import serializers
from .models import BookingSlot, Booking

class BookingSlotSerializer(serializers.ModelSerializer):
    is_available = serializers.ReadOnlyField()
    
    class Meta:
        model = BookingSlot
        fields = ['id', 'title', 'description', 'start_time', 'end_time', 
                 'max_bookings', 'current_bookings', 'status', 'is_available', 
                 'created_at', 'updated_at']
        read_only_fields = ['id', 'current_bookings', 'created_at', 'updated_at']

class BookingSerializer(serializers.ModelSerializer):
    slot_title = serializers.CharField(source='slot.title', read_only=True)
    slot_date = serializers.DateTimeField(source='slot.start_time', read_only=True)
    
    class Meta:
        model = Booking
        fields = ['id', 'slot', 'slot_title', 'slot_date', 'customer_name', 
                 'customer_email', 'customer_phone', 'customer_notes', 
                 'status', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

class BookingCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Booking
        fields = ['slot', 'customer_name', 'customer_email', 'customer_phone', 'customer_notes']