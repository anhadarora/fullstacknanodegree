import fresh_tomatoes
import media

""" This module holds the list of movies and their attributes as objects.
This list populates my Movie website.
The fresh_tomatoes.open_movies_page() constructor is called."""

# Movie instances
lion_king = media.Movie(
    "Lion King",
    "A story of good triumphing evil on the savannah!",
    "http://t1.gstatic.com/images?q=tbn:ANd9GcQ2vZQTR"
    "7HyXqWbjYYr0HNfAyDLRq7EXogJGAgG0bbM8odQlDLV",
    "https://www.youtube.com/watch?v=MPugv1k7r-s")

crash = media.Movie(
    "Crash", "Interweaving lives 'crash' into each other.",
    "http://www.gstatic.com/tv/thumb/movieposters/35710/p35710_p_v7_aa.jpg",
    "https://www.youtube.com/watch?v=durNwe9pL0E")

city_of_god = media.Movie(
    "City of God", "Shit gets real in the favelas!",
    "http://cdn.miramax.com/media/assets/City-of-God1.png",
    "www.youtube.com/watch?v=ioUE_5wpg_E")

royal_tenenbaums = media.Movie(
    "The Royal Tenenbaums", "A family of geniuses is dysfunctional!",
    "http://41.media.tumblr.com/tumblr_m15fgy1xJG1r4k0fyo1_500.png",
    "https://www.youtube.com/watch?v=aPO12GYknq4")

the_constant_gardner = media.Movie(
    "The Constant Gardner", "A man's wife stirs shit up in the "
    "pharmaceutical industry, and he loves to garden!",
    "http://static.rogerebert.com/uploads/movie/movie_poster/"
    "the-constant-gardener-2005/large_r7QOXMcuIqZUeIVXVc4BCZrd9ni.jpg",
    "https://www.youtube.com/watch?v=r4iTjavIkbk")

the_usual_suspects = media.Movie(
    "The Usual Suspects", "A crime is committed, a story is told, "
    "but what really happened?",
    "http://hdmovies.name/wp-content/uploads/2015/04/"
    "The-Usual-Suspect-1995-HD-720p-BluRay-682x1024.jpg",
    "https://www.youtube.com/watch?v=oiXdPolca5w")

# the list of movies
movies = [lion_king, crash, city_of_god, royal_tenenbaums,
          the_constant_gardner, the_usual_suspects]

# function that opens runs a local html page in a browser
fresh_tomatoes.open_movies_page(movies)
