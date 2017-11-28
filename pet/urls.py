from django.conf.urls import url, include
from django.views.generic import TemplateView
from . import views

app_name = 'pet'

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='index.html'), name='index'),
    url(r'^pets/$', views.pet_list, name='pet list'),
    url(r'^pets/findpet/$',views.find_pet,name='find pet'),
    url(r'^pet/detail/(?P<pet_code>.*)/$', views.pet_detail, name='pet detail'),
    url(r'^pet/detail_like/(?P<pet_code>.*)/(?P<im_id>[0-9]+)/$',
        views.LikeImage.as_view(), name='like image'),
    url(r'^pet/api/detail_like/(?P<pet_code>.*)/(?P<im_id>[0-9]+)/$',
        views.LikeImageAPI.as_view(), name='like image api'),
    url(r'^pet/(?P<pet_id>[0-9]+)/followed/$', views.Pet_follow.as_view(), name='pet follow'),
    url(r'^pet/(?P<pet_id>[0-9]+)/unfollowed/$', views.Pet_unfollow.as_view(), name='pet unfollow'),
    url(r'^purchases/mypurchases/(?P<pet_type>.*)/(?P<filter_type>.*)/$',views.my_purchases, name='my purchases'),
    url(r'^purchases/detail/(?P<purchase_id>.*)/$', views.purchase_detail, name='purchase detail'),
    url(r'^purchases/(?P<purchase_id>[0-9]+)/followed/$', views.purchase_follow, name='purchase follow'),
    url(r'^purchases/(?P<purchase_id>[0-9]+)/unfollowed/$', views.purchase_unfollow, name='purchase unfollow'),
    url(r'^purchases/add/$', views.add_purchase, name='add purchase'),
    url(r'^purchases/(?P<pet_type>.*)/(?P<filter_type>.*)/$',
        views.purchases, name='pet purchases'),
    url(r'^custom_purchases/(?P<pet_code>.*)/(?P<filter_type>.*)/$',
        views.pet_custom_purchases, name='pet custom purchases'),
    url(r'^other_users_purchases/(?P<user_id>[0-9]+)/(?P<pet_type>.*)/(?P<filter_type>.*)/$',
        views.other_users_purchases, name='user purchases'),
    url(r'^profile/edit/(?P<purchase_id>[0-9]+)/$',
        views.edit_purchase, name='edit purchase'),
    url(r'^profile/(?P<user_id>[0-9]+)/$', views.user_profile, name='user profile'),
    url(r'^profile/$', TemplateView.as_view(template_name='my_profile.html'), name='current user profile'),
    url(r'^profile/edit/$', views.edit_profile, name='edit profile'),
    url(r'^profile/(?P<user_id>[0-9]+)/followed/$', views.user_follow, name='user follow'),
    url(r'^profile/(?P<user_id>[0-9]+)/unfollowed/$', views.user_unfollow, name='user unfollow'),
    url(r'^users/(?P<filter_type>.*)/$',
        views.user_list, name='top users'),
]
