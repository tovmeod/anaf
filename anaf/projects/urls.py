"""URLs for the Projects module
For most part I just use the DefaultRouter for DRF, for some views I need to set manually
This may seem verbose, and I considered to make a function to generate the regexes,
but I felt that this would hide the regex for someone searching for it, so I chose to make them explicit
"""
from __future__ import unicode_literals
from django.conf.urls import url, patterns, include
from anaf.projects import views_new
from anaf.routers import BetterRouter

router = BetterRouter()
router.include_root_view = False
router.register(r'project', views_new.ProjectView)
router.register(r'taskstatus', views_new.TaskStatusView)
router.register(r'milestone', views_new.MilestoneView)
router.register(r'task', views_new.TaskView)
router.register(r'tasktimeslot', views_new.TaskTimeSlotView)

urlpatterns = patterns('anaf.projects.views',
                       # url(r'^/?(\.(?P<response_format>\w+))?$', oldviews.index, name='projects'),
                       url(r'^/', include(patterns('',
                           url(r'^', include(router.urls)),

                       # [u'projects/task/(?P<pk>[^/.]+)/status\\.(?P<format>[a-z0-9]+)/?$', u'projects/task/(?P<pk>[^/.]+)/status/$']
                           # url(r'^dojo$', 'dojo_view', name='dojo_view'),

                           # Project:
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+)/$',
                               views_new.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),

                           # Milestone:
                           url(r'^milestone/new_to_project/(?P<project_id>[^/.]+)/$',
                               views_new.MilestoneView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='milestone-new-to-project'),
                           url(r'^milestone/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.MilestoneView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='milestone-new-to-project'),
                           url(r'^milestone/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+)/$',
                               views_new.MilestoneView.as_view({'get': 'set_status'}), name='milestone-set-status'),
                           url(r'^milestone/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.MilestoneView.as_view({'get': 'set_status'}), name='milestone-set-status'),
                           url(r'^milestone/(?P<pk>[^/.]+)/$',
                               views_new.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),
                           url(r'^milestone/(?P<pk>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),

                           # Task:
                           url(r'^task/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+)/$',
                               views_new.TaskView.as_view({'get': 'set_status'}), name='task-set-status'),
                           url(r'^task/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.TaskView.as_view({'get': 'set_status'}), name='task-set-status'),
                           url(r'^task/new_to_milestone/(?P<milestone_id>[^/.]+)/$',
                               views_new.TaskView.as_view({'get': 'new_to_milestone', 'post': 'new_to_milestone'}),
                               name='task-new-to-milestone'),
                           url(r'^task/new_to_milestone/(?P<milestone_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.TaskView.as_view({'get': 'new_to_milestone', 'post': 'new_to_milestone'}),
                               name='task-new-to-milestone'),
                           url(r'^task/new_to_project/(?P<project_id>[^/.]+)/$',
                               views_new.TaskView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='task-new-to-project'),
                           url(r'^task/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.TaskView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='task-new-to-project'),
                           url(r'^task/status/(?P<status_id>[^/.]+)/$',
                               views_new.TaskView.as_view({'get': 'status', 'post': 'status'}), name='task-status'),
                           url(r'^task/status/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.TaskView.as_view({'get': 'status', 'post': 'status'}), name='task-status'),

                           # Times Slots
                           url(r'^tasktimeslot/new_to_task/(?P<task_id>[^/.]+)/$',
                               views_new.TaskTimeSlotView.as_view({'get': 'new_to_task', 'post': 'new_to_task'}),
                               name='tasktimeslot-new-to-task'),
                           url(r'^tasktimeslot/new_to_task/(?P<task_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views_new.TaskTimeSlotView.as_view({'get': 'new_to_task', 'post': 'new_to_task'}),
                               name='tasktimeslot-new-to-task'),

                           # Settings
                           url(r'^settings/edit/$',
                               views_new.ProjectsSettingsView.as_view({'get': 'edit'}), name='projectssettings-edit'),
                           url(r'^settings/edit.(?P<format>[a-z0-9]+)/?$',
                               views_new.ProjectsSettingsView.as_view({'get': 'edit'}), name='projectssettings-edit'),
                           url(r'^settings/$',
                               views_new.ProjectsSettingsView.as_view({'get': 'view'}), name='projectssettings-view'),
                           url(r'^settings.(?P<format>[a-z0-9]+)/?$',
                               views_new.ProjectsSettingsView.as_view({'get': 'view'}), name='projectssettings-view'),
                       )))
                       )
