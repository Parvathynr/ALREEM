
from django.urls import path
from . import views


urlpatterns = [
    path('admin_login', views.admin_login, name='admin_login'),           #done
    path('admin_logout', views.admin_logout, name='admin_logout'),        #done
    path('add_member', views.add_member, name='add_member'),              #done
    path('update_member/<int:id>', views.update_member, name='update_member'),   #done
    path('delete_member/<int:id>', views.delete_member, name='delete_member'),    #done
    path('add_plan', views.add_plan, name='add_plan'),                          #done                 
    path('view_plans', views.view_plans, name='view_plans'),                    #done
    path('edit_plan/<int:id>', views.edit_plan, name='edit_plan'),              #done
    path('delete_plan/<int:id>',views.delete_plan, name='delete_plan'),             #done 
    path('view_members', views.view_members, name='view_members'),              #done
    path('add_trainer_staff', views.add_trainer_staff, name='add_trainer_staff'),   #done
    path('view_all_trainers_staff', views.view_all_trainers_staff, name='view_all_trainers_staff'), #done without photo
    path('view_single_trainer_staff/<int:id>', views.view_single_trainer_staff, name='view_single_trainer_staff'),  #done
    path('edit_trainer_staff/<int:id>', views.edit_trainer_staff, name='edit_trainer_staff'), #done
    path('delete_trainer_staff/<int:id>', views.delete_trainer_staff, name='delete_trainer_staff'), #done
    path('add_branch', views.add_branch, name='add_branch')

]
