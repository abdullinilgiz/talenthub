import yaml
import string
import re
from typing import List

import cv2 as cv
import numpy as np
import easyocr
import matplotlib.image as mpimg

from django.contrib.auth import get_user_model
from djoser.views import UserViewSet
from rest_framework.permissions import (AllowAny,
                                        IsAuthenticated,
                                        IsAuthenticatedOrReadOnly,
                                        SAFE_METHODS, )
from rest_framework import viewsets, mixins
from django.conf import settings

from api.serializers import (DjoserUserSerializer,
                             AllergenSerializer,
                             GetPhotoQuerySerializer,
                             PostPhotoQuerySerializer, )
from ingredients.models import Allergen, PhotoQuery, Ingredient

User = get_user_model()

path_to_file = settings.BASE_DIR / 'data.yaml'
with open(path_to_file, 'r', encoding='utf-8') as file:
    id_data = yaml.safe_load(file)


class DjoserUserViewSet(UserViewSet):
    queryset = User.objects.all()
    serializer_class = DjoserUserSerializer
    permission_classes = [AllowAny, ]


class AllergensViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for all allergens in database.

    list: List all Allergen instances

    retrieve: Retrieve Allergen by id

    update: Update Allergen by id

    create: Create Allergen

    destroy: Delete Allergen by id
    """
    queryset = Allergen.objects.all()
    permission_classes = (IsAuthenticatedOrReadOnly, )
    serializer_class = AllergenSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]


class MyAllergensViewSet(viewsets.ModelViewSet):
    """
    ModelViewSet for allergens of current user.

    list: List all Allergen inctances of current user

    retrieve: Retrieve Allergen of current user by id

    update: Update Allergen of current user by id

    create: Create Allergen

    destroy: Delete Allergen of current user by id
    """
    permission_classes = (IsAuthenticated, )
    serializer_class = AllergenSerializer
    http_method_names = ['get', 'post', 'patch', 'delete', ]

    def perform_create(self, serializer):
        instance = serializer.save()
        for idx, items in id_data.items():
            if instance.name in items:
                instance.allergen_id = idx
                serializer.save()
                break

    def get_queryset(self):
        return Allergen.objects.filter(user=self.request.user)


class PhotoQueryViewSet(mixins.ListModelMixin,
                        mixins.RetrieveModelMixin,
                        mixins.CreateModelMixin,
                        viewsets.GenericViewSet):
    """
    ViewSet for all PhotoQuery of current user.

    We create PhotoQuery when user upload photo.

    list: List all PhotoQuery instances of current user

    retrieve: Retrieve PhotoQuery of current user by id

    create: Create PhotoQuery
    """
    permission_classes = (IsAuthenticated, )
    http_method_names = ['get', 'post', ]

    def _find_matching_words(self,
                             Coc_list: List[str],
                             matching_ids: List[int]) -> List[str]:
        """
        Находит слова из Coc_list в подмножестве словаря data,
        где ключи соответствуют matching_ids.

        Параметры:
        - Coc_list (List[str]): Список слов для поиска.
        - matching_ids (List[int]): Список id для поиска в словаре data.
        - data (Dict[int, set]): Словарь, в котором производится поиск.

        Возвращает:
        - List[str]: Список найденных слов.
        """

        processed_list = []

        for word in Coc_list:
            normalized_word = word.lower()
            processed_list.append(normalized_word)

            # ВОТ НАД ЭТИМ НАДО СЕРЬЕЗНО ПОДУМАТЬ
            if ' ' in normalized_word:
                processed_list.extend(normalized_word.split())

        found_words = {}

        for word in processed_list:
            for idx in matching_ids:
                if word in id_data[idx]:
                    if word not in found_words:
                        found_words[word] = []
                    found_words[word].append(idx)

        return list(found_words.keys())

    def perform_create(self, serializer):
        instance = serializer.save()
        image_path = instance.image.path
        print(image_path)
        Original_img = mpimg.imread(image_path)
        img = np.uint8(np.clip((cv.add(1.5 * Original_img, 0)), 0, 255))
        reader = easyocr.Reader(['ru'])
        results = reader.readtext(img)
        ingredients = []
        symbols = '[a-zA-Z0-9]|[„“’""!?$…‒-—_@.&:;#+]|[\\\]|[!*\(\),\).\«\»,\»'
        symbols += '.\<\>>\[\]\{\}\|\€\/\~\^\%\"\"]+'
        punct = string.punctuation
        for i in results:
            words = i[1]
            lst2 = [re.sub(symbols, ' ', words)]
            lst3 = [word.strip() for word in lst2]
            lst4 = [word.lower() for word in lst3 if word not in punct]
            ingredients.append(lst4)
        ingredients = sum(ingredients, [])
        allergens_ids = list(Allergen.objects.filter(
            user=self.request.user).values_list('allergen_id', flat=True))
        matches = self._find_matching_words(ingredients, allergens_ids)
        print(matches)
        ingredients_for_bulk = []
        for ingr in ingredients:
            marker = False
            for match in matches:
                if match in ingr:
                    marker = True
                    break
            ingredients_for_bulk.append(Ingredient(
                query=instance,
                name=ingr,
                is_dangerous=marker,
            ))
        Ingredient.objects.bulk_create(ingredients_for_bulk)

    def get_queryset(self):
        return PhotoQuery.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request in SAFE_METHODS:
            return GetPhotoQuerySerializer
        return PostPhotoQuerySerializer
