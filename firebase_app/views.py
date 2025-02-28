import logging 
import matplotlib
matplotlib.use("Agg")  

import matplotlib.pyplot as plt
from adjustText import adjust_text  # Import adjustText to fix overlapping labels
from io import BytesIO
import base64
from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import CreateModelMixin, ListModelMixin, RetrieveModelMixin, UpdateModelMixin
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
from rest_framework.decorators import action
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from .models import UserDB, UserStats
from .serializers import UserDBSerializer, UserStatsSerializer

# Logger for debugging
logger = logging.getLogger(__name__)

def home_view(request: HttpRequest):
    return render(request, "templates.html")

class UserDBView(CreateModelMixin, ListModelMixin, RetrieveModelMixin, GenericViewSet):
    queryset = UserDB.objects.all()
    serializer_class = UserDBSerializer
    lookup_field = "id"
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        try:
            user = self.get_object()
            serializer = self.get_serializer(user)

            # Fetch user stats
            user_stats = UserStats.objects.filter(id=user.id).first()
            stats_serializer = UserStatsSerializer(user_stats) if user_stats else None

            return Response(
                {
                    "user": serializer.data,
                    "stats": stats_serializer.data if stats_serializer else {"likes": 0, "dislikes": 0, "watch": 0},
                },
                status=status.HTTP_200_OK,
            )
        except UserDB.DoesNotExist:
            return Response({"error": "User not found."}, status=status.HTTP_404_NOT_FOUND)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response({"users": serializer.data}, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="create-user")
    def create_user(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class UserStatsView(ListModelMixin, RetrieveModelMixin, UpdateModelMixin, GenericViewSet):
    queryset = UserStats.objects.all()
    serializer_class = UserStatsSerializer
    lookup_field = "id"
    lookup_url_kwarg = "id"
    renderer_classes = [JSONRenderer]

    def retrieve(self, request, *args, **kwargs):
        try:
            stats = self.get_object()
            serializer = self.get_serializer(stats)
            return Response({"stats": serializer.data}, status=status.HTTP_200_OK)
        except UserStats.DoesNotExist:
            return Response({"error": "Stats not found."}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=["get"], url_path="pie-chart")
    def generate_pie_chart(self, request, id=None):
        try:
            user_stats = UserStats.objects.get(id=id)
            stats = {
                "Likes": user_stats.likes,
                "Dislikes": user_stats.dislikes,
                "Watch": user_stats.watch,
            }

            labels = list(stats.keys())
            sizes = list(stats.values())

            if sum(sizes) == 0:
                return JsonResponse({"error": "No data to display"}, status=400)

            colors = ["#008000", "#0000FF", "#FF0000"]  # Green, Blue, Red
            explode = [0.1 if size < sum(sizes) * 0.1 else 0 for size in sizes]  

            fig, ax = plt.subplots(figsize=(6, 6))
            fig.patch.set_facecolor("#1f1f1f")  
            ax.set_facecolor("#1f1f1f")

            wedges, texts, autotexts = ax.pie(
                sizes,
                labels=labels,
                autopct=lambda p: f'{p:.1f}%' if p > 1 else '',  
                startangle=90,
                colors=colors,
                explode=explode,
                pctdistance=0.8,
                labeldistance=1.2,
                textprops={"color": "white", "fontsize": 12},
            )

            ax.axis("equal")  
            all_texts = texts + autotexts
            adjust_text(all_texts, only_move={'points': 'y', 'texts': 'y'})  

            img_io = BytesIO()
            plt.savefig(img_io, format="png", facecolor=fig.get_facecolor(), bbox_inches="tight")
            img_io.seek(0)
            plt.close(fig)

            chart_image = base64.b64encode(img_io.getvalue()).decode("utf-8")
            return JsonResponse({"pie_chart": chart_image}, status=200)

        except UserStats.DoesNotExist:
            return JsonResponse({"error": "User stats not found."}, status=404)

    @action(detail=True, methods=["post"], url_path="update-likes")
    def update_likes(self, request, id=None):
        logger.debug(f"Received update-likes request for id: {id}")
        user_stats, created = UserStats.objects.get_or_create(id=id)  # Ensure record exists
        user_stats.likes += 1
        user_stats.save()
        return Response({"message": "Likes updated", "likes": user_stats.likes}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="update-dislikes")
    def update_dislikes(self, request, id=None):
        user_stats, created = UserStats.objects.get_or_create(id=id)
        user_stats.dislikes += 1
        user_stats.save()
        return Response({"message": "Dislikes updated", "dislikes": user_stats.dislikes}, status=status.HTTP_200_OK)

    @action(detail=True, methods=["post"], url_path="update-watch")
    def update_watch(self, request, id=None):
        user_stats, created = UserStats.objects.get_or_create(id=id)
        user_stats.watch += 1
        user_stats.save()
        return Response({"message": "Watch count updated", "watch": user_stats.watch}, status=status.HTTP_200_OK)
