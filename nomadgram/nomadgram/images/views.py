from rest_framework.views import APIView
from rest_framework.response import Response
from . import models, serializers
from rest_framework import status
from nomadgram.notifications import views as notification_views
from nomadgram.users import models as user_models
from nomadgram.users import serializers as user_serializers


# Create your views here.
# hastag로 이미지 검색 1122

# 피드 뷰 디테일
class ImageDetail(APIView):

    def find_own_image(self, image_id, user):
        try:
            image = models.Image.objects.get(id=image_id, creator=user)
            return image
        except models.Image.DoesNotExist:
            return None

    def get(self, request, image_id, format=None):
        user = request.user
        try:
            image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        serializer = serializers.ImageSerializer(image)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    # ImageDetail로 요청이 put 요청일 경우
    # 업데이트 처리
    def put(self, request, image_id, format = None):
        user = request.user
        print('user : ', user)
        print( 'ImageDetail put() 실행 ')
        print('image_id : ', image_id)
        print('user : ', user)

        image = self.find_own_image(image_id, user)
        print('image : ', image)

        if image is None:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = serializers.InputImageSerializer(image, data=request.data, partial=True)
        # 직렬화 객체가 정상적으로 만들어졌으면 save 해라
        # 아니면 HTTP_400_BAD_REQUEST으로 응답
        if serializer.is_valid():
            serializer.save(creator=user)
            return Response(data=serializer.data, status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class Search(APIView):
    def get(self, request, format=None):
        hashtags = request.query_params.get('hashtags', None)

        if hashtags is not None:
            print("hashtag : " , hashtags)

            hashtag = hashtags.split(",")
            images = models.Image.objects.filter(tags__name__in = hashtag).distinct()
            print(images)

            serializer = serializers.ImageSerializer(images, many = True)

            return Response(data=serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_400_BAD_REQUEST)

class DeleteComments(APIView):

    def delete(self, request, image_id, comment_id, format=None):
        user = request.user

        # 댓글 삭제 시도
        try:
            comment = models.Comment.objects.get(image__id= image_id, id=comment_id, creator=user )
            comment.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

            print('{user} 가 {image_id}번글 {id}번 댓글을 삭제 하였습니다'.format(user, image_id, comment_id))

        # ??
        except models.Comment.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

class CommentOnImage(APIView):
    print('CommentOnImage 함수 실행')
    def post(self, request, image_id, format=None):

        # 댓글 다는 사람 객체
        user = request.user
        # 댓글 달 이미지 객체 생성
        try:
            image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=404)

        serializer = serializers.CommentSerializer(data=request.data)

        if serializer.is_valid():
            # 입력한 데이터를 저장
            serializer.save(creator=user, image=image)

            # 이미지에 댓글 단것에 대해 알림 저장
            notification_views.create_notification(user,
            image.creator, 'comment', image, request.data['message'])

            return Response(data=serializer.data, status=201)

        else:
            return Response(data=serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class LikeImage(APIView):
    def get(self, request, image_id, format=None):
        likes = models.Like.objects.filter(image__id=image_id)
        # print("likes.values() : ", likes.values())

        like_creators_ids = likes.values('creator_id')
        users = user_models.User.objects.filter(id__in=like_creators_ids)
        print('users : ', users)

        serializer = user_serializers.ListUserSerializer(users, many=True)

        return Response(data=serializer.data, status=status.HTTP_200_OK)

    def post(self, request, image_id, format=None):
        user = request.user

        try:
            image = models.Image.objects.get(id=image_id)
        except models.Image.DoesNotExist:
            return Response(status=404)

        # 유저가 저장한 해당 이미지에 대한 좋아요를 삭제 시도
        # 없을 경우에는 저장
        try:
            preexisting_like = models.Like.objects.get(
                creator=user,
                image=image
            )
            # preexisting_like.delete()
            # print(user , '님이')
            # print(image , ' 이미지를 삭제하였습니다. : ')
            return Response(status=304)

        # 기존의 좋아요가 없을 경우 저장
        except models.Like.DoesNotExist:
            new_like = models.Like.objects.create(
                creator=user,
                image=image
            )

        new_like.save()
        print(user, '님이 ')
        print(image , '에 대해 좋아요를 저장했습니다.')

        # 좋아요에 대해 알림 메세지 저장
        notification_views.create_notification(user, image.creator, 'like', image)

        return Response(status=200)


class UnLikeImage(APIView):
    def delete(self, request, image_id, format=None):
        user = request.user

        # 좋아요를 취소 시도
        try:
            preexisiting_like = models.Like.objects.get(
                creator=user,
                image__id=image_id
            )
            preexisiting_like.delete()
            print(user ,' 가 ' , preexisiting_like , ' 에 대한 좋아요를 삭제 하였습니다')
            return Response(status=status.HTTP_204_NO_CONTENT)

        # 좋아요가 없을 경우 에러 처리
        except models.Like.DoesNotExist:
            print(user ,' 의 좋아요 정보중에 ' , preexisiting_like , ' 에 대한 정보를 찾지 못했습니다.')
            return Response(status=status.HTTP_304_NOT_MODIFIED)

class Feed(APIView):
    def get(self, request, format=None):
        # 요청한 현재 유저(나)
        user = request.user

        # 유저가 팔로잉 하는 사람
        following_users = user.following.all()
        print("following_users , " , following_users)

        # 반환할 이미지 배열
        image_list = []

        # 내가 팔로잉 하는 유저가 쓴 이미지 2개
        for following_user in following_users:
            user_images = following_user.images.all()[:2]

            for image in user_images:
                print("image : ", image)
                image_list.append(image)
        print("image_list : " , image_list)

        # 본인 이미지도 추가
        my_images = user.images.all()[:2]
        for image in my_images:
            image_list.append(image)

        sorted_list = sorted(image_list, key=get_key, reverse=True)
        serializer = serializers.ImageSerializer(sorted_list, many=True)
        return Response(serializer.data)

def get_key(image):
    return image.created_at
