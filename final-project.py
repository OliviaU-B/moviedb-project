import requests
from pprint import pprint
from time import ctime
import os


def run_a_search():
    chosen_option = input(
        'What would you like to search for today? Enter the corresponding number (1, 2, 3 or 4)\n for the search you '
        'would like to carry out:\n1) Search for movies starring a specific actor \n2) Search for a movie '
        'recommendation based on a film you like \n3) Search for the credits for a particular film \n4) Manage my '
        'search history \n')

    if chosen_option == "1":
        list_actors_movies()
        ask_if_search_again()
    elif chosen_option == "2":
        get_a_movie_recommendation()
        ask_if_search_again()
    elif chosen_option == "3":
        get_movie_credits()
        ask_if_search_again()
    elif chosen_option == "4":
        refine_search()
        ask_if_search_again()
    else:
        print('Sorry, I do not recognise what you have entered, please try again. \n')
        run_a_search()


def add_to_search_history(type_of_search, user_search):
    with open('../search-history.txt', 'a') as search_history:
        search_history.write('{}: "{}" at {} \n'.format(type_of_search, user_search, ctime()))


def refine_search():
    manage_search_history = input('What would you like to do? Please enter 1 or 2 for the action you would like '
                                  'to carry out: \n1) View my search history \n2) Clear my search history\n')
    if manage_search_history == "1":
        view_search_history()
    elif manage_search_history == "2":
        clear_search_history()
    else:
        print('Sorry, I do not recognise what you have entered, please try again')


def clear_search_history():
    with open('../search-history.txt', 'w'): pass
    print('Your search history is now cleared.')


def view_search_history():
    print('Your search history: \n')
    with open('../search-history.txt', 'r') as search_history:
        print(search_history.read())


def save_results_to_file(search_entry, search_type, results):
    ask_to_save = input("Would you like to save these results to a file? y/n? \n")
    if ask_to_save == "y":
        with open('saved-results/{} - {}.txt'.format(search_entry, search_type), 'a') as text_file:
            results_to_write = ""
            for result in results:
                results_to_write += str(result) + "\n"
            text_file.write(results_to_write)
    elif ask_to_save == "n":
        return
    else:
        print("I'm sorry, I don't recognise what you have entered. Please try again!")
        save_results_to_file()


def ask_if_search_again():
    make_another = input('Would you like to make another search? y/n?\n')
    if make_another == "y":
        run_a_search()
    elif make_another == "n":
        print('Thank you for using MovieSearch! See you again soon!')
    else:
        print('Sorry, I do not recognise that, please try again')
        ask_if_search_again()


def list_actors_movies():
    which_actor = input("Please type in the actor's name that you would like to see? \n")

    add_to_search_history("Actor's movie history", which_actor)

    response = requests.get('https://api.themoviedb.org/3/search/person', params={
        "api_key": os.environ.get('API_KEY'),
        "language": "en-US",
        "query": which_actor,
        "page": 1,
        "include_adult": "false",
    })
    try:
        actor_id = response.json()['results'][0]['id']
    except IndexError:
        print("Uh oh! It looks like that is not a name in our list. Please check your spelling or check for another "
              "actor\n")
        return list_actors_movies()

    movies_response = requests.get('https://api.themoviedb.org/3/person/{}/movie_credits'.format(actor_id), params={
        "api_key": os.environ.get('API_KEY'),
        "language": "en-US"
    })
    movies = movies_response.json()['cast']
    movie_list = []
    for i in range(len(movies)):
        movie_list.append(movies[i]['title'])
    pprint(movie_list)
    save_results_to_file(which_actor, "Movies", movie_list)
    return movie_list


def get_a_movie_recommendation():
    which_movie = input("Please type a movie title you have enjoyed in the past: \n")

    add_to_search_history("Movie Recommendation", which_movie)

    response = requests.get('https://api.themoviedb.org/3/search/movie', params={
        "api_key": os.environ.get('API_KEY'),
        "language": "en-US",
        "query": which_movie,
        "page": 1,
        "include_adult": "false",
    })
    try:
        movie_id = response.json()['results'][0]['id']
    except IndexError:
        print("Uh oh! We don't recognise that movie, please check your spelling or enter another movie for a "
              "recommendation!\n")
        return get_a_movie_recommendation()
    recommendations_response = requests.get('https://api.themoviedb.org/3/movie/{}/recommendations'.format(movie_id),
                                            params={
                                                "api_key": os.environ.get('API_KEY'),
                                                "language": "en-US",
                                                "page": 1,
                                            })

    recommendations = recommendations_response.json()['results']
    recommendations_list = []
    for i in range(len(recommendations)):
        recommendations_list.append(recommendations[i]['title'])
    pprint(recommendations_list)
    save_results_to_file(which_movie, "Recommendations", recommendations_list)
    return recommendations_list


def get_movie_credits():
    which_movie = input("Please enter which movie you would like to retrieve the credits for: \n")

    add_to_search_history("Movie Credits", which_movie)

    response = requests.get('https://api.themoviedb.org/3/search/movie', params={
        "api_key": os.environ.get('API_KEY'),
        "language": "en-US",
        "query": which_movie,
        "page": 1,
        "include_adult": "false",
    })

    try:
        movie_id = response.json()['results'][0]['id']
    except IndexError:
        print("Uh oh! We don't recognise that movie, please check your spelling or enter another movie for a "
              "recommendation!\n")
        return get_movie_credits()
    credits_response = requests.get('https://api.themoviedb.org/3/movie/{}/credits'.format(movie_id), params={
        "api_key": os.environ.get('API_KEY'),
    })
    movie_credits = credits_response.json()['cast']
    credits_list = []
    for i in range(len(movie_credits)):
        credits_list.append(movie_credits[i]['name'])
    pprint(credits_list)
    save_results_to_file(which_movie, "Credits", credits_list)
    return credits_list


run_a_search()
