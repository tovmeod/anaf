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

urlpatterns = patterns('anaf.projects.views',
                       url(r'^/?(\.(?P<response_format>\w+))?$', 'index', name='projects'),
                       url(r'^/', include(patterns('',
                           url(r'^', include(router.urls)),
                           # url(r'^dojo$', 'dojo_view', name='dojo_view'),

                           url(r'^index(\.(?P<response_format>\w+))?/?$', oldviews.index, name='projects_index'),
                           url(r'^task/owned(\.(?P<response_format>\w+))?/?$',
                               oldviews.index_owned, name='projects_index_owned'),
                           url(r'^task/assigned(\.(?P<response_format>\w+))?/?$',
                               oldviews.index_assigned, name='projects_index_assigned'),
                           url(r'^task/in_progress(\.(?P<response_format>\w+))?/?$',
                               oldviews.index_in_progress, name='projects_tasks_in_progress'),

                           # Projects
                           url(r'^add(\.(?P<response_format>\w+))?/?$', oldviews.project_add, name='project_add'),
                           url(r'^add/project/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_add_typed, name='projects_project_add_typed'),
                           url(r'^view/(?P<project_id>\w+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_view, name='projects_project_view'),
                           url(r'^edit/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_edit, name='projects_project_edit'),
                           url(r'^delete/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.project_delete, name='projects_project_delete'),
                           url(r'^gantt/(?P<project_id>\w+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.gantt_view, name='projects_gantt_view'),

                            # Milestones
                           url(r'^milestone/add(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_add, name='projects_milestone_add'),
                           url(r'^milestone/add/project/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_add_typed, name='projects_milestone_add_typed'),
                           url(r'^milestone/view/(?P<milestone_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_view, name='projects_milestone_view'),
                           url(r'^milestone/edit/(?P<milestone_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_edit, name='projects_milestone_edit'),
                           url(r'^milestone/set/(?P<milestone_id>\d+)/status/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_set_status, name='projects_milestone_set_status'),
                           url(r'^milestone/delete/(?P<milestone_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.milestone_delete, name='projects_milestone_delete'),

                           # Tasks
                           url(r'^task/add(\.(?P<response_format>\w+))?/?$', oldviews.task_add, name='projects_task_add'),
                           url(r'^task/add/project/(?P<project_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_add_typed, name='projects_task_add_typed'),
                           url(r'^task/add/milestone/(?P<milestone_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_add_to_milestone, name='projects_task_add_to_milestone'),
                           url(r'^task/view/(?P<task_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_view, name='projects_task_view'),
                           url(r'^task/edit/(?P<task_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_edit, name='projects_task_edit'),
                           url(r'^task/set/(?P<task_id>\d+)/status/(?P<status_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_set_status, name='projects_task_set_status'),
                           url(r'^task/delete/(?P<task_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_delete, name='projects_task_delete'),

                           # Subtask
                           url(r'^task/add/subtask/(?P<task_id>\d+)(\.(?P<response_format>\w+))?/?$',
                               oldviews.task_add_subtask, name='projects_task_add_subtask'),

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
