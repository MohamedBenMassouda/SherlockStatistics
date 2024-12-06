from django.shortcuts import render
from rest_framework.views import APIView, Response, status

from users.models import User
from users.serializers import UserSerializer


# Create your views here.
class UserList(APIView):
    def get(self, request):
        users = User.objects.all()

        return Response(UserSerializer(users, many=True).data)

    def post(self, request):
        try:
            serializer = UserSerializer(data=request.data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)

            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserDetail(APIView):
    def get(self, request, pk):
        try:
            user = User.objects.get(pk=pk)

            return Response(UserSerializer(user).data)

        except User.DoesNotExist:
            return Response(
                {
                    "detail": "User not found",
                },
                status=status.HTTP_404_NOT_FOUND
            )

        except Exception as e:
            return Response(str(e), status=status.HTTP_500_INTERNAL_SERVER_ERROR)
