from django.db import models

class Show(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField()
    release_date = models.DateField()
    imdb_rating = models.FloatField()
    kinopoisk_rating = models.FloatField()

    def __str__(self):
        return self.title

class Season(models.Model):
    show = models.ForeignKey(Show, related_name='seasons', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    description = models.TextField(blank=True)

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.show.title} - Season {self.number}'

class Episode(models.Model):
    season = models.ForeignKey(Season, related_name='episodes', on_delete=models.CASCADE)
    number = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    release_date = models.DateField()

    class Meta:
        ordering = ['number']

    def __str__(self):
        return f'{self.season.show.title} S{self.season.number}E{self.number} - {self.title}'

class Movie(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.URLField()
    release_date = models.DateField(null=True, blank=True)
    imdb_rating = models.FloatField()
    kinopoisk_rating = models.FloatField(null=True, blank=True, default=0)
    release_year = models.PositiveIntegerField(null=True, blank=True)

    def __str__(self):
        return self.title

SOURCE_TYPE_CHOICES = [
    ('playlist', 'Playlist'),
    ('direct', 'Direct'),
]

class Source(models.Model):
    movie = models.ForeignKey(Movie, related_name='sources', null=True, blank=True, on_delete=models.CASCADE)
    episode = models.ForeignKey(Episode, related_name='sources', null=True, blank=True, on_delete=models.CASCADE)
    url = models.URLField()
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)

    def __str__(self):
        target = self.movie or self.episode
        return f'{target} - {self.get_source_type_display()}'
