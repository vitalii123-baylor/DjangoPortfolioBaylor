from django.urls import path
from . import views

app_name = 'group_collab'

urlpatterns = [
    path('',                                views.group_home,           name='home'),
    path('demo-generate/',                  views.demo_generate,        name='demo_generate'),
    path('demo-pdf/',                       views.demo_pdf,             name='demo_pdf'),
    path('demo-extract/',                   views.demo_extract,         name='demo_extract'),
    path('tips/',                           views.get_tips,             name='tips'),
    path('rephrase/',                       views.rephrase_part,        name='rephrase'),
    path('create/',                         views.create_group,         name='create'),
    path('join/',                           views.join_group,           name='join'),
    path('<str:code>/',                     views.group_dashboard,      name='dashboard'),
    path('<str:code>/leave/',               views.leave_group,          name='leave'),
    path('<str:code>/update/',              views.update_group,         name='update'),
    path('<str:code>/kick/<int:member_id>/',views.kick_member,          name='kick'),
    path('<str:code>/role/<int:member_id>/',views.update_role,          name='role'),
    path('<str:code>/open-voting/',         views.open_voting,          name='open_voting'),
    path('<str:code>/vote/',                views.cast_vote,            name='vote'),
    path('<str:code>/close-voting/',        views.close_voting,         name='close_voting'),
    path('<str:code>/generate/',            views.generate_presentation,name='generate'),
    path('<str:code>/upload-pdf/',          views.upload_pdf,           name='upload_pdf'),
    path('<str:code>/notes/<int:part_id>/', views.update_notes,         name='notes'),
    path('<str:code>/status/',              views.poll_status,          name='status'),
]
