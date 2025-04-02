from django.urls import path
from profile import views as auth_views
from profile import admin_views

urlpatterns = [
    path('signup/', auth_views.SignUpView.as_view(), name = 'signup'),
    path('signin/', auth_views.SignInView.as_view(), name = 'signin'),
    path('getProfile/', auth_views.GetProfile.as_view(), name = 'getProfile'),
    path('generateResetPasswordLink/', auth_views.GeneratePasswordResetLink.as_view(), name = 'generateResetPasswordLink'),
    path('resetPasswordByLink/', auth_views.ResetPasswordByLink.as_view(), name = 'resetPasswordByLink'),
    path('updateUserProfile/', auth_views.UpdateUserProfile.as_view(), name = 'updateUserProfile'),
    path('getUserList/<str:role>/', auth_views.GetUserList.as_view(), name = 'getUserList'),
    path('addRole/', admin_views.AdminAddRole.as_view(), name = 'AdminAddRole'),
    path('AddUserbyRole/', admin_views.AdminPmAddUser.as_view(), name = 'AddUser'),
    path('users/', admin_views.AdminPmUserList.as_view(), name = 'UserList'),
    path('users/<int:user_id>', auth_views.GetUserByAdminorPm.as_view(), name = 'user'),
    path('usersPaginated/', admin_views.AdminPmUserListPaginated.as_view(), name = 'UserListPaginated'),
    path('userDelete/<int:user_id>', admin_views.DeleteUser.as_view(), name = 'DeleteUser'),
    path('getRoles/', auth_views.GetRoleList.as_view(), name= 'RolesList')
]
