
from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from django.conf.urls.static import static
from django.conf import settings
from . import views
from . import administrators as admin
from . import database_management as dbase
from . import decorators

from . import algorithm_configs as algocnf

# Authorization
urlpatterns = [
    path('', views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(template_name = 'base/logout.html'), name = 'logout'),
    re_path(r'^accounts/*', RedirectView.as_view(pattern_name='login', permanent=True)),
    path('change_password/', views.change_password, name='change_password'),
    path('signup/', views.signup, name='signup'),
    path('reset_password/<int:ins>/', views.reset_password, name='reset_password'),
    path('admin/create_superuser/', views.create_superuser, name='create_superuser'),
]

# ADMIN PAGES
urlpatterns += [
    path('admin/dashboard/', decorators.admin_required(admin.dashboard), name="admin_dashboard"),
    path('user/dashboard/', admin.user_dashboard, name="user_dashboard"),
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
    path('admin/manage_imports/', admin.manage_imports, name="manage_imports"),
    path('admin/manage_imports/<str:tab_status>/', admin.manage_imports, name="manage_imports"),
    path('admin/import_data_from_file/', admin.import_data_from_file, name="import_data_from_file"),
    path('admin/delete_record/<str:tab_status>/<int:ins>/', decorators.admin_required(admin.delete_record), name="delete_record"),
    path('admin/edit_record/<str:tab_status>/', admin.edit_record, name="edit_record"),
    path('admin/move_all_to_final/<str:tab_status>/', admin.move_all_to_final, name="move_all_to_final"),
    path('admin/move_to_final/<str:tab_status>/<int:ins>/', admin.move_to_final, name="move_to_final"),
    path('admin/move_data_bg_process/<str:tab_status>/',admin.move_data_bg_process, name="move_data_bg_process"),
    path('admin/show_final_records/', admin.show_final_records, name="show_final_records"),
    path('admin/show_final_records/<str:tab_status>/', admin.show_final_records, name="show_final_records"),
    path('admin/download_missing_accounts_csv/', admin.download_missing_accounts_csv, name="download_missing_accounts_csv"),
    path('admin/delete_selected_records/<str:tab_status>/', decorators.admin_required(admin.delete_selected_records), name="delete_selected_records"),
    path('admin/collateral_upload/', admin.collateral_upload, name="collateral_upload"),
    path('admin/get_collateral_data/<int:ins>/', decorators.admin_required(admin.get_collateral_data), name="get_collateral_data"),
    path('admin/delete_single_collateral_data/', decorators.admin_required(admin.delete_single_collateral_data), name="delete_single_collateral_data"),
    path('admin/delete_all_collaterals/', decorators.admin_required(admin.delete_all_collaterals), name="delete_all_collaterals"),
    path('admin/show_collateral_mapping/', decorators.admin_required(admin.show_collateral_mapping), name="show_collateral_mapping"),
    path('admin/delete_collateral/', decorators.admin_required(admin.delete_collateral), name="delete_collateral"),
    path('admin/edit_collateral/', decorators.admin_required(admin.edit_collateral), name="edit_collateral"),
]

# Output & Reports
urlpatterns += [
    path('admin/show_final/', admin.show_final_records, name="show_final_records"),
    path('admin/show_final/<str:tab_status>/', admin.show_final_records, name="show_final_records"),
    path('admin/show_reports/', admin.show_reports, name='show_reports'),
    path('admin/show_reports/<str:tab_status>/', admin.show_reports, name='show_reports'),
    path('admin/delete_final_records/<str:tab_status>/', decorators.admin_required(admin.delete_final_records), name="delete_final_records"),
    path('admin/delete_final_single_record/<str:tab_status>/<int:ins>/', decorators.admin_required(admin.delete_final_single_record), name="delete_final_single_record"),
    path('admin/delete_report_records/<str:tab_status>/', decorators.admin_required(admin.delete_report_records), name="delete_report_records"),
    path('admin/delete_report_single_record/<str:tab_status>/<int:ins>/', decorators.admin_required(admin.delete_report_single_record), name="delete_report_single_record"),
    path('admin/download_reports/<str:tab_status>/<int:ftype>/', decorators.admin_required(admin.download_reports), name="download_reports"),
    path('admin/download_ecl_missing_reports/<int:ftype>/', decorators.admin_required(admin.download_missing_ecl), name="download_missing_ecl"),
]

# Process Management
urlpatterns += [
    path('admin/database_management/', decorators.admin_required(dbase.database_management), name='database_management'),
    path('admin/show_audit_trail/', decorators.admin_required(admin.show_audit_trail), name='show_audit_trail'),
    path('admin/delete_audit_trails/', decorators.admin_required(admin.delete_audit_trails), name="delete_audit_trails"),
    path('admin/delete_audit_trail_single/', decorators.admin_required(admin.delete_audit_trail_single), name="delete_audit_trail_single"),
    path('admin/show_missing_ecl/', decorators.admin_required(admin.show_missing_ecl), name="show_missing_ecl"),
    path('admin/delete_missing_ecl/', decorators.admin_required(admin.delete_missing_ecl), name="delete_missing_ecl"),

]

#Background tasks
urlpatterns += [
    path('admin/run_pd_report/', admin.pd_report, name='pd_report'),
    path('admin/run_pd_report/<int:s_type>/', admin.pd_report, name='pd_report'),
    path('admin/run_lgd_report/', admin.lgd_report, name='lgd_report'),
    path('admin/run_lgd_report/<int:s_type>/', admin.lgd_report, name='lgd_report'),
    path('admin/run_stage_report/', admin.stage_report, name='stage_report'),
    path('admin/run_stage_report/<int:s_type>/', admin.stage_report, name='stage_report'),
    path('admin/run_ead_report/', admin.ead_report, name='ead_report'),
    path('admin/run_ead_report/<int:s_type>/', admin.ead_report, name='ead_report'),
    path('admin/run_ecl_report/', admin.ecl_report, name='ecl_report'),
    path('admin/run_ecl_report/<int:s_type>/', admin.ecl_report, name='ecl_report'),
    path('admin/run_eir_report/', admin.eir_report, name='eir_report'),
    path('admin/run_eir_report/<int:s_type>/', admin.eir_report, name='eir_report'),
]


#Configurations Of Algorithm
urlpatterns += [
    path('admin/load_predefined_variables/', decorators.admin_required(algocnf.load_predefined_variables), name='load_predefined_variables'),
    path('algocnf/configure_templates/', decorators.admin_required(algocnf.ConfigureTemplates.as_view()), name="configure_templates"),
    path('algocnf/configure_templates/<str:tab_status>/', decorators.admin_required(algocnf.ConfigureTemplates.as_view()), name="configure_templates"),
    path('algocnf/configure_templates/<str:tab_status>/<int:template_id>/', decorators.admin_required(algocnf.ConfigureTemplates.as_view()), name="configure_templates"),
    path('algocnf/configure_templates/<int:ins>/delete/', decorators.admin_required(algocnf.delete_template), name="delete_template"),
    path('algocnf/delete_column/<int:ins>/', decorators.admin_required(algocnf.delete_column_algoconfig), name="delete_column_algoconfig"),
    path('admin/pd_module_testing/', decorators.admin_required(algocnf.pd_module_testing), name='pd_module_testing'),
    path('admin/pd_module_testing/<int:algo_type>/', decorators.admin_required(algocnf.pd_module_testing), name='pd_module_testing'),
]

#
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)


