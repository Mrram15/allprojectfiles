from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
	       path('AdminLogin.html', views.AdminLogin, name="AdminLogin"), 
	       path('UserLogin.html', views.UserLogin, name="UserLogin"),
	       path('Register.html', views.Register, name="Register"), 
	       path('AdminLoginAction', views.AdminLoginAction, name="AdminLoginAction"), 
	       path('UserLoginAction', views.UserLoginAction, name="UserLoginAction"), 
	       path('RegisterAction', views.RegisterAction, name="RegisterAction"),
	       path('AreaChoose', views.AreaChoose, name="AreaChoose"), 
	       path('ChooseSlot', views.ChooseSlot, name="ChooseSlot"), 
	       path('SlotRelease', views.SlotRelease, name="SlotRelease"), 
	       path('AreaModify', views.AreaModify, name="AreaModify"), 
	       path('AddArea', views.AddArea, name="AddArea"), 
	       path('AddAreaAction', views.AddAreaAction, name="AddAreaAction"), 
	       path('ModifyArea', views.ModifyArea, name="ModifyArea"), 
	       path('ModifyAreaAction', views.ModifyAreaAction, name="ModifyAreaAction"), 

	       path('ViewUsers', views.ViewUsers, name="ViewUsers"), 
	       path('ViewOccupancy', views.ViewOccupancy, name="ViewOccupancy"), 
	       path('BookSlot', views.BookSlot, name="BookSlot"), 
	       path('BookSlotAction', views.BookSlotAction, name="BookSlotAction"), 
	       path('ViewHistory', views.ViewHistory, name="ViewHistory"),
	       path('ReleaseSlot', views.ReleaseSlot, name="ReleaseSlot"), 
	       path('ReleaseSlotAction', views.ReleaseSlotAction, name="ReleaseSlotAction"), 
]