from django.contrib import admin
from .models import Show, Season, Episode, Movie, Source
from django.db.models.functions import Coalesce
from django.db.models import Case, IntegerField, Value, When

@admin.register(Show)
class ShowAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'imdb_rating', 'kinopoisk_rating')
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(Season)
class SeasonAdmin(admin.ModelAdmin):
    list_display = ('show', 'number')
    list_filter = ('show',)
    ordering = ('show__title', 'number')

@admin.register(Episode)
class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('title', 'season', 'number', 'release_date')
    list_filter = ('season__show',)
    ordering = ('season__show__title', 'season__number', 'number')

@admin.register(Movie)
class MovieAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_date', 'imdb_rating', 'kinopoisk_rating')
    search_fields = ('title',)
    ordering = ('title',)

@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    list_display  = ("url", "source_type", "linked_movie", "linked_episode")
    list_filter   = ("source_type",)
    search_fields = ("url",)

    def linked_movie(self, obj):
        return obj.movie
    linked_movie.short_description = "Movie"

    def linked_episode(self, obj):
        return obj.episode
    linked_episode.short_description = "Episode"

    def get_queryset(self, request):
        qs = super().get_queryset(request)

        qs = qs.annotate(
            is_movie=Case(
                When(movie__isnull=False, then=Value(0)),
                default=Value(1),
                output_field=IntegerField(),
            ),
            sort_title=Coalesce(
                "movie__title",                  
                "episode__season__show__title"   
            )
        ).order_by(
            "is_movie",
            "sort_title",
            "episode__season__number",
            "episode__number",
            "id",
        )

        return qs
