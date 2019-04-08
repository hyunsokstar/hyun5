from django.contrib.auth import get_user_model
from rest_framework.views import APIView
from . import models, serializers
from rest_framework.response import Response
from rest_framework import status
from nomadgram.notifications import views as notification_views

User = get_user_model()

# create your view~!
class ChangePassword(APIView):
    def put(self, request, username, format=None):
        print("ChangePassword 클래스 뷰 실행 ")
        user = request.user
        print('user : ', user)
        print('username : ', username)
        
        # url로 넘긴 username 과 현재 로그인 유저가 같은지 조사
        if user.username == username:
            # 현재 비번이 있으면 current_password로 얻어오기
            current_password = request.data.get('current_password',None)

            # 넘어온 비번이 맞는지확인, 넘어온 비번이 없으면 400 bad request
            if current_password is not None:
                passwords_match = user.check_password(current_password)
                # 비번이 맞으면 새로운 비밀번호 얻어와서 저장, 비번이 틀리면 400 bad request
                if passwords_match:
                    new_password = request.data.get('new_password',None)
                    # 새로운 비번이 있으면 저장 아니면 400 bad request
                    if new_password is not None:
                        user.set_password(new_password)
                        user.save()
                        return Response(status=status.HTTP_200_OK)
                    else:
                        return Response(status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response(status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response(status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class Search(APIView):
    def get(self, request, formt=None):
        # user_name을 url 요청으로부터 받아와서
        username = request.query_params.get('user_name', None)

        if username is not None:
            # db에서 해당 user 모델 정보가 있으면
            # users = models.User.objects.filter(username__icontains=username)
            users = models.User.objects.filter(username__istartswith=username)
            #직렬화한뒤
            serializer = serializers.ListUserSerializer(users, many=True)

            # 출력!
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        # 없으면 400 bad request
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

# 특정 유저를 팔로잉 하는 유저 리스트를 출력하는 클래스 뷰
class UserFollowing(APIView):
    def get(self, request, user_name, format = None):
        # 인자로 받은 유저 정보를 검색
        try:
            user = models.User.objects.get(username=user_name)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 유저를 팔로우하는 사람들을 검색
        user_following = found_user.following.all()

        # 직렬화 하기
        serializer = serializers.ListUserSerializer(
            user_following, many=True)

        # 응답 하기 (json 데이타 및 응답 코드)
        return Response(data=serializer.data, status = status.HTTP_200_OK)


# 특정 유저가 팔로잉 하는 사람들을 출력하는 클래스 뷰
class UserFollowers(APIView):
    def get(self, request, user_name, format = None):
        # 인자로 받은 user_name으로 유저 정보 검색
        try:
            user = models.User.objects.get(username=user_name)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 유저가 팔로워하는 사람들의 리트를 검색
        followers = user.followers.all()

        # followers를 직렬화, 리스트이므로 many = true option 필요
        serializer = serializers.ListUserSerializer(followers, many=True)

        # Response 함수로 json data와 응답 코드를 출력
        return Response(data=serializer.data, status = status.HTTP_200_OK)

# class UserProfile(APIView):
#     def get(self, reuquest, user_name, format=None):
#         try:
#             found_user = models.User.objects.get(username=user_name)
#         except models.User.DoesNotExist:
#             return Response(status=status.HTTP_404_NOT_FOUND)
#         serializer = serializers.UserProfileSerializer(found_user)
#         return Response(data=serializer.data, status=status.HTTP_200_OK)

class UserProfile(APIView):
    def get_user(self, user_name):
        try:
            user = models.User.objects.get(username=user_name)
            return user
        except models.User.DoesNotExist:
            return None

    def get(self, request, user_name, format=None):
        print("UserProfile 클래스뷰 실행")
        user = self.get_user(user_name)
        if user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        serializer = serializers.UserProfileSerializer(user)
        # print("serializer : ", serializer)

        return Response(data=serializer.data, status=202)

    # 유저 데이터 업데이트
    def put(self, request, user_name, format=None):

        user = request.user
        # 수정할 유저 객체 생성
        found_user= self.get_user(user_name)

        # 수정하려는 사용자가 없을 경우
        if found_user is None:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 로그인한 유저와 동일 인물인지 비교
        elif found_user.username != user.username:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        # serializer를 이용해 수정
        else:
            serializer = serializers.UserProfileSerializer(found_user, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            print(user, '의 프로필 수정 성공')
            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FollowUser(APIView):
    def post(self, request, user_id, format=None):
        user= request.user

        try:
            user_to_follow = models.User.objects.get(id=user_id)
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        user.following.add(user_to_follow)
        user.save()

        # 팔로우에 관한 알림 정보 저장
        notification_views.create_notification(user, user_to_follow, 'follow')

        print(user, '가' , user_to_follow, ' 를 팔로우하였습니다' )
        return Response(status=status.HTTP_200_OK)

class ExploreUsers(APIView):
    def get(self, request, format=None):
        last_five = models.User.objects.all().order_by('date_joined')[:5]
        serializer = serializers.ListUserSerializer(last_five, many=True)
        return Response(data=serializer.data, status=200)

class UnFollowUser(APIView):
    def post(self, request, user_id, format=None):

        user = request.user

        # 유저가 있을 경우
        try:
            user_to_follow = models.User.objects.get(id=user_id)

        # 유저가 없을 경우
        except models.User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

        # 팔로잉에서 해당 유저 삭제
        user.following.remove(user_to_follow)
        user.save()

        # 콘솔 메세지 확인
        print(user ,' 가 ' , user_to_follow, '에 대해 unfollow 하였습니다. ');

        return Response(status=status.HTTP_200_OK)
