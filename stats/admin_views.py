
from django.template import RequestContext
from django.shortcuts import render_to_response
from django.contrib.admin.views.decorators import staff_member_required
from tuhlaajapojat.stats.models import *
from django.contrib import admin

#from tuhlaajapojat.stats.forms import *

from tuhlaajapojat.stats.admin import MatchAdmin

    ## def add_view(self, request, form_url='', extra_context=None):

def add_match(request, season_id):
    match_admin = MatchAdmin(Match,admin.site)
    return match_admin.add_view(request, season_id)

## def season(self, request, context, add=False, change=False, form_url='', obj=None):
##         opts = self.model._meta
##         app_label = opts.app_label
##         ordered_objects = opts.get_ordered_objects()
##         context.update({
##             'add': add,
##             'change': change,
##             'has_add_permission': self.has_add_permission(request),
##             'has_change_permission': self.has_change_permission(request, obj),
##             'has_delete_permission': self.has_delete_permission(request, obj),
##             'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
##             'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
##             'ordered_objects': ordered_objects,
##             'form_url': mark_safe(form_url),
##             'opts': opts,
##             'content_type_id': ContentType.objects.get_for_model(self.model).id,
##             'save_as': self.save_as,
##             'save_on_top': self.save_on_top,
##             'root_path': self.admin_site.root_path,
##         })
##         context_instance = template.RequestContext(request, current_app=self.admin_site.name)
##         return render_to_response(self.change_form_template or [
##             "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
##             "admin/%s/change_form.html" % app_label,
##             "admin/change_form.html"
##         ], context, context_instance=context_instance)

## (request, season_id):
##     form = MatchForm()
##     return render_to_response(
##         "admin/stats/season_change_form.html",
##         {'cl' : Season.objects.all(),
##          'season_list' : Season.objects.all(),
##          'form' : form,},
##         RequestContext(request, {}),
##     )
## season = staff_member_required(season)
