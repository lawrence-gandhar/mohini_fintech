
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from . import views
from . import administrators as admin
from . import database_management as dbase
from . import decorators

# Authorization
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'base/logout.html'), name = 'logout'),
    re_path(r'^accounts/*', RedirectView.as_view(pattern_name='login', permanent=True)),
    path('change_password/', views.change_password, name='change_password'),
    path('signup/', views.signup, name='signup'),
    path('reset_password/<int:ins>/', views.reset_password, name='reset_password'),
]

# ADMIN PAGES
urlpatterns += [
    path('admin/dashboard/', decorators.admin_required(admin.dashboard), name="admin_dashboard"),
    path('admin/manage_users/', decorators.admin_required(admin.manage_users), name="manage_users"),
    path('admin/edit_user/', decorators.admin_required(admin.edit_user), name="edit_user"),
    path('admin/delete_user/<int:ins>/', decorators.admin_required(admin.delete_user), name="delete_user"),
    path('admin/delete_selected_users/', decorators.admin_required(admin.delete_selected_users), name="delete_selected_users"),
    path('admin/manage_users/new/', decorators.admin_required(admin.manage_new_users), name="manage_new_users"),
    path('admin/new_users/accept/', decorators.admin_required(admin.accept_new_users), name="accept_new_users"),
    path('admin/new_users/accept/<int:ids>/', decorators.admin_required(admin.accept_new_users), name="accept_new_users"),
    path('admin/new_users/reject/', decorators.admin_required(admin.reject_new_users), name="reject_new_users"),
    path('admin/new_users/reject/<int:ids>/', decorators.admin_required(admin.reject_new_users), name="reject_new_users"),
    path('admin/new_users/delete/', decorators.admin_required(admin.delete_new_users), name="delete_new_users"),
    path('admin/new_users/delete/<int:ids>/', decorators.admin_required(admin.delete_new_users), name="delete_new_users"),
]


# IMPORTS Management
urlpatterns += [
    path('admin/manage_imports/', decorators.admin_required(admin.manage_imports), name="manage_imports"),
    path('admin/manage_imports/<str:tab_status>/', decorators.admin_required(admin.manage_imports), name="manage_imports"),
    path('admin/import_data_from_file/', decorators.admin_required(admin.import_data_from_file), name="import_data_from_file"),
    path('admin/delete_record/<str:tab_status>/<int:ins>/', decorators.admin_required(admin.delete_record), name="delete_record"),
    path('admin/edit_record/<str:tab_status>/', decorators.admin_required(admin.edit_record), name="edit_record"),
    path('admin/move_all_to_final/<str:tab_status>/', decorators.admin_required(admin.move_all_to_final), name="move_all_to_final"),
    path('admin/move_to_final/<str:tab_status>/<int:ins>/', decorators.admin_required(admin.move_to_final), name="move_to_final"),
    path('admin/move_data_bg_process/<str:tab_status>/',decorators.admin_required(admin.move_data_bg_process), name="move_data_bg_process"),
    path('admin/show_final_records/', decorators.admin_required(admin.show_final_records), name="show_final_records"),
    path('admin/show_final_records/<str:tab_status>/', decorators.admin_required(admin.show_final_records), name="show_final_records"),
    path('admin/download_missing_accounts_csv/', decorators.admin_required(admin.download_missing_accounts_csv), name="download_missing_accounts_csv"),
    path('admin/delete_selected_records/<str:tab_status>/', decorators.admin_required(admin.delete_selected_records), name="delete_selected_records"),
    path('admin/collateral_upload/', decorators.admin_required(admin.collateral_upload), name="collateral_upload"),
    path('admin/get_collateral_data/<int:ins>/', decorators.admin_required(admin.get_collateral_data), name="get_collateral_data"),
    path('admin/delete_single_collateral_data/', decorators.admin_required(admin.delete_single_collateral_data), name="delete_single_collateral_data"),
    path('admin/delete_all_collaterals/', decorators.admin_required(admin.delete_all_collaterals), name="delete_all_collaterals"),
]

# Output & Reports
urlpatterns += [
    path('admin/show_final/', decorators.admin_required(admin.show_final_records), name="show_final_records"),
    path('admin/show_final/<str:tab_status>/', decorators.admin_required(admin.show_final_records), name="show_final_records"),
    path('admin/show_reports/', decorators.admin_required(admin.show_reports), name='show_reports'),
    path('admin/show_reports/<str:tab_status>/', decorators.admin_required(admin.show_reports), name='show_reports'),
    path('admin/delete_final_records/<str:tab_status>/', decorators.admin_required(admin.delete_final_records), name="delete_final_records"),
    path('admin/delete_report_records/<str:tab_status>/', decorators.admin_required(admin.delete_report_records), name="delete_report_records"),
]

# Process Management
urlpatterns += [
    path('admin/database_management/', decorators.admin_required(dbase.database_management), name='database_management'),
]

#Background tasks
urlpatterns += [
    path('admin/run_pd_report/', decorators.admin_required(admin.pd_report), name='pd_report'),
    path('admin/run_pd_report/<int:s_type>/', decorators.admin_required(admin.pd_report), name='pd_report'),
    path('admin/run_lgd_report/', decorators.admin_required(admin.lgd_report), name='lgd_report'),
    path('admin/run_lgd_report/<int:s_type>/', decorators.admin_required(admin.lgd_report), name='lgd_report'),
    path('admin/run_stage_report/', decorators.admin_required(admin.stage_report), name='stage_report'),
    path('admin/run_stage_report/<int:s_type>/', decorators.admin_required(admin.stage_report), name='stage_report'),
]


#
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
