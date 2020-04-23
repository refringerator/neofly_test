from django.shortcuts import get_object_or_404
from rest_framework.generics import UpdateAPIView
from rest_framework.mixins import UpdateModelMixin
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import UserSerializer


class UserListView(APIView):

    def get(self, request):
        user_model = get_user_model()
        items = user_model.objects.all()
        serializer = UserSerializer(items, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserDetailView(APIView):

    def get(self, request, pk=None, phone=None):
        user_model = get_user_model()
        if pk:
            item = get_object_or_404(user_model, pk=pk)
        else:
            item = get_object_or_404(user_model, phone_number=phone)
        serializer = UserSerializer(item)
        return Response(serializer.data)