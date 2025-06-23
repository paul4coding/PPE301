from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views
from .views import set_rdv_status

urlpatterns = [
    # === AUTHENTIFICATION ===
    path('home/', views.user_home, name="acceuil"),
    path('inscription/', views.inscription, name='inscription'),
    path('connexion/', views.connexion, name='connexion'),
    path('welcome/', views.welcome_view, name='welcome'),

    path('patient/bilan/', views.bilan_patient, name='bilan_patient'),
    path('prescription/<int:prescription_id>/edit/', views.edit_prescription, name='edit_prescription'),
    path('prescription/<int:prescription_id>/delete/', views.delete_prescription, name='delete_prescription'),
    # Dossiers patients
    path('dossiers/', views.liste_dossiers_patients, name='liste_dossiers_patients'),
    path('dossier/creer/', views.creer_dossier_patient, name='creer_dossier_patient'),
    path('dossier/<int:dossier_id>/edit/', views.edit_dossier_patient, name='edit_dossier_patient'),
    path('dossier/<int:dossier_id>/delete/', views.delete_dossier_patient, name='delete_dossier_patient'),

    # Pages (journalières) du dossier patient
    path('dossier/<int:dossier_id>/page/ajouter/', views.add_page_dossier_patient, name='add_page_dossier_patient'),
    path('dossier/page/<int:page_id>/edit/', views.edit_page_dossier_patient, name='edit_page_dossier_patient'),

    # Profil patient (affichage du dossier)
    path('patient/<int:patient_id>/profil/', views.hos_patient_profile, name='hos_patient_profile'),

    # === ADMIN ===
    path('admin_home/', views.admin_home, name='admin_home'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('admin/personnels_a_valider/', views.personnels_a_valider, name='personnels_a_valider'),
    path('admin/valider_personnel/<int:user_id>/', views.valider_personnel, name='valider_personnel'),
    
    path('admin/rendezvous/liste/', views.liste_rendezvous, name='liste_rendezvous'),
    path('admin/rendezvous/modifier/<int:rdv_id>/', views.modifier_rendezvous, name='modifier_rendezvous'),
    path('supprimer/<int:rdv_id>/', views.supprimer_rendezvous, name='supprimer_rendezvous'),


    # === RENDEZ-VOUS ===
    #path('admin/rendezvous/', views.gerer_rendezvous, name='gerer_rendezvous'),  # Gestion par le personnel
    path('admin/rendezvous/ajouter/', views.ajouter_rendezvous, name='ajouter_rendezvous'),
    path('admin/rendezvous/calendrier/', views.hos_events, name='hos_events'),


    # API Rendez-vous (FullCalendar, notifications, etc.)
    #path('api/rendezvous/', views.api_rendezvous, name='rendezvous_api'),  # Calendrier interactif
    #path('api/rendezvous-du-jour/', views.api_rendezvous_du_jour, name='rendezvous_du_jour'),  # Notifications du jour
    
    path('changer-statut/', views.set_rdv_status, name='set_rdv_status'),
    
    path('notifications/', views.all_notifications, name='all_notifications'),

    # === CHARTS ===
    path('charts/chartjs/bar/', views.charts_chartjs_bar, name='charts_chartjs_bar'),
    path('charts/chartjs/line/', views.charts_chartjs_line, name='charts_chartjs_line'),
    path('charts/chartjs/pie-donut/', views.charts_chartjs_pie_donut, name='charts_chartjs_pie_donut'),
    path('charts/echart/bar/', views.charts_echart_bar, name='charts_echart_bar'),
    path('charts/echart/line/', views.charts_echart_line, name='charts_echart_line'),
    path('charts/flot/area/', views.charts_flot_area, name='charts_flot_area'),
    path('charts/flot/line/', views.charts_flot_line, name='charts_flot_line'),
    path('charts/flot/stacked/', views.charts_flot_stacked, name='charts_flot_stacked'),
    path('charts/morris/area/', views.charts_morris_area, name='charts_morris_area'),
    path('charts/morris/bar/', views.charts_morris_bar, name='charts_morris_bar'),
    path('charts/morris/line/', views.charts_morris_line, name='charts_morris_line'),
    path('charts/morris/pie/', views.charts_morris_pie, name='charts_morris_pie'),
    path('charts/sparkline/bar/', views.charts_sparkline_bar, name='charts_sparkline_bar'),
    path('charts/sparkline/composite/', views.charts_sparkline_composite, name='charts_sparkline_composite'),
    path('charts/sparkline/line/', views.charts_sparkline_line, name='charts_sparkline_line'),

    # === facture et resultat  ===
    path('factures/', views.liste_factures, name='liste_factures'),
    path('facture/<int:facture_id>/', views.detail_facture, name='detail_facture'),
    path('facture/<int:facture_id>/edit/', views.edit_facture, name='edit_facture'),
    path('facture/<int:facture_id>/delete/', views.delete_facture, name='delete_facture'),

    path('facture/creer/', views.creer_facture, name='creer_facture'),
    path('facture/<int:facture_id>/ajouter-ligne/', views.ajouter_ligne_facture, name='ajouter_ligne_facture'),
    path('ligne/<int:ligne_id>/ajouter-resultat/', views.ajouter_resultat, name='ajouter_resultat'),
    path('resultat/<int:resultat_id>/ajouter-prescription/', views.ajouter_prescription, name='ajouter_prescription'),
    path('resultat/<int:resultat_id>/edit/', views.edit_resultat, name='edit_resultat'),
    path('resultat/<int:resultat_id>/delete/', views.delete_resultat, name='delete_resultat'),

    # === FORMULAIRES ===
    path('form/elements/grid/', views.form_elements_grid, name='form_elements_grid'),
    path('form/elements/icheck/', views.form_elements_icheck, name='form_elements_icheck'),
    path('form/elements/premade/', views.form_elements_premade, name='form_elements_premade'),
    path('form/elements/', views.form_elements, name='form_elements'),
    path('form/validation/', views.form_validation, name='form_validation'),
    path('form/wizard/', views.form_wizard, name='form_wizard'),

    # === HOSPITAL/ADMIN ===
    path('hos/add-doctor/', views.hos_add_doctor, name='hos_add_doctor'),
    path('hos/add-patient/', views.hos_add_patient, name='hos_add_patient'),
    path('hos/add-payment/', views.hos_add_payment, name='hos_add_payment'),
    path('hos/all-doctors/', views.hos_all_doctors, name='hos_all_doctors'),
    path('hos/all-patients/', views.hos_all_patients, name='hos_all_patients'),
    path('hos/book-appointment/', views.hos_book_appointment, name='hos_book_appointment'),
    path('health/hos/doctor-profile/<int:medecin_id>/', views.hos_doctor_profile, name='hos_doctor_profile'),
    path('hos/delete-doctor/<int:medecin_id>/', views.hos_delete_doctor, name='hos_delete_doctor'),
    path('hos/edit-doctor/<int:medecin_id>/', views.hos_edit_doctor, name='hos_edit_doctor'),
    path('health/hos/edit-patient/<int:patient_id>/', views.hos_edit_patient, name='hos_edit_patient'),
    path('hos/delete-patient/<int:patient_id>/', views.hos_delete_patient, name='hos_delete_patient'),
    path('hos/events/', views.hos_events, name='hos_events'),
    path('hos/faq/', views.hos_faq, name='hos_faq'),
    path('hos/patient-dash/', views.hos_patient_dash, name='hos_patient_dash'),
    path('hos/patient-invoice/', views.hos_patient_invoice, name='hos_patient_invoice'),
    path('hos/patient-profile/<int:patient_id>/', views.hos_patient_profile, name='hos_patient_profile'),
    path('hos/patients/', views.hos_patients, name='hos_patients'),
    path('hos/payment/', views.hos_payment, name='hos_payment'),
    path('hos/schedule/', views.hos_schedule, name='hos_schedule'),
    
    path('api/rendezvous/', views.api_rendezvous, name='api_rendezvous'),
    
    path('hos/staff-profile/', views.hos_staff_profile, name='hos_staff_profile'),
    path('hos/support/', views.hos_support, name='hos_support'),

    # === INDEX ===
    path('dashboard/', views.index_dashboard, name='index_dashboard'),
    path('', views.index, name='index'),

    # === UI ===
    path('ui/404/', views.ui_404, name='ui_404'),
    path('ui/accordion/', views.ui_accordion, name='ui_accordion'),
    path('ui/alerts/', views.ui_alerts, name='ui_alerts'),
    path('ui/breadcrumbs/', views.ui_breadcrumbs, name='ui_breadcrumbs'),
    path('ui/buttons/', views.ui_buttons, name='ui_buttons'),
    path('ui/dropdowns/', views.ui_dropdowns, name='ui_dropdowns'),
    path('ui/faq/', views.ui_faq, name='ui_faq'),
    path('ui/fontawesome/', views.ui_fontawesome, name='ui_fontawesome'),
    path('ui/glyphicons/', views.ui_glyphicons, name='ui_glyphicons'),
    path('ui/grids/', views.ui_grids, name='ui_grids'),
    path('ui/group-list/', views.ui_group_list, name='ui_group_list'),
    path('ui/icons/', views.ui_icons, name='ui_icons'),
    path('ui/labels-badges/', views.ui_labels_badges, name='ui_labels_badges'),
    path('ui/login/', views.ui_login, name='ui_login'),
    path('ui/modals/', views.ui_modals, name='ui_modals'),
    path('ui/navbars/', views.ui_navbars, name='ui_navbars'),
    path('ui/notifications/', views.ui_notifications, name='ui_notifications'),
    path('ui/pagination/', views.ui_pagination, name='ui_pagination'),
    path('ui/panels/', views.ui_panels, name='ui_panels'),
    path('ui/popovers/', views.ui_popovers, name='ui_popovers'),
    path('ui/pricing-expanded/', views.ui_pricing_expanded, name='ui_pricing_expanded'),
    path('ui/pricing-narrow/', views.ui_pricing_narrow, name='ui_pricing_narrow'),
    path('ui/progress/', views.ui_progress, name='ui_progress'),
    path('ui/register/', views.ui_register, name='ui_register'),
    path('ui/tabs/', views.ui_tabs, name='ui_tabs'),
    path('ui/timeline-centered/', views.ui_timeline_centered, name='ui_timeline_centered'),
    path('ui/timeline-left/', views.ui_timeline_left, name='ui_timeline_left'),
    path('ui/tooltips/', views.ui_tooltips, name='ui_tooltips'),
    path('ui/typography/', views.ui_typography, name='ui_typography'),
]
