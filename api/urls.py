from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register_user, name='register'),
    path('login', views.login_user, name='login'),

    # Farmer
    path("farmer/dashboard", views.farmer_dashboard),
    path("farmer/projects", views.farmer_projects),
    path('projects', views.submit_project),
    path('farmer/notifications', views.farmer_notifications),

    # Panchayat
    path('panchayat/dashboard', views.panchayat_dashboard),
    path('panchayat/project-review/<int:project_id>', views.panchayat_project_review),
    path('panchayat/village-map', views.panchayat_village_map),
    path('panchayat/local-farmers', views.panchayat_local_farmers),
    path('verify/approve', views.panchayat_approve),
    path('verify/reject', views.panchayat_reject),

    # Admin
    path("admin/map", views.map_view),
    path('admin/dashboard', views.admin_dashboard),
    path('admin/approve', views.admin_approve),
    path('admin/reject', views.admin_reject),
    path('admin/analytics', views.analytics_dashboard),
    path('admin/export-analytics', views.export_analytics),
    path('admin/credit-requests', views.admin_credit_requests),
    path('admin/approve-credit-request', views.admin_approve_credit_request),
    path('admin/reject-credit-request', views.admin_reject_credit_request),

    # Company marketplace
    path('marketplace', views.marketplace_dashboard),
    path('company/request-farmer-credits', views.request_farmer_credits),
    path('company/request-credits', views.request_bulk_credits),
    path('company/portfolio', views.company_portfolio),
    path('company/certificates', views.company_certificates),
    path('projects/map', views.project_map_data),
    path("certificates/<str:tx_hash>.pdf", views.download_certificate),
]