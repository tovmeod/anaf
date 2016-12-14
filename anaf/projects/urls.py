from django.conf.urls import url, patterns, include
from rest_framework.routers import DefaultRouter
from anaf.projects.api import views
from anaf.projects import views as oldviews

router = DefaultRouter()
router.include_root_view = False
router.register(r'project', views.ProjectView)
router.register(r'taskstatus', views.TaskStatusView)
router.register(r'milestone', views.MilestoneView)
router.register(r'task', views.TaskView)
router.register(r'tasktimeslot', views.TaskTimeSlotView)
# router.register(r'settings', views.ProjectsSettingsView)

urlpatterns = patterns('anaf.projects.views',
                       # url(r'^/?(\.(?P<response_format>\w+))?$', oldviews.index, name='projects'),
                       url(r'^/', include(patterns('',
                           url(r'^', include(router.urls)),

                           # Task Statuses
                           # because of limitation on DRF I need to set some views manually
                           # TODO: use drf-nested-routers or drf-extensions for nested routes support
                           # Task:
                           url(r'^task/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+)/$',
                               views.TaskView.as_view({'get': 'set_status'}), name='task-set-status'),
                           url(r'^task/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.TaskView.as_view({'get': 'set_status'}), name='task-set-status'),
                           url(r'^task/new_to_milestone/(?P<milestone_id>[^/.]+)/$',
                               views.TaskView.as_view({'get': 'new_to_milestone', 'post': 'new_to_milestone'}),
                               name='task-new-to-milestone'),
                           url(r'^task/new_to_milestone/(?P<milestone_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.TaskView.as_view({'get': 'new_to_milestone', 'post': 'new_to_milestone'}),
                               name='task-new-to-milestone'),
                           url(r'^task/new_to_project/(?P<project_id>[^/.]+)/$',
                               views.TaskView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='task-new-to-project'),
                           url(r'^task/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.TaskView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='task-new-to-project'),
                           url(r'^task/status/(?P<status_id>[^/.]+)/$',
                               views.TaskView.as_view({'get': 'status', 'post': 'status'}), name='task-status'),
                           url(r'^task/status/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.TaskView.as_view({'get': 'status', 'post': 'status'}), name='task-status'),

                           # Milestone:
                           url(r'^milestone/new_to_project/(?P<project_id>[^/.]+)/$',
                               views.MilestoneView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='milestone-new-to-project'),
                           url(r'^milestone/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.MilestoneView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='milestone-new-to-project'),
                           url(r'^milestone/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+)/$',
                               views.MilestoneView.as_view({'get': 'set_status'}), name='milestone-set-status'),
                           url(r'^milestone/(?P<pk>[^/.]+)/setstatus/(?P<status_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.MilestoneView.as_view({'get': 'set_status'}), name='milestone-set-status'),


                       # [u'projects/task/(?P<pk>[^/.]+)/status\\.(?P<format>[a-z0-9]+)/?$', u'projects/task/(?P<pk>[^/.]+)/status/$']
                           # url(r'^dojo$', 'dojo_view', name='dojo_view'),

                           # Project:
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+)/$',
                               views.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),

                           # Milestones
                           url(r'^milestone/(?P<pk>[^/.]+)/$',
                               views.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),
                           url(r'^milestone/(?P<pk>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),

                           # Times Slots
                           url(r'^tasktimeslot/new_to_task/(?P<task_id>[^/.]+)/$',
                               views.TaskTimeSlotView.as_view({'get': 'new_to_task', 'post': 'new_to_task'}),
                               name='tasktimeslot-new-to-task'),
                           url(r'^tasktimeslot/new_to_task/(?P<task_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.TaskTimeSlotView.as_view({'get': 'new_to_task', 'post': 'new_to_task'}),
                               name='tasktimeslot-new-to-task'),

                           # Settings

                           url(r'^settings/edit/$',
                               views.ProjectsSettingsView.as_view({'get': 'edit'}), name='projectssettings-edit'),
                           url(r'^settings/edit.(?P<format>[a-z0-9]+)/?$',
                               views.ProjectsSettingsView.as_view({'get': 'edit'}), name='projectssettings-edit'),
                           url(r'^settings/$',
                               views.ProjectsSettingsView.as_view({'get': 'view'}), name='projectssettings-view'),
                           url(r'^settings.(?P<format>[a-z0-9]+)/?$',
                               views.ProjectsSettingsView.as_view({'get': 'view'}), name='projectssettings-view'),

                           # AJAX lookups
                           url(r'^ajax/tasks(\.(?P<response_format>\w+))?/?$',
                               oldviews.ajax_task_lookup, name='projects_ajax_task_lookup'),
                       )))
                       )
