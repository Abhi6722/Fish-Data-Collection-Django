from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from .serializer import LoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken

# Generate Token Manually
def get_tokens_for_user(user):
  refresh = RefreshToken.for_user(user)
  return {
      'refresh': str(refresh),
      'access': str(refresh.access_token),
  }
  
class LoginView(generics.GenericAPIView):
    # permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token = get_tokens_for_user(user)
        # token, _ = Token.objects.get_or_create(user=user)
        return Response({'token': token,
                         'message':'Login Success'}, status = status.HTTP_200_OK)