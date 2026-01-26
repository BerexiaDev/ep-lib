from ep_lib.auth.user import User
from ep_lib.auth.portal_user import PortalUser

class AuthHelper:
    
    @staticmethod
    def get_auth_token(request):
        """Extract auth token from cookies"""
        return request.cookies.get('access_token')
    
    @staticmethod
    def get_logged_in_user(request):
        auth_token = AuthHelper.get_auth_token(request)
        if auth_token:
            resp = User.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = User().load({'_id':resp['token']})
                response_object = {
                    'status': 'success',
                    'data': {
                        'id': user.id,
                        'email': user.email,
                        'full_name': user.full_name,
                        'is_active': user.is_active,
                        'created_on': str(user.created_on),
                        'role': user.role
                    }
                }
                return response_object, 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 401
    
    @staticmethod
    def get_logged_in_user_from_token(token):
        resp = User.decode_auth_token(token)
        if not isinstance(resp, str):
            user = User().load({'_id':resp['token']})
            response_object = {
                'status': 'success',
                'data': {
                    'id': user.id,
                    'email': user.email,
                    'full_name': user.full_name,
                    'is_active': user.is_active,
                    'created_on': str(user.created_on),
                    'role': user.role
                }
            }
            return response_object
        
    @staticmethod
    def get_logged_in_portal_user(request):
        auth_token = AuthHelper.get_auth_token(request)
        if auth_token:
            resp = PortalUser.decode_auth_token(auth_token)
            if not isinstance(resp, str):
                user = PortalUser().load({'_id':resp['token']})
                response_object = {
                    'status': 'success',
                    'data': {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'created_on': str(user.created_on),
                    }
                }
                return response_object, 200
            response_object = {
                'status': 'fail',
                'message': resp
            }
            return response_object, 401
        else:
            response_object = {
                'status': 'fail',
                'message': 'Provide a valid auth token.'
            }
            return response_object, 401
    