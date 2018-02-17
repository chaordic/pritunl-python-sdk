# This is a fork of @Lowess's code (https://github.com/ansible/ansible/pull/26584)

import logging
import requests
import json
from six import iteritems
from .auth import pritunl_auth_request

LOGGER = logging.getLogger(__name__)

def _list_pritunl_organization(filters=None):
    orgs = []

    response = pritunl_auth_request('GET', '/organization')

    if response.status_code != 200:
        LOGGER.debug('Could not retrieve organizations from Pritunl')
    else:
        for org in response.json():
            # No filtering
            if filters is None:
                orgs.append(org)

            else:
                filtered_flag = False

                for filter_key, filter_val in iteritems(filters):
                    if filter_val != org[filter_key]:
                        filtered_flag = True

                if not filtered_flag:
                    orgs.append(org)

    return orgs


def _list_pritunl_user(organization_id,filters=None):
    users = []

    response = pritunl_auth_request('GET', "/user/%s" % organization_id)

    if response.status_code != 200:
        LOGGER.debug('Could not retrieve users from Pritunl')
    else:
        for user in response.json():
            # No filtering
            if filters is None:
                users.append(user)

            else:
                filtered_flag = False

                for filter_key, filter_val in iteritems(filters):
                    if filter_val != user[filter_key]:
                        filtered_flag = True

                if not filtered_flag:
                    users.append(user)

    return users


def get_pritunl_user(user_name, org_name, user_type):

    org_obj_list = _list_pritunl_organization({"name": org_name})

    if len(org_obj_list) == 0:
        LOGGER.info("Can not list users from the organization '%s' which does not exist" % org_name)

    org_id = org_obj_list[0]['id']

    users = _list_pritunl_user(org_id, filters=({"type": user_type} if user_name is None else {"name": user_name, "type": user_type}))

    result = {}
    result['changed'] = False
    result['users'] = users

    return result


def post_pritunl_user(org_name,user_name,user_email=None,user_groups=None,user_disabled=None,user_gravatar=None,user_type=None):
    result = {}

    if user_name is None:
        LOGGER.info('Please provide a user name using user_name=<username>')

    user_params = {
        'name': user_name,
        'email': user_email,
        'groups': user_groups,
        'disabled': user_disabled,
        'gravatar': user_gravatar,
        'type': user_type,
    }

    org_obj_list = _list_pritunl_organization({"name": org_name})

    if len(org_obj_list) == 0:
        LOGGER.debug("Can not add user to organization '%s' which does not exist" % org_name)

    org_id = org_obj_list[0]['id']

    # Grab existing users from this org
    users = _list_pritunl_user(org_id, filters={"name": user_name})

    # Check if the pritunl user already exists
    # If yes do nothing
    if len(users) > 0:
        # Compare remote user params with local user_params and trigger update if needed
        user_params_changed = False
        for key in user_params.keys():
            # When a param is not specified grab the existing one to prevent from changing it with the PUT request
            if user_params[key] is None:
                user_params[key] = users[0][key]

            # groups is a list comparison
            if key == 'groups':
                if set(users[0][key]) != set(user_params[key]):
                    user_params_changed = True

            # otherwise it is either a boolean or a string
            else:
                if users[0][key] != user_params[key]:
                    user_params_changed = True

        # Trigger a PUT on the API to update the current user if settings have changed
        if user_params_changed:
            response = pritunl_auth_request('PUT',
                                            "/user/%s/%s" % (org_id, users[0]['id']),
                                            headers={'Content-Type': 'application/json'},
                                            data=json.dumps(user_params))

            if response.status_code != 200:
                LOGGER.debug("Could not update Pritunl user %s from %s organization" % (user_name, org_name) )
            else:
                return response.json()
        else:
            result['changed'] = False
            result['response'] = users
    else:
        response = pritunl_auth_request('POST', "/user/%s" % org_id,
                                        headers={'Content-Type': 'application/json'},
                                        data=json.dumps(user_params))

        if response.status_code != 200:
            LOGGER.debug("Could not add Pritunl user %s to %s organization" % (user_params['name'], org_name) )
        else:
            result['changed'] = True
            result['response'] = response.json()

    return result

def delete_pritunl_user(org_name,user_name):
    result = {}

    org_obj_list = _list_pritunl_organization({"name": org_name})

    if len(org_obj_list) == 0:
        LOGGER.debug("Can not remove user from the organization '%s' which does not exist" % org_name)

    org_id = org_obj_list[0]['id']

    # Grab existing users from this org
    users = _list_pritunl_user(org_id, filters={"name": user_name})

    # Check if the pritunl user exists, if not, do nothing
    if len(users) == 0:
        LOGGER.debug("Can not remove user from the organization '%s', user does not exist" % user_name)

    # Otherwise remove the org from Pritunl
    else:
        response = pritunl_auth_request('DELETE', "/user/%s/%s" % (org_id, users[0]['id']))

        if response.status_code != 200:
            LOGGER.debug("Could not remove user %s from organization %s from Pritunl" % (users[0]['name'], org_name) )
        else:
            result['changed'] = True
            result['response'] = response.json()

    return result
