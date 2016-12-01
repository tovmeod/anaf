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

route_list = (
    (r'project', views.ProjectView),
    (r'taskstatus', views.TaskStatusView),
    (r'milestone', views.MilestoneView),
    (r'task', views.TaskView),
    (r'tasktimeslot', views.TaskTimeSlotView)
)

urlpatterns = patterns('anaf.projects.views',
                       url(r'^/?(\.(?P<response_format>\w+))?$', oldviews.index, name='projects'),
                       url(r'^/', include(patterns('',
                           url(r'^', include(router.urls)),
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

                           url(r'^index(\.(?P<response_format>\w+))?/?$', oldviews.index, name='projects_index'),

                           # Project:
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+)/$',
                               views.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),
                           url(r'^project/new_to_project/(?P<project_id>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.ProjectView.as_view({'get': 'new_to_project', 'post': 'new_to_project'}),
                               name='project-new-to-project'),

                           url(r'^view/(?P<project_id>\w+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_view, name='projects_project_view'),
                           url(r'^edit/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_edit, name='projects_project_edit'),
                           url(r'^delete/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_delete, name='projects_project_delete'),
                           url(r'^gantt/(?P<project_id>\w+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.gantt_view, name='projects_gantt_view'),

                            # Milestones
                           url(r'^milestone/(?P<pk>[^/.]+)/$',
                               views.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),
                           url(r'^milestone/(?P<pk>[^/.]+).(?P<format>[a-z0-9]+)/?$',
                               views.MilestoneView.as_view({'get': 'retrieve', 'post': 'retrieve'}),
                               name='milestone-detail'),

                           # Times Slots
                           url(r'^task/time/(?P<task_id>\w+)/add(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_add, name='projects_task_time_slot_add'),
                           url(r'^task/time/(?P<task_id>\w+)/start(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_start, name='projects_task_time_slot_start'),

                           url(r'^task/time/stop/(?P<slot_id>\w+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_stop, name='projects_task_time_slot_stop'),
                           url(r'^task/time/view/(?P<time_slot_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_view, name='projects_task_time_slot_view'),
                           url(r'^task/time/edit/(?P<time_slot_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_edit, name='projects_task_time_slot_edit'),
                           url(r'^task/delete/time/(?P<time_slot_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_time_slot_delete, name='projects_task_time_slot_delete'),

                           # Task Statuses
                           url(r'^task/status/add(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_status_add, name='projects_task_status_add'),
                           url(r'^task/status/view/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.index_by_status, name='projects_index_by_status'),
                           url(r'^task/status/edit/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_status_edit, name='projects_task_status_edit'),
                           url(r'^task/status/delete/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_status_delete, name='projects_task_status_delete'),

                            # Settings
                           url(r'^settings/view(\.(?P<response_format>\w+))?/?$',
                               oldviews.settings_view, name='projects_settings_view'),
                           url(r'^settings/edit(\.(?P<response_format>\w+))?/?$',
                               oldviews.settings_edit, name='projects_settings_edit'),

                           # AJAX lookups
                           url(r'^ajax/tasks(\.(?P<response_format>\w+))?/?$',
                               oldviews.ajax_task_lookup, name='projects_ajax_task_lookup'),
                       )))
                       )
