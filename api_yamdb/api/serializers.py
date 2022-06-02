from datetime import datetime

from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from reviews.models import Category, Comment, Genre, Review, Title, User


class ReviewSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Review."""
    author = serializers.SlugRelatedField(slug_field='username',
                                          read_only=True)
    title = serializers.SlugRelatedField(slug_field='name', read_only=True)

    class Meta:
        model = Review
        fields = ('id', 'text', 'author', 'score', 'title', 'pub_date')

    def validate(self, data):
        if self.context.get('request').method != 'POST':
            return data

        title_id = self.context['view'].kwargs.get('title_id')
        author = self.context.get('request').user
        if Review.objects.filter(title_id=title_id, author=author):
            raise serializers.ValidationError('Отзыв уже написан')
        return data

    def validate_score(self, value):
        if not 1 <= value <= 10:
            raise serializers.ValidationError(
                'Оценка может быть от 1 до 10'
            )
        return value


class CategorySerializer(serializers.ModelSerializer):
    """Сериализатор для модели Category."""
    class Meta:
        fields = ('name', 'slug')
        model = Category


class GenreSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Genre."""
    class Meta:
        fields = ('name', 'slug')
        model = Genre


class TitleReadSerializer(serializers.ModelSerializer):
    """Сериализатор Get для модели Title."""
    category = CategorySerializer(read_only=True, many=False)
    genre = GenreSerializer(read_only=True, many=True)
    rating = serializers.FloatField()

    class Meta:
        fields = (
            'id',
            'category',
            'name',
            'year',
            'description',
            'genre',
            'rating',
            'reviews')
        model = Title


class TitleWriteSerializer(serializers.ModelSerializer):
    """Сериализатор Post для модели Title."""
    category = serializers.SlugRelatedField(
        queryset=Category.objects.all(), slug_field='slug')
    genre = serializers.SlugRelatedField(
        queryset=Genre.objects.all(),
        slug_field='slug',
        many=True)

    class Meta:
        fields = ('id', 'category', 'name', 'year', 'description', 'genre',)
        model = Title

    def validate_year(self, value):
        year = datetime.now().year
        if not value <= year:
            raise serializers.ValidationError('Проверьте год произведения')
        return value


class UserSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        required=True,
        max_length=150,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        )


class UserMeSerializer(serializers.ModelSerializer):
    """Сериализатор для модели User."""
    role = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'bio', 'email', 'role'
        )


class UserSignupSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True, max_length=254)
    username = serializers.RegexField(
        regex=r'^[\w.@+-]+\Z$',
        required=True,
        max_length=150
    )

    def validate_username(self, value):
        if value == 'me':
            raise serializers.ValidationError(
                'Нельзя создавать пользователя с username = "me".'
            )
        return value


class ConfirmationCodeSerializer(serializers.Serializer):
    username = serializers.RegexField(required=True, regex=r'^[\w.@+-]+\Z$')
    confirmation_code = serializers.CharField(required=True)


class CommentSerializer(serializers.ModelSerializer):
    """Сериализатор для модели Comment."""
    author = serializers.SlugRelatedField(
        slug_field='username',
        read_only=True,
        default=serializers.CurrentUserDefault())

    class Meta:
        model = Comment
        fields = ('id', 'text', 'pub_date', 'author')
