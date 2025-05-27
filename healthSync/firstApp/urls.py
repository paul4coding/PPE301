from django.contrib import admin
from django.urls import path, include
from . import views

urlpatterns = [
    
   #/store/acceuil: URL menant à la page Acceuil utilisateur
   path('home/', views.user_home, name="acceuil"),
   
   path('inscription/', views.inscription, name='inscription'),

   path('connexion/', views.connexion, name='connexion'), 

   path('welcome/', views.welcome_view, name='welcome'),
   
# Admin URL
   path('admin_home/', views.admin_home, name='admin_home'),


   path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),


   path('admin/personnels_a_valider/', views.personnels_a_valider, name='personnels_a_valider'),
    path('admin/valider_personnel/<int:user_id>/', views.valider_personnel, name='valider_personnel'),
    

    

    # --- CHARTS ---
    path('charts/chartjs/bar/', views.charts_chartjs_bar, name='charts_chartjs_bar'),  # charts-chartjs-bar.html
    path('charts/chartjs/line/', views.charts_chartjs_line, name='charts_chartjs_line'),  # charts-chartjs-line.html
    path('charts/chartjs/pie-donut/', views.charts_chartjs_pie_donut, name='charts_chartjs_pie_donut'),  # charts-chartjs-pie-donut.html
    path('charts/echart/bar/', views.charts_echart_bar, name='charts_echart_bar'),  # charts-echart-bar.html
    path('charts/echart/line/', views.charts_echart_line, name='charts_echart_line'),  # charts-echart-line.html
    path('charts/flot/area/', views.charts_flot_area, name='charts_flot_area'),  # charts-flot-area.html
    path('charts/flot/line/', views.charts_flot_line, name='charts_flot_line'),  # charts-flot-line.html
    path('charts/flot/stacked/', views.charts_flot_stacked, name='charts_flot_stacked'),  # charts-flot-stacked.html
    path('charts/morris/area/', views.charts_morris_area, name='charts_morris_area'),  # charts-morris-area.html
    path('charts/morris/bar/', views.charts_morris_bar, name='charts_morris_bar'),  # charts-morris-bar.html
    path('charts/morris/line/', views.charts_morris_line, name='charts_morris_line'),  # charts-morris-line.html
    path('charts/morris/pie/', views.charts_morris_pie, name='charts_morris_pie'),  # charts-morris-pie.html
    path('charts/sparkline/bar/', views.charts_sparkline_bar, name='charts_sparkline_bar'),  # charts-sparkline-bar.html
    path('charts/sparkline/composite/', views.charts_sparkline_composite, name='charts_sparkline_composite'),  # charts-sparkline-composite.html
    path('charts/sparkline/line/', views.charts_sparkline_line, name='charts_sparkline_line'),  # charts-sparkline-line.html

    # --- FORM ---
    path('form/elements/grid/', views.form_elements_grid, name='form_elements_grid'),  # form-elements-grid.html
    path('form/elements/icheck/', views.form_elements_icheck, name='form_elements_icheck'),  # form-elements-icheck.html
    path('form/elements/premade/', views.form_elements_premade, name='form_elements_premade'),  # form-elements-premade.html
    path('form/elements/', views.form_elements, name='form_elements'),  # form-elements.html
    path('form/validation/', views.form_validation, name='form_validation'),  # form-validation.html
    path('form/wizard/', views.form_wizard, name='form_wizard'),  # form-wizard.html

    # --- HOSPITAL/ADMIN ---
    path('hos/add-doctor/', views.hos_add_doctor, name='hos_add_doctor'),  # hos-add-doctor.html
    path('hos/add-patient/', views.hos_add_patient, name='hos_add_patient'),  # hos-add-patient.html
    path('hos/add-payment/', views.hos_add_payment, name='hos_add_payment'),  # hos-add-payment.html
    path('hos/all-doctors/', views.hos_all_doctors, name='hos_all_doctors'),  # hos-all-doctors.html
    path('hos/all-patients/', views.hos_all_patients, name='hos_all_patients'),  # hos-all-patients.html
    path('hos/book-appointment/', views.hos_book_appointment, name='hos_book_appointment'),  # hos-book-appointment.html
    path('hos/doctor-dash/', views.hos_doctor_dash, name='hos_doctor_dash'),  # hos-doctor-dash.html
    path('hos/doctor-profile/', views.hos_doctor_profile, name='hos_doctor_profile'),  # hos-doctor-profile.html
    path('hos/edit-doctor/', views.hos_edit_doctor, name='hos_edit_doctor'),  # hos-edit-doctor.html
    path('hos/edit-patient/', views.hos_edit_patient, name='hos_edit_patient'),  # hos-edit-patient.html
    path('hos/events/', views.hos_events, name='hos_events'),  # hos-events.html
    path('hos/faq/', views.hos_faq, name='hos_faq'),  # hos-faq.html
    path('hos/patient-dash/', views.hos_patient_dash, name='hos_patient_dash'),  # hos-patient-dash.html
    path('hos/patient-invoice/', views.hos_patient_invoice, name='hos_patient_invoice'),  # hos-patient-invoice.html
    path('patients/<int:id_patient>/', views.hos_patient_profile, name='hos_patient_profile'),  # hos-patient-profile.html
    path('hos/patients/', views.hos_patients, name='hos_patients'),  # hos-patients.html
    path('hos/payment/', views.hos_payment, name='hos_payment'),  # hos-payment.html
    path('hos/schedule/', views.hos_schedule, name='hos_schedule'),  # hos-schedule.html
    path('hos/staff-profile/', views.hos_staff_profile, name='hos_staff_profile'),  # hos-staff-profile.html
    path('hos/support/', views.hos_support, name='hos_support'),  # hos-support.html

    # --- INDEX ---
    path('dashboard/', views.index_dashboard, name='index_dashboard'),  # index-dashboard.html
    path('', views.index, name='index'),  # index.html (accueil)

    # --- UI ---
    path('ui/404/', views.ui_404, name='ui_404'),  # ui-404.html
    path('ui/accordion/', views.ui_accordion, name='ui_accordion'),  # ui-accordion.html
    path('ui/alerts/', views.ui_alerts, name='ui_alerts'),  # ui-alerts.html
    path('ui/breadcrumbs/', views.ui_breadcrumbs, name='ui_breadcrumbs'),  # ui-breadcrumbs.html
    path('ui/buttons/', views.ui_buttons, name='ui_buttons'),  # ui-buttons.html
    path('ui/dropdowns/', views.ui_dropdowns, name='ui_dropdowns'),  # ui-dropdowns.html
    path('ui/faq/', views.ui_faq, name='ui_faq'),  # ui-faq.html
    path('ui/fontawesome/', views.ui_fontawesome, name='ui_fontawesome'),  # ui-fontawesome.html
    path('ui/glyphicons/', views.ui_glyphicons, name='ui_glyphicons'),  # ui-glyphicons.html
    path('ui/grids/', views.ui_grids, name='ui_grids'),  # ui-grids.html
    path('ui/group-list/', views.ui_group_list, name='ui_group_list'),  # ui-group-list.html
    path('ui/icons/', views.ui_icons, name='ui_icons'),  # ui-icons.html
    path('ui/labels-badges/', views.ui_labels_badges, name='ui_labels_badges'),  # ui-labels-badges.html
    path('ui/login/', views.ui_login, name='ui_login'),  # ui-login.html
    path('ui/modals/', views.ui_modals, name='ui_modals'),  # ui-modals.html
    path('ui/navbars/', views.ui_navbars, name='ui_navbars'),  # ui-navbars.html
    path('ui/notifications/', views.ui_notifications, name='ui_notifications'),  # ui-notifications.html
    path('ui/pagination/', views.ui_pagination, name='ui_pagination'),  # ui-pagination.html
    path('ui/panels/', views.ui_panels, name='ui_panels'),  # ui-panels.html
    path('ui/popovers/', views.ui_popovers, name='ui_popovers'),  # ui-popovers.html
    path('ui/pricing-expanded/', views.ui_pricing_expanded, name='ui_pricing_expanded'),  # ui-pricing-expanded.html
    path('ui/pricing-narrow/', views.ui_pricing_narrow, name='ui_pricing_narrow'),  # ui-pricing-narrow.html
    path('ui/progress/', views.ui_progress, name='ui_progress'),  # ui-progress.html
    path('ui/register/', views.ui_register, name='ui_register'),  # ui-register.html
    path('ui/tabs/', views.ui_tabs, name='ui_tabs'),  # ui-tabs.html
    path('ui/timeline-centered/', views.ui_timeline_centered, name='ui_timeline_centered'),  # ui-timeline-centered.html
    path('ui/timeline-left/', views.ui_timeline_left, name='ui_timeline_left'),  # ui-timeline-left.html
    path('ui/tooltips/', views.ui_tooltips, name='ui_tooltips'),  # ui-tooltips.html
    path('ui/typography/', views.ui_typography, name='ui_typography'),  # ui-typography.html


]