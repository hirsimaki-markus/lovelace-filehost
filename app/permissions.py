#!/usr/bin/env python3

"""
Before making changes to these stubs, try doing ctrl+f find-in-project for the
function names to see where they are used. This should allow one to easily
find the critical areas that need changes.

This file provides functions that help relate the abstract permission objects
to individual routes and files. All the methods are stubs as the implementation
details for authprovider do not exist yet.

The choice of how to implement associating permission objects with a given
route is left for the implementer to allow optional designs such as having some
routes require elevated priviledges and others being public so that
get_yes_or_no_from_auth_provider_with_permission_object_and_token can return
True without having to even make a query to authprovider.

Suggested way to do the associating: add a dict to models.py such that;
{
    a_route: permission object,
    another_route: permission object,
}
and then check the dict as needed by the stubs in this file.
"""


def get_partial_permission_object_to_save_in_db(_sample_arg1, _sample_arg2):
    """Returns the part of a permission object that is saved with an individual
    file in a database. It is expected that when this partial permission object
    is read from a db, it is complemented by permission object whose
    information is found by checking permission object for a particular route.
    """
    return "{}"  # Serialized json.


def get_permission_for_route_that_is_not_a_file(_sample_arg1, _sample_arg2):
    """Returns the permission object for an endpoint that is a collection
    and not an individual file.
    """
    return "{}"  # Serialized json.


def get_permission_for_route_thats_a_file_in_db(_sample_arg1, _sample_arg2):
    """Returns the permission object for an endpoint that is not a collection
    and is an individual file. This function should read the partial permission
    object from the individual file and join it with the permission
    object associated with a given route.
    """
    return "{}"  # Serialized json.


def get_yes_or_no_from_auth_provider_with_permission_object_and_token(
    _sample_arg1, _sample_arg2
):
    """queries authprovider and returns a true if given token and
    given permission object show that the user can indeed perform the action
    they attempted to do
    """
    return True  # Always allow because the function is a stub.


def get_personal_information_when_saving_file_to_redis_database(
    _sample_arg1, _sample_arg2
):
    """The identifier should be obtained from authprovider. The id should be
    pseudonymous with only authprovider knowing the true identity.
    """
    return "Erkki Esimerkki"
