from rest_framework.permissions import BasePermission

# class IsLoggedInUserOrAdmin(permissions.BasePermission):
    
#     def has_object_permission(self, request, view, obj):
#         return obj == request.user or request.user.is_staff

# class IsAdminUser(permissions.BasePermission):

#     def has_permission(self, request, view):
#         return request.user and request.user.is_staff

#     def has_object_permission(self, request, view, obj):
#         return obj == request.user and request.user.is_staff

# method_details = ['PUT', 'PATCH', 'GET', 'DELETE']


# class IsLoggedInUserOrAdmin(BasePermission):

#     def has_permission(self, request, view):
#         if (request.method in method_details and (request.user and request.user.is_authenticated())):
#             return True
#         return False 

#     def has_object_permission(self, request, view, obj):
#         if not request.user.is_authenticated():
#             return False

#         if view.action == 'retrieve':
#             return obj == request.user or request.user.is_admin
#         elif view.action in ['update', 'partial_update']:
#             return obj == request.user or request.user.is_admin
#         elif view.action == 'destroy':
#             return request.user.is_admin
#         else:
#             return False


# method_list = ['GET', 'POST']

# class IsAdminUser(BasePermission):

#     def has_permission(self, request, view):
#         if (request.method in method_list and (request.user and request.user.is_staff)):
#             return True
#         return False 

#     def has_object_permission(self, request, view, obj):
#         if (request.method in method_list and (obj.user == request.user and request.user.is_staff)):
#             return True
#         return False 

# class UserPermission(BasePermission):

#     def has_permission(self, request, view):
#         if request.method == 'list':
#             return request.user.is_authenticated and request.user.is_admin

#         elif request.method == 'create':
#             return True

#         return request.method in ('retrieve','update', 'partial_update', 'destroy') and (request.user and request.user.is_authenticated)
    
#     def has_object_permission(self, request, view, obj):
#         # if request.method == 'list' and request.user.is_admin:
#         #     return True
#         if request.method in ('retrieve','update', 'partial_update', 'destroy') and (request.user.is_admin or obj.user == request.user):
#             return True 
#         return False



# class UserPermission(permissions.BasePermission):

#     def has_permission(self, request, view):
#         if view.action == 'list':
#             return request.user.is_authenticated() and request.user.is_admin
#         elif view.action == 'create':
#             return True
#         elif view.action in ['retrieve', 'update', 'partial_update', 'destroy']:
#             return True
#         else:
#             return False

#     def has_object_permission(self, request, view, obj):
#         # Deny actions on objects if the user is not authenticated
#         if not request.user.is_authenticated():
#             return False

#         if view.action == 'retrieve':
#             return obj == request.user or request.user.is_admin
#         elif view.action in ['update', 'partial_update']:
#             return obj == request.user or request.user.is_admin
#         elif view.action == 'destroy':
#             return request.user.is_admin
#         else:
#             return False